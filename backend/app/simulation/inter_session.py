"""Inter-session events — what happens in the world while the player is away.

Runs a lightweight simulation of N days without LLM calls.
Uses deterministic rules: fear decay, goal progress, relationship drift,
nemesis escalation, random events from pool.
"""

from __future__ import annotations

import random

from app.models.evolution import (
    NPCEvolutionState, Fear, Goal, GoalStatus,
    RelationshipTag, EvolutionLogEntry,
)
from app.simulation.nemesis import escalate_nemesis, apply_nemesis_adaptations


# ── Event pool (no LLM needed) ──

EVENT_POOL = [
    {"type": "natural", "template": "A {weather} swept through {location}, causing minor damage."},
    {"type": "social", "template": "Villagers gathered at {location} for a community meeting."},
    {"type": "trade", "template": "A traveling merchant arrived at {location} with exotic wares."},
    {"type": "natural", "template": "The river near {location} flooded briefly after heavy rains."},
    {"type": "social", "template": "A wedding was celebrated at {location}."},
    {"type": "conflict", "template": "A brawl broke out at {location} between two locals."},
    {"type": "natural", "template": "Wild animals were spotted near {location}."},
    {"type": "trade", "template": "Harvest yields at {location} were {quality} this season."},
    {"type": "social", "template": "A traveling bard performed at {location} to great applause."},
    {"type": "conflict", "template": "Bandits were spotted on the road near {location}."},
    {"type": "natural", "template": "A rare herb was discovered growing near {location}."},
    {"type": "social", "template": "A child went missing near {location} but was found safe."},
]

_WEATHERS = ["storm", "blizzard", "heatwave", "thick fog", "hailstorm"]
_QUALITIES = ["excellent", "poor", "average", "surprisingly good", "devastatingly bad"]


def generate_inter_session_events(
    days_passed: int,
    location_names: list[str],
    seed: int | None = None,
) -> list[dict]:
    """Generate lightweight events for days the player was away.

    Returns list of {day_offset, type, description} dicts.
    Roughly 1-2 events per day.
    """
    rng = random.Random(seed)
    events: list[dict] = []

    for day in range(1, days_passed + 1):
        # 1-2 events per day (70% chance of 1, 30% of 2)
        n_events = 1 if rng.random() < 0.7 else 2
        # Use sample to avoid duplicates when n_events > 1
        day_templates = rng.sample(EVENT_POOL, min(n_events, len(EVENT_POOL)))

        for template in day_templates:
            loc = rng.choice(location_names) if location_names else "the village"
            desc = template["template"].format(
                location=loc,
                weather=rng.choice(_WEATHERS),
                quality=rng.choice(_QUALITIES),
            )
            events.append({
                "day_offset": day,
                "type": template["type"],
                "description": desc,
            })

    return events


def run_inter_session_evolution(
    evo: NPCEvolutionState,
    days_passed: int,
    start_day: int,
) -> list[EvolutionLogEntry]:
    """Advance NPC evolution state by N days without LLM.

    Handles:
    - Fear intensity decay
    - Fear removal when faded
    - Goal abandonment (>30 days, <10% progress)
    - Nemesis escalation by time
    - Nemesis adaptations on escalation
    - Relationship tag strength decay
    """
    all_logs: list[EvolutionLogEntry] = []
    rng = random.Random(start_day)

    for day_offset in range(1, days_passed + 1):
        world_day = start_day + day_offset

        # Fear decay
        faded = []
        for fear in evo.fears:
            fear.intensity = max(0.0, fear.intensity - fear.decay_rate)
            if fear.intensity < 0.05:
                faded.append(fear)
                all_logs.append(EvolutionLogEntry(
                    day=world_day, change_type="fear_faded",
                    description=f"Fear of {fear.trigger} has faded away",
                ))
        for f in faded:
            evo.fears.remove(f)

        # Goal abandonment
        for goal in evo.goals:
            if goal.status == GoalStatus.ACTIVE:
                days_active = world_day - goal.created_day
                if days_active > 30 and goal.progress < 0.1:
                    goal.status = GoalStatus.ABANDONED
                    goal.resolved_day = world_day
                    all_logs.append(EvolutionLogEntry(
                        day=world_day, change_type="goal_abandoned",
                        description=f"Abandoned goal: {goal.description} (stalled)",
                    ))

        # Relationship tag decay
        for npc_id, tags in evo.relationship_tags.items():
            for tag in tags:
                if tag.tag != "nemesis":  # nemesis doesn't decay
                    tag.strength = max(0.0, tag.strength - 0.01)

        # Nemesis escalation (by time only, no combat during inter-session)
        nem_logs = escalate_nemesis(evo, world_day)
        if nem_logs:
            all_logs.extend(nem_logs)
            adapt_logs = apply_nemesis_adaptations(evo, world_day, rng=rng)
            all_logs.extend(adapt_logs)

    # Clean up faded relationship tags
    for npc_id in list(evo.relationship_tags.keys()):
        evo.relationship_tags[npc_id] = [
            t for t in evo.relationship_tags[npc_id] if t.strength > 0.05
        ]
        if not evo.relationship_tags[npc_id]:
            del evo.relationship_tags[npc_id]

    return all_logs


async def process_inter_session(
    gq,
    days_passed: int,
    current_day: int,
    location_names: list[str],
) -> dict:
    """Run inter-session simulation for all NPCs.

    Returns summary: {events, npc_changes, days_simulated}
    """
    events = generate_inter_session_events(days_passed, location_names, seed=current_day)

    # Process each NPC
    all_npcs = await gq.get_all_npcs()
    npc_changes: list[dict] = []

    for npc in all_npcs:
        if not npc.get("alive", True):
            continue

        evo_json = npc.get("evolution_state_json")
        if not evo_json:
            continue

        try:
            evo = NPCEvolutionState.model_validate_json(evo_json)
        except Exception:
            continue

        start_day = current_day - days_passed
        logs = run_inter_session_evolution(evo, days_passed, start_day)

        if logs:
            evo.evolution_log.extend(logs)
            if len(evo.evolution_log) > 50:
                evo.evolution_log = evo.evolution_log[-50:]

            await gq.update_npc(npc["id"], {
                "evolution_state_json": evo.model_dump_json(),
            })

            npc_changes.append({
                "npc_id": npc["id"],
                "npc_name": npc["name"],
                "changes": [l.description for l in logs],
            })

    return {
        "days_simulated": days_passed,
        "events": events,
        "npc_changes": npc_changes,
    }
