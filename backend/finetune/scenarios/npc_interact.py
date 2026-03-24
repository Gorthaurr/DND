"""Scenario generator for NPC-to-NPC interactions."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import WORLD_SITUATIONS


class NPCInteractGenerator(BaseScenarioGenerator):
    """Generates NPC interaction scenarios between archetype pairs."""

    def agent_type(self) -> str:
        return "npc_interact"

    def _generate_one(self) -> dict:
        loc = self._random_location()
        npc_a = self._random_npc()
        npc_b = self._random_npc()

        a_to_b = self._random_relationship()
        b_to_a = self._random_relationship()

        # Optional scenario context (50% chance)
        scenario_context = None
        if self.rng.random() > 0.5:
            scenario_context = self.rng.choice(WORLD_SITUATIONS)

        context = {
            "location_name": loc["name"],
            "npc_a": npc_a,
            "npc_b": npc_b,
            "a_to_b": a_to_b,
            "b_to_a": b_to_a,
            "scenario_context": scenario_context,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("npc_interact.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "archetype_a": npc_a["archetype"],
                "archetype_b": npc_b["archetype"],
                "sentiment_a_to_b": a_to_b["sentiment"],
                "sentiment_b_to_a": b_to_a["sentiment"],
                "has_scenario": scenario_context is not None,
            },
        }
