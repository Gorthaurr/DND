"""Core NPC evolution engine — deterministic, no LLM calls."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.evolution import (
    NPCEvolutionState, TraitScale, Fear, Goal, GoalStatus,
    RelationshipTag, EvolutionLogEntry, to_big_five_string,
)
from app.simulation.evolution_rules import (
    TriggerType, TRAIT_SHIFT_TABLE, FEAR_TRIGGERS, GOAL_TEMPLATES,
    ARCHETYPE_PROFILES, ARCHETYPE_DRIFT_THRESHOLD, ARCHETYPE_DRIFT_DAYS_REQUIRED,
)
from app.simulation.evolution_migration import migrate_npc_to_evolution, _cosine_similarity
from app.simulation.nemesis import (
    check_nemesis_trigger, record_nemesis_combat, escalate_nemesis,
    apply_nemesis_adaptations,
)


@dataclass
class EvolutionTrigger:
    type: TriggerType
    magnitude: float = 0.5      # 0.0 to 1.0
    source_npc_id: str | None = None
    source_npc_name: str | None = None
    context: str = ""


# ── Event classification ──

def classify_events(
    npc: dict,
    decision: dict | None,
    interactions: list[dict],
    world_day: int,
) -> list[EvolutionTrigger]:
    """Scan tick outputs for evolution triggers. Pure deterministic logic."""
    triggers: list[EvolutionTrigger] = []
    npc_id = npc.get("id", "")
    current_hp = npc.get("current_hp", npc.get("max_hp", 10))
    max_hp = npc.get("max_hp", 10)

    # Near death: HP dropped below 25%
    if max_hp > 0 and current_hp <= max_hp * 0.25 and current_hp > 0:
        triggers.append(EvolutionTrigger(
            type=TriggerType.NEAR_DEATH, magnitude=1.0 - (current_hp / max_hp),
            context=decision.get("consequence", "combat") if decision else "combat",
        ))

    if decision:
        action = decision.get("action", "")
        target = decision.get("target", "")
        consequence = decision.get("consequence", "")

        if action == "fight" and "won" in consequence.lower():
            triggers.append(EvolutionTrigger(
                type=TriggerType.COMBAT_VICTORY, magnitude=0.5,
                source_npc_name=target, context=consequence,
            ))
        elif action == "fight" and ("lost" in consequence.lower() or "defeated" in consequence.lower()):
            triggers.append(EvolutionTrigger(
                type=TriggerType.COMBAT_DEFEAT, magnitude=0.6, context=consequence,
            ))
        elif action == "help":
            triggers.append(EvolutionTrigger(
                type=TriggerType.HELPED_SOMEONE, magnitude=0.3,
                source_npc_name=target,
            ))
        elif action == "threaten":
            triggers.append(EvolutionTrigger(
                type=TriggerType.SOCIAL_REJECTION, magnitude=0.2, context=consequence or "",
            ))
        elif action == "rob":
            triggers.append(EvolutionTrigger(
                type=TriggerType.ROBBERY_SUCCESS, magnitude=0.4,
                source_npc_name=target,
            ))

    for inter in interactions:
        action = inter.get("action", "")
        other_id = inter.get("other_npc_id", "")
        other_name = inter.get("other_npc_name", "")
        sentiment_change = inter.get("sentiment_change", 0)

        # Betrayal: sentiment dropped significantly from a trusted NPC
        if sentiment_change < -0.4:
            triggers.append(EvolutionTrigger(
                type=TriggerType.BETRAYED, magnitude=min(1.0, abs(sentiment_change)),
                source_npc_id=other_id, source_npc_name=other_name,
            ))
        elif sentiment_change > 0.3 and action == "help":
            triggers.append(EvolutionTrigger(
                type=TriggerType.RECEIVED_HELP, magnitude=0.3,
                source_npc_id=other_id, source_npc_name=other_name,
            ))

        if action == "threaten" and inter.get("target_id") == npc_id:
            triggers.append(EvolutionTrigger(
                type=TriggerType.THREAT_RECEIVED, magnitude=0.3,
                source_npc_id=other_id, source_npc_name=other_name,
            ))

        if action == "rob" and inter.get("target_id") == npc_id:
            triggers.append(EvolutionTrigger(
                type=TriggerType.ROBBERY_VICTIM, magnitude=0.5,
                source_npc_id=other_id, source_npc_name=other_name,
            ))

    # ── Nemesis triggers ──
    # Check if NPC has nemesis and interacted with them
    evo_json = npc.get("evolution_state_json")
    if evo_json:
        try:
            evo = NPCEvolutionState.model_validate_json(evo_json)
        except Exception:
            evo = None
        if evo and evo.nemesis:
            nem_id = evo.nemesis.target_id
            # Check if fought nemesis this tick
            if decision and decision.get("action") == "fight":
                target_name = (decision.get("target") or "").lower()
                nem_name = evo.nemesis.target_name.lower()
                if nem_name and nem_name in target_name:
                    consequence = (decision.get("consequence") or "").lower()
                    if "won" in consequence:
                        triggers.append(EvolutionTrigger(
                            type=TriggerType.NEMESIS_VICTORY, magnitude=0.8,
                            source_npc_id=nem_id,
                            source_npc_name=evo.nemesis.target_name,
                            context=decision.get("consequence", ""),
                        ))
                    elif "lost" in consequence or "defeated" in consequence:
                        triggers.append(EvolutionTrigger(
                            type=TriggerType.NEMESIS_DEFEAT, magnitude=0.9,
                            source_npc_id=nem_id,
                            source_npc_name=evo.nemesis.target_name,
                            context=decision.get("consequence", ""),
                        ))

            # Check co-location with nemesis (encounter)
            npc_location = npc.get("location_id", "")
            nemesis_location = npc.get("_nemesis_location", "")  # injected by ticker
            if npc_location and npc_location == nemesis_location:
                triggers.append(EvolutionTrigger(
                    type=TriggerType.NEMESIS_ENCOUNTER, magnitude=0.4,
                    source_npc_id=nem_id,
                    source_npc_name=evo.nemesis.target_name,
                ))

    return triggers


# ── Trait shifts ──

def apply_trait_shifts(state: NPCEvolutionState, triggers: list[EvolutionTrigger], day: int) -> list[EvolutionLogEntry]:
    log: list[EvolutionLogEntry] = []
    for trigger in triggers:
        deltas = TRAIT_SHIFT_TABLE.get(trigger.type)
        if not deltas:
            continue
        old = to_big_five_string(state.traits)
        state.traits.openness = _clamp(state.traits.openness + deltas["O"] * trigger.magnitude)
        state.traits.conscientiousness = _clamp(state.traits.conscientiousness + deltas["C"] * trigger.magnitude)
        state.traits.extraversion = _clamp(state.traits.extraversion + deltas["E"] * trigger.magnitude)
        state.traits.agreeableness = _clamp(state.traits.agreeableness + deltas["A"] * trigger.magnitude)
        state.traits.neuroticism = _clamp(state.traits.neuroticism + deltas["N"] * trigger.magnitude)
        new = to_big_five_string(state.traits)
        if old != new:
            log.append(EvolutionLogEntry(
                day=day, change_type="trait_shift",
                description=f"{trigger.type.value}: {trigger.context or 'event'}",
                old_value=old, new_value=new,
            ))
    return log


# ── Fears ──

def evaluate_fears(state: NPCEvolutionState, triggers: list[EvolutionTrigger], day: int) -> list[EvolutionLogEntry]:
    log: list[EvolutionLogEntry] = []

    # Decay existing fears
    surviving: list[Fear] = []
    for fear in state.fears:
        fear.intensity = max(0.0, fear.intensity - fear.decay_rate)
        if fear.intensity >= 0.05:
            surviving.append(fear)
        else:
            log.append(EvolutionLogEntry(
                day=day, change_type="fear_faded",
                description=f"Fear of {fear.trigger} has faded",
            ))
    state.fears = surviving

    # Generate new fears
    existing_triggers = {f.trigger for f in state.fears}
    for trigger in triggers:
        candidates = FEAR_TRIGGERS.get(trigger.type, [])
        for candidate in candidates:
            keyword = candidate["context_contains"]
            if keyword and keyword not in trigger.context.lower():
                continue
            fear_name = candidate["fear"]
            if fear_name in existing_triggers:
                # Intensify existing fear
                for f in state.fears:
                    if f.trigger == fear_name:
                        f.intensity = min(1.0, f.intensity + 0.15 * trigger.magnitude)
                break
            state.fears.append(Fear(
                trigger=fear_name,
                intensity=candidate["intensity"] * trigger.magnitude,
                origin_day=day,
                origin_event=trigger.context or trigger.type.value,
            ))
            existing_triggers.add(fear_name)
            log.append(EvolutionLogEntry(
                day=day, change_type="fear_acquired",
                description=f"Developed fear of {fear_name} ({trigger.context or trigger.type.value})",
            ))
            break  # only one fear per trigger

    return log


# ── Goals ──

def evaluate_goals(
    state: NPCEvolutionState,
    npc: dict,
    triggers: list[EvolutionTrigger],
    day: int,
) -> list[EvolutionLogEntry]:
    log: list[EvolutionLogEntry] = []

    # Progress existing goals based on actions
    for trigger in triggers:
        if trigger.type == TriggerType.COMBAT_VICTORY:
            _progress_goal_matching(state, "protect", 0.15, day, log)
            _progress_goal_matching(state, "prove", 0.2, day, log)
            _progress_goal_matching(state, "stronger", 0.1, day, log)
        elif trigger.type == TriggerType.HELPED_SOMEONE:
            _progress_goal_matching(state, "help", 0.1, day, log)
            _progress_goal_matching(state, "repay", 0.15, day, log)
        elif trigger.type == TriggerType.ROBBERY_VICTIM:
            _fail_goal_matching(state, "safe", day, log)

    # Complete goals at 100% progress
    for goal in state.goals:
        if goal.status == GoalStatus.ACTIVE and goal.progress >= 1.0:
            goal.status = GoalStatus.COMPLETED
            goal.resolved_day = day
            log.append(EvolutionLogEntry(
                day=day, change_type="goal_completed",
                description=f"Completed: {goal.description}",
            ))

    # Abandon stale goals (active for 30+ days with <10% progress)
    for goal in state.goals:
        if (goal.status == GoalStatus.ACTIVE
                and day - goal.created_day > 30
                and goal.progress < 0.1):
            goal.status = GoalStatus.ABANDONED
            goal.resolved_day = day
            log.append(EvolutionLogEntry(
                day=day, change_type="goal_abandoned",
                description=f"Abandoned: {goal.description}",
            ))

    # Generate new goals from triggers
    active_count = sum(1 for g in state.goals if g.status == GoalStatus.ACTIVE)
    if active_count < 5:
        for trigger in triggers:
            templates = GOAL_TEMPLATES.get(trigger.type, [])
            for tmpl in templates:
                desc = tmpl["description"]
                desc = desc.replace("{source_npc}", trigger.source_npc_name or "someone")
                desc = desc.replace("{fear_trigger}", state.fears[-1].trigger if state.fears else "danger")
                # Don't duplicate existing goals
                if any(g.description == desc for g in state.goals):
                    continue
                state.goals.append(Goal(
                    description=desc, priority=tmpl["priority"], created_day=day,
                ))
                log.append(EvolutionLogEntry(
                    day=day, change_type="goal_new",
                    description=f"New goal: {desc}",
                ))
                active_count += 1
                if active_count >= 5:
                    break
            if active_count >= 5:
                break

    return log


# ── Archetype drift ──

def evaluate_archetype(state: NPCEvolutionState, current_archetype: str, day: int) -> list[EvolutionLogEntry]:
    log: list[EvolutionLogEntry] = []

    # Recalculate affinities
    for arch_id, profile in ARCHETYPE_PROFILES.items():
        state.archetype_affinity[arch_id] = round(_cosine_similarity(state.traits, profile), 3)

    # Find best matching archetype
    best_id = max(state.archetype_affinity, key=lambda k: state.archetype_affinity[k])
    best_score = state.archetype_affinity[best_id]
    current_score = state.archetype_affinity.get(current_archetype, 0)

    if best_id != current_archetype and (best_score - current_score) > ARCHETYPE_DRIFT_THRESHOLD:
        if state.archetype_drift_target == best_id:
            state.archetype_drift_days += 1
        else:
            state.archetype_drift_target = best_id
            state.archetype_drift_days = 1

        if state.archetype_drift_days >= ARCHETYPE_DRIFT_DAYS_REQUIRED:
            log.append(EvolutionLogEntry(
                day=day, change_type="archetype_drift",
                description=f"Personality shifted from {current_archetype} to {best_id}",
                old_value=current_archetype, new_value=best_id,
            ))
            state.archetype_drift_days = 0
            state.archetype_drift_target = None
    else:
        state.archetype_drift_days = 0
        state.archetype_drift_target = None

    return log


# ── Relationship tags ──

def evaluate_relationship_tags(
    state: NPCEvolutionState,
    triggers: list[EvolutionTrigger],
    day: int,
) -> list[EvolutionLogEntry]:
    log: list[EvolutionLogEntry] = []

    # Decay existing tags
    for npc_id, tags in list(state.relationship_tags.items()):
        for t in tags:
            t.strength = max(0.0, t.strength - 0.01)
        surviving = [t for t in tags if t.strength >= 0.1]
        if surviving:
            state.relationship_tags[npc_id] = surviving
        else:
            del state.relationship_tags[npc_id]

    # Add new tags from triggers
    tag_map = {
        TriggerType.BETRAYED: "betrayer",
        TriggerType.SAVED_BY: "savior",
        TriggerType.KILLED_SOMEONE: "killer",
        TriggerType.ROBBERY_VICTIM: "thief",
        TriggerType.HELPED_SOMEONE: "helped",
        TriggerType.RECEIVED_HELP: "ally",
    }
    for trigger in triggers:
        tag_name = tag_map.get(trigger.type)
        npc_id = trigger.source_npc_id
        if not tag_name or not npc_id:
            continue
        tags = state.relationship_tags.setdefault(npc_id, [])
        if any(t.tag == tag_name for t in tags):
            # Reinforce existing tag
            for t in tags:
                if t.tag == tag_name:
                    t.strength = min(1.0, t.strength + 0.2)
            continue
        tags.append(RelationshipTag(
            tag=tag_name, since_day=day,
            reason=trigger.context or trigger.type.value,
        ))
        log.append(EvolutionLogEntry(
            day=day, change_type="relationship_tag",
            description=f"Tagged {trigger.source_npc_name or npc_id} as '{tag_name}'",
        ))

    return log


# ── Main entry point ──

async def run_evolution_phase(
    gq,  # GraphQueries instance
    npc: dict,
    decision: dict | None,
    interactions: list[dict],
    world_day: int,
) -> list[EvolutionLogEntry]:
    """Run evolution for a single NPC. Returns log of all changes."""
    npc_id = npc.get("id", "")

    # Load or migrate evolution state
    raw_state = npc.get("evolution_state_json")
    if raw_state:
        state = NPCEvolutionState.model_validate_json(raw_state)
    else:
        state = migrate_npc_to_evolution(npc)

    # Classify events into triggers
    triggers = classify_events(npc, decision, interactions, world_day)
    if not triggers:
        # Still do daily maintenance (fear decay)
        fear_log = evaluate_fears(state, [], world_day)
        if fear_log:
            state.evolution_log.extend(fear_log)
            await _persist_state(gq, npc_id, state, npc.get("archetype", ""))
        return fear_log

    all_log: list[EvolutionLogEntry] = []

    # Apply evolution phases
    all_log.extend(apply_trait_shifts(state, triggers, world_day))
    all_log.extend(evaluate_fears(state, triggers, world_day))
    all_log.extend(evaluate_goals(state, npc, triggers, world_day))
    all_log.extend(evaluate_archetype(state, npc.get("archetype", ""), world_day))
    all_log.extend(evaluate_relationship_tags(state, triggers, world_day))

    # ── Nemesis phase ──
    # 1. Check if nemesis should be created (first defeat by player/opponent)
    for trigger in triggers:
        if trigger.type in (TriggerType.COMBAT_DEFEAT, TriggerType.ROBBERY_VICTIM) and trigger.source_npc_id:
            check_nemesis_trigger(
                evo=state,
                opponent_id=trigger.source_npc_id,
                opponent_name=trigger.source_npc_name or "unknown",
                combat_lost=(trigger.type == TriggerType.COMBAT_DEFEAT),
                robbed=(trigger.type == TriggerType.ROBBERY_VICTIM),
                nearly_killed=any(t.type == TriggerType.NEAR_DEATH for t in triggers),
                world_day=world_day,
            )
            break  # only one nemesis

    # 2. Record combat outcome if already has nemesis
    for trigger in triggers:
        if trigger.type == TriggerType.NEMESIS_VICTORY:
            record_nemesis_combat(state, won=True)
        elif trigger.type == TriggerType.NEMESIS_DEFEAT:
            record_nemesis_combat(state, won=False)

    # 3. Escalate + adapt
    all_log.extend(escalate_nemesis(state, world_day))
    all_log.extend(apply_nemesis_adaptations(state, world_day))

    # Keep log manageable (last 50 entries)
    state.evolution_log.extend(all_log)
    if len(state.evolution_log) > 50:
        state.evolution_log = state.evolution_log[-50:]

    # Persist
    await _persist_state(gq, npc_id, state, npc.get("archetype", ""))

    return all_log


async def _persist_state(gq, npc_id: str, state: NPCEvolutionState, current_archetype: str) -> None:
    """Save evolution state back to Neo4j."""
    updates: dict = {
        "evolution_state_json": state.model_dump_json(),
        "personality": to_big_five_string(state.traits),
        "goals": [g.description for g in state.goals if g.status == GoalStatus.ACTIVE],
    }

    # Check for archetype drift
    for entry in state.evolution_log:
        if entry.change_type == "archetype_drift" and entry.new_value:
            updates["archetype"] = entry.new_value

    await gq.update_npc(npc_id, updates)


# ── Helpers ──

def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def _progress_goal_matching(state: NPCEvolutionState, keyword: str, amount: float, day: int, log: list) -> None:
    for goal in state.goals:
        if goal.status == GoalStatus.ACTIVE and keyword in goal.description.lower():
            old = goal.progress
            goal.progress = min(1.0, goal.progress + amount)
            if goal.progress != old:
                log.append(EvolutionLogEntry(
                    day=day, change_type="goal_progress",
                    description=f"Goal '{goal.description}': {old:.0%} -> {goal.progress:.0%}",
                ))


def _fail_goal_matching(state: NPCEvolutionState, keyword: str, day: int, log: list) -> None:
    for goal in state.goals:
        if goal.status == GoalStatus.ACTIVE and keyword in goal.description.lower():
            goal.status = GoalStatus.FAILED
            goal.resolved_day = day
            log.append(EvolutionLogEntry(
                day=day, change_type="goal_failed",
                description=f"Failed: {goal.description}",
            ))
