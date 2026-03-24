"""Lazy migration — converts static NPC data to NPCEvolutionState on first use."""

from __future__ import annotations

from app.models.evolution import (
    NPCEvolutionState, TraitScale, Goal, GoalStatus,
    parse_big_five,
)
from app.simulation.evolution_rules import ARCHETYPE_PROFILES


def migrate_npc_to_evolution(npc: dict) -> NPCEvolutionState:
    """
    Create initial NPCEvolutionState from existing static NPC data.

    Called lazily when evolution_state_json is None.
    Parses personality string, converts goals list, sets initial archetype affinity.
    """
    # Parse Big Five from string
    personality_str = npc.get("personality", "O:mid, C:mid, E:mid, A:mid, N:mid")
    traits = parse_big_five(personality_str)

    # Convert flat goals list to Goal objects
    raw_goals = npc.get("goals", [])
    goals = [
        Goal(
            description=g,
            status=GoalStatus.ACTIVE,
            priority=0.6 if i == 0 else 0.4,
            created_day=0,
        )
        for i, g in enumerate(raw_goals)
    ]

    # Compute initial archetype affinity
    current_archetype = npc.get("archetype", "")
    archetype_affinity: dict[str, float] = {}

    for arch_id, profile in ARCHETYPE_PROFILES.items():
        similarity = _cosine_similarity(traits, profile)
        archetype_affinity[arch_id] = round(similarity, 3)

    # Give current archetype a small boost (it was chosen for narrative reasons)
    if current_archetype in archetype_affinity:
        archetype_affinity[current_archetype] = min(
            1.0, archetype_affinity[current_archetype] + 0.1,
        )

    return NPCEvolutionState(
        traits=traits,
        fears=[],
        goals=goals,
        archetype_affinity=archetype_affinity,
        relationship_tags={},
        evolution_log=[],
    )


def _cosine_similarity(a: TraitScale, b: TraitScale) -> float:
    """Compute cosine similarity between two TraitScales."""
    a_vals = [a.openness, a.conscientiousness, a.extraversion, a.agreeableness, a.neuroticism]
    b_vals = [b.openness, b.conscientiousness, b.extraversion, b.agreeableness, b.neuroticism]

    dot = sum(x * y for x, y in zip(a_vals, b_vals))
    mag_a = sum(x * x for x in a_vals) ** 0.5
    mag_b = sum(x * x for x in b_vals) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)
