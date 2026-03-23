"""World tick system — advances the simulation by one game day."""

from __future__ import annotations

import asyncio

from celery import Celery

from app.config import settings
from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("ticker")

celery_app = Celery("living_world", broker=settings.redis_url)
celery_app.conf.beat_schedule = {
    "world-tick": {
        "task": "app.simulation.ticker.celery_world_tick",
        "schedule": settings.tick_interval_seconds,
    },
}


@celery_app.task(name="app.simulation.ticker.celery_world_tick")
def celery_world_tick():
    """Celery task wrapper for the async world tick."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(run_world_tick())
        log.info("tick_completed", day=result["day"])
    finally:
        loop.close()


async def run_world_tick() -> dict:
    """Execute one world tick (= 1 game day)."""
    import random as _rng

    from app.agents.event_agent import event_agent
    from app.agents.npc_agent import npc_agent
    from app.graph.connection import get_driver
    from app.models.memory import add_memory, get_memory_count, get_recent_memories, init_memory_db
    from app.models.npc import NPCContext, NPCRelationship
    from app.simulation.events import process_events
    from app.simulation.rumors import propagate_rumors
    from app.simulation.scheduler import get_active_npcs

    init_memory_db()
    gq = GraphQueries(get_driver())

    world_day = await gq.increment_world_day()

    day_phases = ["dawn", "morning", "afternoon", "evening", "night"]
    current_day_phase = day_phases[world_day % len(day_phases)]

    log.info("tick_starting", day=world_day)

    # 1. Get active NPCs & world state
    all_npcs = await gq.get_all_npcs()
    active_npcs = await get_active_npcs(gq, all_npcs, "player-1")
    locations = await gq.get_all_locations()
    recent_events_raw = await gq.get_recent_events(max(1, world_day - 3))
    recent_event_descs = [e["description"] for e in recent_events_raw]

    # ── 1.5. ENVIRONMENT ────────────────────────────────────────────
    from app.simulation.environment import environment_engine
    env_result = await environment_engine.tick(gq, world_day)
    env_events, current_season, current_weather = env_result
    # Refresh locations after env updates
    locations = await gq.get_all_locations()

    # ── 1.6. ECONOMY ────────────────────────────────────────────────
    from app.simulation.economy import economy_engine
    economy_events = await economy_engine.tick(gq, world_day, all_npcs)

    # ── 2. SCENARIO LIFECYCLE (now uses Narrator for tension-based arcs) ──
    from app.simulation.scenario_manager import run_scenario_lifecycle
    scenario_directives, scenario_injected_events, scenario_infos = await run_scenario_lifecycle(
        gq, world_day, all_npcs, locations, recent_event_descs,
    )

    # ── 2.5. FACTION STRATEGIES ──────────────────────────────────────
    from app.agents.faction_agent import faction_agent
    faction_directives: dict[str, str] = {}
    try:
        all_factions = await gq.get_all_factions()
        for faction in all_factions:
            members = await gq.get_faction_members(faction["id"])
            if not members:
                continue
            other_factions = [f for f in all_factions if f["id"] != faction["id"]]
            strategy_result = await faction_agent.strategize(
                faction, members, other_factions,
            )
            # Update faction strategy in graph
            await gq.update_faction(faction["id"], {"strategy": strategy_result["strategy"]})
            # Merge faction directives into NPC directives
            faction_directives.update(strategy_result.get("directives", {}))
    except Exception as e:
        log.error("faction_strategy_failed", error=str(e))

    # ── 3. WORLD EVENTS ────────────────────────────────────────────────
    event_agent.load_event_pool(settings.worlds_dir / "medieval_village")
    generated_events = await event_agent.generate(
        world_day=world_day,
        locations=[dict(l) for l in locations],
        recent_events=recent_event_descs,
        tensions=[],
    )
    # Add scenario-injected events + environment events + economy events
    generated_events.extend(scenario_injected_events)
    generated_events.extend(env_events)
    generated_events.extend(economy_events)

    event_results = await process_events(gq, generated_events, world_day)

    # Refresh event descriptions for NPC context
    all_event_descs = recent_event_descs + [e["description"] for e in generated_events]

    # ── 4. NPC DECISIONS (with priority-based scaling) ─────────────────
    # At night, some NPCs sleep
    if current_day_phase in ("night", "dawn"):
        active_for_decisions = [n for n in active_npcs if _rng.random() > 0.4]  # 60% sleep
    else:
        active_for_decisions = active_npcs

    npc_actions = []

    # ── Priority classification ──
    # High: NPC in active scenario or has scene_context
    # Low: everyone else → gets deterministic decision without LLM
    scenario_npc_ids = set()
    for s in scenario_infos:
        scenario_npc_ids.update(s.get("involved_npc_ids", []))

    high_priority = []
    low_priority = []
    for npc in active_for_decisions:
        if npc["id"] in scenario_npc_ids or npc["id"] in scenario_directives or npc["id"] in faction_directives:
            high_priority.append(npc)
        else:
            low_priority.append(npc)

    # Ensure we use LLM for at least priority_llm_ratio of NPCs
    llm_budget = max(len(high_priority), int(len(active_for_decisions) * settings.priority_llm_ratio))
    extra_llm_slots = llm_budget - len(high_priority)
    if extra_llm_slots > 0 and low_priority:
        _rng.shuffle(low_priority)
        promoted = low_priority[:extra_llm_slots]
        remaining_low = low_priority[extra_llm_slots:]
        high_priority.extend(promoted)
        low_priority = remaining_low

    # ── Deterministic decisions for low-priority NPCs (schedule engine, no LLM) ──
    from app.simulation.schedule import schedule_engine
    for npc in low_priority:
        sched = schedule_engine.get_activity(npc, current_day_phase, world_day)
        action = sched["action"]
        activity_desc = sched["activity_desc"]
        npc_actions.append({
            "npc_id": npc["id"],
            "npc_name": npc["name"],
            "action": action,
            "target": None,
            "dialogue": None,
            "reasoning": "daily routine",
        })
        await gq.update_npc(npc["id"], {"current_activity": activity_desc})
        add_memory(npc["id"], f"Day {world_day}: Spent the day {activity_desc}.", day=world_day)

    # ── LLM decisions for high-priority NPCs (in batches) ──
    decision_tasks = []

    for npc in high_priority:
        try:
            location = await gq.get_npc_location(npc["id"])
            if not location:
                continue

            nearby = await gq.get_npcs_at_location(location["id"])
            nearby = [n for n in nearby if n["id"] != npc["id"]]

            connected_locs = await gq.get_connected_locations(location["id"])

            relationships_raw = await gq.get_relationships(npc["id"])
            relationships = [
                NPCRelationship(npc_id=r["id"], name=r["name"], sentiment=r["sentiment"], reason=r["reason"])
                for r in relationships_raw
            ]

            memories = get_recent_memories(npc["id"], limit=5)

            archetype_name = None
            archetype_decision_bias = None
            archetype_group_role = None
            if npc.get("archetype"):
                from app.models.archetypes import get_archetype
                arch = get_archetype(npc["archetype"])
                if arch:
                    archetype_name = arch.name
                    archetype_decision_bias = arch.decision_bias
                    archetype_group_role = arch.group_role

            equipment_summary = None
            combat_capability = None
            npc_gold = npc.get("gold", 0)
            equipment_ids = npc.get("equipment_ids", [])
            if equipment_ids:
                from app.dnd.equipment import get_weapon, get_armor
                parts = []
                for eid in equipment_ids:
                    w = get_weapon(eid)
                    if w:
                        parts.append(f"{w.name} ({w.damage_dice} {w.damage_type})")
                    a = get_armor(eid)
                    if a:
                        parts.append(f"{a.name} (AC {a.ac_base})")
                if parts:
                    equipment_summary = "Equipped: " + ", ".join(parts)
                npc_level = npc.get("level", 1)
                npc_class = npc.get("class_id", npc["occupation"])
                combat_capability = f"Level {npc_level} {npc_class}, HP ~{npc.get('max_hp', 10)}"

            scene_context = scenario_directives.get(npc["id"])
            # Merge faction directive into scene context
            fac_directive = faction_directives.get(npc["id"])
            if fac_directive:
                if scene_context:
                    scene_context = f"{scene_context} | FACTION ORDER: {fac_directive}"
                else:
                    scene_context = f"FACTION ORDER: {fac_directive}"

            enriched_nearby = []
            for n in nearby:
                nd = dict(n)
                rel = next((r for r in relationships_raw if r["id"] == n["id"]), None)
                if rel:
                    nd["sentiment"] = rel["sentiment"]
                    nd["reason"] = rel.get("reason", "")
                enriched_nearby.append(nd)

            ctx = NPCContext(
                npc_id=npc["id"],
                name=npc["name"],
                personality=npc["personality"],
                backstory=npc.get("backstory", ""),
                biography=npc.get("biography"),
                goals=npc.get("goals", []),
                mood=npc["mood"],
                occupation=npc["occupation"],
                age=npc["age"],
                location_name=location["name"],
                location_description=location["description"],
                nearby_npcs=enriched_nearby,
                relationships=relationships,
                recent_memories=memories,
                recent_events=all_event_descs[-5:],
                world_day=world_day,
                current_phase=current_day_phase,
                archetype_name=archetype_name,
                archetype_decision_bias=archetype_decision_bias,
                archetype_group_role=archetype_group_role,
                active_scene_context=scene_context,
                equipment_summary=equipment_summary,
                combat_capability=combat_capability,
                gold=npc_gold,
                nearby_locations=[loc["name"] for loc in connected_locs],
                # Evolution baselines
                trust_baseline=npc.get("trust_baseline", 0.0) or 0.0,
                mood_baseline=npc.get("mood_baseline", 0.0) or 0.0,
                aggression_baseline=npc.get("aggression_baseline", 0.0) or 0.0,
                confidence_baseline=npc.get("confidence_baseline", 0.0) or 0.0,
                # Environment
                season=current_season,
                weather=current_weather,
                location_condition=location.get("condition"),
                # Economy
                local_shortages=economy_engine.get_shortages(location),
                # Faction
                faction_directive=faction_directives.get(npc["id"]),
            )

            decision_tasks.append((npc, ctx))
        except Exception as e:
            log.error("npc_context_failed", npc=npc["name"], error=str(e))

    # Process LLM decisions in batches to avoid overwhelming Ollama
    batch_size = settings.llm_batch_size

    async def _decide_and_apply(npc_data, context):
        try:
            decision = await npc_agent.decide(context)
            return (npc_data, decision)
        except Exception as e:
            log.error("npc_decide_failed", npc=npc_data["name"], error=str(e))
            return None

    for batch_start in range(0, len(decision_tasks), batch_size):
        batch = decision_tasks[batch_start : batch_start + batch_size]
        results = await asyncio.gather(
            *[_decide_and_apply(npc, ctx) for npc, ctx in batch],
            return_exceptions=True,
        )

        from app.simulation.evolution import evolution_engine

        for res in results:
            if res is None or isinstance(res, Exception):
                continue
            npc, decision = res
            npc_actions.append({
                "npc_id": npc["id"],
                "npc_name": npc["name"],
                "action": decision.action,
                "target": decision.target,
                "dialogue": decision.dialogue,
                "reasoning": decision.reasoning,
            })
            combat_result = await _apply_decision(gq, npc, decision, locations, world_day)
            add_memory(npc["id"], f"Day {world_day}: I decided to {decision.action}" +
                       (f" targeting {decision.target}" if decision.target else ""), day=world_day)
            mood = npc["mood"]
            if decision.mood_change == "better":
                mood = "content" if mood in ("angry", "fearful") else "excited"
            elif decision.mood_change == "worse":
                mood = "angry" if mood in ("content", "excited") else "fearful"
            if mood != npc["mood"]:
                await gq.update_npc(npc["id"], {"mood": mood})

            # ── Evolution: shift baselines based on action outcome ──
            event_types = evolution_engine.classify_action_outcome(
                decision.action, decision.target, combat_result,
            )
            if event_types:
                await evolution_engine.apply_shifts(gq, npc["id"], npc, event_types)

    # ── 5. NPC INTERACTIONS (with consequences) ────────────────────────
    # Build scenario context string for interactions
    scenario_context_str = None
    if scenario_infos:
        parts = [f"{s['title']}: {s['narrative_update'] or s['description']}" for s in scenario_infos]
        scenario_context_str = " | ".join(parts)

    from app.simulation.interaction_resolver import resolve_interactions
    interactions = await resolve_interactions(
        gq, npc_agent, active_npcs, world_day, scenario_context_str,
    )

    # ── 6. CLEANUP & MEMORY ──────────────────────────────────────────
    await propagate_rumors(gq, active_npcs, world_day)

    from app.agents.memory_architect import memory_architect
    from app.models.memory import purge_old_summarized
    from app.simulation.events import summarize_old_memories
    for npc in active_npcs:
        count = get_memory_count(npc["id"])
        if count > settings.memory_summarize_threshold:
            # Use Memory Architect for smart consolidation
            await memory_architect.consolidate_npc(npc["id"], npc["name"])
        # Decay old memories (importance fades over time)
        memory_architect.decay_memories(npc["id"], world_day)
        # Defragment: remove oldest summarized records if too many accumulated
        purge_old_summarized(npc["id"], keep=50)

    # Build collective location memory every 5 days
    if world_day % 5 == 0:
        for loc in locations:
            try:
                await memory_architect.build_location_memory(gq, loc["id"], loc["name"], world_day)
            except Exception as e:
                log.error("location_memory_failed", location=loc["name"], error=str(e))

    result = {
        "day": world_day,
        "season": current_season,
        "weather": current_weather,
        "events": [{"description": e["description"], "type": e.get("type", "event")} for e in generated_events],
        "npc_actions": npc_actions,
        "interactions": interactions,
        "active_scenarios": scenario_infos,
    }

    log.info("tick_done", day=world_day, season=current_season, weather=current_weather,
             events=len(generated_events), actions=len(npc_actions), scenarios=len(scenario_infos))
    return result


async def _apply_decision(gq: GraphQueries, npc: dict, decision, locations: list[dict], world_day: int) -> dict | None:
    """Apply an NPC's decision to the world graph — FULL execution of all action types.

    Returns combat_result dict if a fight/rob occurred, else None.
    """
    import random
    from app.models.memory import add_memory

    action = decision.action
    target_name = decision.target
    combat_result = None

    # ── MOVE ──
    if action == "move" and target_name:
        for loc in locations:
            if target_name.lower() in loc["name"].lower():
                await gq.set_npc_location(npc["id"], loc["id"])
                break

    # ── WORK / CRAFT ── (update activity, possible gold gain)
    elif action in ("work", "craft"):
        gold_earned = random.randint(1, 5)
        await gq.update_npc(npc["id"], {
            "current_activity": f"working as {npc['occupation']}",
            "gold": npc.get("gold", 0) + gold_earned,
        })

    # ── TRADE ── (transfer gold between NPCs)
    elif action == "trade" and target_name:
        location = await gq.get_npc_location(npc["id"])
        if location:
            nearby = await gq.get_npcs_at_location(location["id"])
            target = next((n for n in nearby if target_name.lower() in n["name"].lower()), None)
            if target:
                trade_amount = random.randint(1, min(5, npc.get("gold", 0) or 1))
                await gq.transfer_gold(npc["id"], target["id"], trade_amount)
                add_memory(target["id"], f"Day {world_day}: Traded with {npc['name']}.", day=world_day)

    # ── FIGHT / ROB ── (NPC autonomous combat!)
    elif action in ("fight", "rob") and target_name:
        location = await gq.get_npc_location(npc["id"])
        if location:
            nearby = await gq.get_npcs_at_location(location["id"])
            target = next((n for n in nearby if target_name.lower() in n["name"].lower() and n["id"] != npc["id"]), None)
            if target and target.get("alive", True):
                combat_result = await _resolve_npc_combat(gq, npc, target, action, world_day)

    # ── REST ── (heal HP)
    elif action == "rest":
        max_hp = npc.get("max_hp", 10)
        current_hp = npc.get("current_hp", max_hp)
        heal = max(1, max_hp // 4)  # Heal 25% per rest
        if current_hp < max_hp:
            await gq.heal_npc(npc["id"], heal)
        await gq.update_npc(npc["id"], {"current_activity": "resting"})

    # ── PATROL / SNEAK ── (movement variant)
    elif action in ("patrol", "sneak"):
        await gq.update_npc(npc["id"], {
            "current_activity": "patrolling" if action == "patrol" else "sneaking",
        })

    # ── DEFEND ── (protect someone)
    elif action == "defend" and target_name:
        await gq.update_npc(npc["id"], {"current_activity": f"defending {target_name}"})

    # ── TRAIN ── (small stat improvement narrative)
    elif action == "train":
        await gq.update_npc(npc["id"], {"current_activity": "training"})

    # ── PRAY / FORAGE / INVESTIGATE / GOSSIP / HELP / THREATEN ──
    elif action in ("pray", "forage", "investigate", "gossip", "help", "threaten", "talk"):
        activity_map = {
            "pray": "praying at the chapel",
            "forage": "foraging in the wilds",
            "investigate": f"investigating {target_name or 'something'}",
            "gossip": f"gossiping about {target_name or 'the village'}",
            "help": f"helping {target_name or 'someone'}",
            "threaten": f"threatening {target_name or 'someone'}",
            "talk": f"talking with {target_name or 'someone'}",
        }
        await gq.update_npc(npc["id"], {"current_activity": activity_map.get(action, action)})

        # Threaten changes relationships
        if action == "threaten" and target_name:
            location = await gq.get_npc_location(npc["id"])
            if location:
                nearby = await gq.get_npcs_at_location(location["id"])
                target = next((n for n in nearby if target_name.lower() in n["name"].lower()), None)
                if target:
                    await gq.set_relationship(target["id"], npc["id"], -0.3, "was threatened")
                    add_memory(target["id"], f"Day {world_day}: {npc['name']} threatened me!", day=world_day, importance=0.9)
                    # Evolution: victim's trust and confidence drop
                    from app.simulation.evolution import evolution_engine as _evo
                    await _evo.apply_shifts(gq, target["id"], target, ["was_threatened"])

    # Store consequence as NPC activity
    if decision.consequence:
        await gq.update_npc(npc["id"], {"current_activity": decision.consequence[:100]})

    return combat_result


async def _resolve_npc_combat(gq: GraphQueries, attacker: dict, defender: dict, action: str, world_day: int) -> dict:
    """Resolve autonomous NPC-to-NPC combat using D&D-style rules."""
    import random
    from app.models.memory import add_memory
    from app.simulation.evolution import evolution_engine

    atk_level = attacker.get("level", 1)
    def_level = defender.get("level", 1)
    atk_hp = attacker.get("current_hp", attacker.get("max_hp", 10))
    def_hp = defender.get("current_hp", defender.get("max_hp", 10))

    # Simple D&D-ish combat: roll d20 + level vs AC
    atk_roll = random.randint(1, 20) + atk_level
    def_ac = 10 + def_level  # simplified AC

    result = {"attacker_won": False, "defender_died": False, "attacker_died": False}

    if action == "rob":
        # Robbery: stealth check — if attacker level > defender, 70% success
        success_chance = 0.5 + (atk_level - def_level) * 0.05
        if random.random() < success_chance:
            stolen = random.randint(1, max(1, defender.get("gold", 0)))
            await gq.transfer_gold(defender["id"], attacker["id"], stolen)
            add_memory(attacker["id"], f"Day {world_day}: Successfully robbed {defender['name']} of {stolen} gold.", day=world_day, importance=0.9)
            add_memory(defender["id"], f"Day {world_day}: Was robbed! Lost {stolen} gold.", day=world_day, importance=0.9)
            await gq.set_relationship(defender["id"], attacker["id"], -0.8, "robbed me")
            await gq.update_npc(defender["id"], {"mood": "angry"})
            # Evolution: victim's trust drops
            await evolution_engine.apply_shifts(gq, defender["id"], defender, ["was_robbed"])
        else:
            # Caught! Turns into fight
            add_memory(defender["id"], f"Day {world_day}: Caught {attacker['name']} trying to rob me!", day=world_day, importance=0.9)
            await gq.set_relationship(defender["id"], attacker["id"], -0.9, "caught stealing")
            await gq.update_npc(defender["id"], {"mood": "angry"})
            await evolution_engine.apply_shifts(gq, defender["id"], defender, ["caught_thief"])
        return result

    # ── ACTUAL COMBAT ──
    # Simulate 3 rounds of combat
    a_hp = atk_hp
    d_hp = def_hp
    for _ in range(3):
        # Attacker strikes
        roll = random.randint(1, 20) + atk_level
        if roll >= def_ac:
            dmg = random.randint(1, 8) + max(0, atk_level - 1)
            d_hp -= dmg
        if d_hp <= 0:
            break

        # Defender strikes back
        atk_ac = 10 + atk_level
        roll = random.randint(1, 20) + def_level
        if roll >= atk_ac:
            dmg = random.randint(1, 8) + max(0, def_level - 1)
            a_hp -= dmg
        if a_hp <= 0:
            break

    # Apply results
    if d_hp <= 0:
        # Defender killed
        await gq.kill_npc(defender["id"])
        result["defender_died"] = True
        result["attacker_won"] = True
        add_memory(attacker["id"], f"Day {world_day}: Killed {defender['name']} in combat.", day=world_day, importance=1.0)
        # Notify all NPCs at location
        location = await gq.get_npc_location(attacker["id"])
        if location:
            witnesses = await gq.get_npcs_at_location(location["id"])
            for w in witnesses:
                if w["id"] not in (attacker["id"], defender["id"]):
                    add_memory(w["id"], f"Day {world_day}: Witnessed {attacker['name']} kill {defender['name']}!", day=world_day, importance=1.0)
                    await gq.set_relationship(w["id"], attacker["id"],
                                              -0.5, f"killed {defender['name']}")
                    await gq.update_npc(w["id"], {"mood": "fearful"})
                    # Evolution: witnesses are traumatized
                    await evolution_engine.apply_shifts(gq, w["id"], w, ["witnessed_murder"])
        log.info("npc_killed", attacker=attacker["name"], defender=defender["name"])
    elif a_hp <= 0:
        # Attacker killed
        await gq.kill_npc(attacker["id"])
        result["attacker_died"] = True
        add_memory(defender["id"], f"Day {world_day}: Killed {attacker['name']} in self-defense.", day=world_day, importance=1.0)
        log.info("npc_killed", attacker=defender["name"], defender=attacker["name"])
    else:
        # Both survived — update HP
        await gq.update_npc(attacker["id"], {"current_hp": max(1, a_hp), "mood": "angry"})
        await gq.update_npc(defender["id"], {"current_hp": max(1, d_hp), "mood": "angry"})
        add_memory(attacker["id"], f"Day {world_day}: Fought with {defender['name']}, both survived.", day=world_day, importance=0.8)
        add_memory(defender["id"], f"Day {world_day}: Fought with {attacker['name']}, both survived.", day=world_day, importance=0.8)
        await gq.set_relationship(defender["id"], attacker["id"], -0.6, "attacked me")

    return result


