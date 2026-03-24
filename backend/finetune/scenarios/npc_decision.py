"""Scenario generator for NPC autonomous decision-making."""

from __future__ import annotations

from app.models.archetypes import ARCHETYPES, ArchetypeID
from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import (
    ARCHETYPE_IDS,
    LOCATIONS,
    MOODS,
    NPC_ACTIONS,
)

_PHASES = ["morning", "afternoon", "evening"]

_EDGE_CASES = [
    {"label": "low_hp", "hp_ratio": 0.15},
    {"label": "surrounded", "enemy_count": 4},
    {"label": "just_betrayed", "betrayed": True},
    {"label": "normal", "hp_ratio": None},
]


class NPCDecisionGenerator(BaseScenarioGenerator):
    """Generates NPC decision scenarios across archetypes, moods, phases, edge cases."""

    def agent_type(self) -> str:
        return "npc_decision"

    def _generate_one(self) -> dict:
        npc = self._random_npc()
        loc = self._random_location()
        phase = self.rng.choice(_PHASES)
        edge = self.rng.choice(_EDGE_CASES)

        # Apply edge-case overrides
        if edge["label"] == "low_hp":
            npc["current_hp"] = max(1, int(npc["max_hp"] * edge["hp_ratio"]))

        # Nearby NPCs (1-4)
        nearby_count = self.rng.randint(1, 4)
        if edge["label"] == "surrounded":
            nearby_count = edge["enemy_count"]
        nearby_npcs = []
        for _ in range(nearby_count):
            other = self._random_npc()
            rel = self._random_relationship()
            if edge["label"] == "surrounded":
                rel["sentiment"] = round(self.rng.uniform(-1.0, -0.5), 2)
            other.update(rel)
            nearby_npcs.append(other)

        # Archetype metadata
        arch_id = npc["archetype"]
        try:
            arch = ARCHETYPES[ArchetypeID(arch_id)]
        except (ValueError, KeyError):
            arch = None

        # Nearby locations
        nearby_locs = [l["name"] for l in self.rng.sample(LOCATIONS, min(3, len(LOCATIONS)))]

        # Relationship tags (edge case: betrayal)
        rel_tags = {}
        if edge["label"] == "just_betrayed" and nearby_npcs:
            rel_tags[nearby_npcs[0]["name"]] = ["betrayer", "former_ally"]

        context = {
            "name": npc["name"],
            "age": npc["age"],
            "occupation": npc["occupation"],
            "personality": npc["personality"],
            "mood": npc["mood"],
            "goals": npc["goals"],
            "location_name": loc["name"],
            "location_description": loc["description"],
            "nearby_npcs": nearby_npcs,
            "recent_memories": self._random_memories(self.rng.randint(2, 5)),
            "recent_events": self._random_events(self.rng.randint(1, 3)),
            "world_day": self.rng.randint(1, 120),
            "current_phase": phase,
            "archetype_name": arch.name if arch else None,
            "archetype_decision_bias": arch.decision_bias if arch else None,
            "archetype_group_role": arch.group_role if arch else None,
            "equipment_summary": ", ".join(npc["equipment_ids"]),
            "combat_capability": f"Level {npc['level']} {npc['class_id']}, AC {npc['ac']}",
            "gold": npc["gold"],
            "nearby_locations": nearby_locs,
            "fears": npc["fears"],
            "active_goals": npc["active_goals"],
            "completed_goals": npc["completed_goals"],
            "relationship_tags": rel_tags,
            "active_scene_context": self.rng.choice([
                None, None, None,
                "Bandits are raiding the village!",
                "A fire just broke out at the smithy!",
                "Strange howling coming from the forest.",
            ]),
            "current_hp": npc["current_hp"],
            "max_hp": npc["max_hp"],
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("npc_decision.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "archetype": arch_id,
                "phase": phase,
                "edge_case": edge["label"],
                "mood": npc["mood"],
                "nearby_count": len(nearby_npcs),
            },
        }
