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

    # ── 2. SCENARIO LIFECYCLE ──────────────────────────────────────────
    from app.simulation.scenario_manager import run_scenario_lifecycle
    scenario_directives, scenario_injected_events, scenario_infos = await run_scenario_lifecycle(
        gq, world_day, all_npcs, locations, recent_event_descs,
    )

    # ── 3. WORLD EVENTS ────────────────────────────────────────────────
    event_agent.load_event_pool(settings.worlds_dir / "medieval_village")
    generated_events = await event_agent.generate(
        world_day=world_day,
        locations=[dict(l) for l in locations],
        recent_events=recent_event_descs,
        tensions=[],
    )
    # Add scenario-injected events
    generated_events.extend(scenario_injected_events)

    event_results = await process_events(gq, generated_events, world_day)

    # Refresh event descriptions for NPC context
    all_event_descs = recent_event_descs + [e["description"] for e in generated_events]

    # ── 4. NPC DECISIONS ───────────────────────────────────────────────
    # At night, some NPCs sleep
    if current_day_phase in ("night", "dawn"):
        active_for_decisions = [n for n in active_npcs if _rng.random() > 0.4]  # 60% sleep
    else:
        active_for_decisions = active_npcs

    npc_actions = []
    decision_tasks = []  # (npc, ctx) pairs

    for npc in active_for_decisions:
        try:
            location = await gq.get_npc_location(npc["id"])
            if not location:
                continue

            nearby = await gq.get_npcs_at_location(location["id"])
            nearby = [n for n in nearby if n["id"] != npc["id"]]

            # Get connected locations so NPC knows where they can move
            connected_locs = await gq.get_connected_locations(location["id"])

            relationships_raw = await gq.get_relationships(npc["id"])
            relationships = [
                NPCRelationship(npc_id=r["id"], name=r["name"], sentiment=r["sentiment"], reason=r["reason"])
                for r in relationships_raw
            ]

            memories = get_recent_memories(npc["id"], limit=5)

            # Resolve archetype
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

            # Equipment summary
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

            current_phase = current_day_phase

            # Inject scenario directive into scene context
            scene_context = scenario_directives.get(npc["id"])

            # Enrich nearby NPCs with relationship info and HP
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
                current_phase=current_phase,
                archetype_name=archetype_name,
                archetype_decision_bias=archetype_decision_bias,
                archetype_group_role=archetype_group_role,
                active_scene_context=scene_context,
                equipment_summary=equipment_summary,
                combat_capability=combat_capability,
                gold=npc_gold,
                nearby_locations=[loc["name"] for loc in connected_locs],
            )

            decision_tasks.append((npc, ctx))
        except Exception as e:
            log.error("npc_context_failed", npc=npc["name"], error=str(e))

    # Run all decisions in parallel
    async def _decide_and_apply(npc_data, context):
        try:
            decision = await npc_agent.decide(context)
            return (npc_data, decision)
        except Exception as e:
            log.error("npc_decide_failed", npc=npc_data["name"], error=str(e))
            return None

    results = await asyncio.gather(
        *[_decide_and_apply(npc, ctx) for npc, ctx in decision_tasks],
        return_exceptions=True,
    )

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
        await _apply_decision(gq, npc, decision, locations, world_day)
        add_memory(npc["id"], f"Day {world_day}: I decided to {decision.action}" +
                   (f" targeting {decision.target}" if decision.target else ""), day=world_day)
        mood = npc["mood"]
        if decision.mood_change == "better":
            mood = "content" if mood in ("angry", "fearful") else "excited"
        elif decision.mood_change == "worse":
            mood = "angry" if mood in ("content", "excited") else "fearful"
        if mood != npc["mood"]:
            await gq.update_npc(npc["id"], {"mood": mood})

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

    # ── 6. CLEANUP ─────────────────────────────────────────────────────
    await propagate_rumors(gq, active_npcs, world_day)

    from app.simulation.events import summarize_old_memories
    for npc in active_npcs:
        count = get_memory_count(npc["id"])
        if count > settings.memory_summarize_threshold:
            await summarize_old_memories(npc["id"])

    result = {
        "day": world_day,
        "events": [{"description": e["description"], "type": e.get("type", "event")} for e in generated_events],
        "npc_actions": npc_actions,
        "interactions": interactions,
        "active_scenarios": scenario_infos,
    }

    log.info("tick_done", day=world_day, events=len(generated_events),
             actions=len(npc_actions), scenarios=len(scenario_infos))
    return result


async def _apply_decision(gq: GraphQueries, npc: dict, decision, locations: list[dict], world_day: int) -> None:
    """Apply an NPC's decision to the world graph — FULL execution of all action types."""
    import random
    from app.models.memory import add_memory

    action = decision.action
    target_name = decision.target

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
                await _resolve_npc_combat(gq, npc, target, action, world_day)

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

    # Store consequence as NPC activity
    if decision.consequence:
        await gq.update_npc(npc["id"], {"current_activity": decision.consequence[:100]})


async def _resolve_npc_combat(gq: GraphQueries, attacker: dict, defender: dict, action: str, world_day: int) -> dict:
    """Resolve autonomous NPC-to-NPC combat using D&D-style rules."""
    import random
    from app.models.memory import add_memory

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
        else:
            # Caught! Turns into fight
            add_memory(defender["id"], f"Day {world_day}: Caught {attacker['name']} trying to rob me!", day=world_day, importance=0.9)
            await gq.set_relationship(defender["id"], attacker["id"], -0.9, "caught stealing")
            await gq.update_npc(defender["id"], {"mood": "angry"})
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


