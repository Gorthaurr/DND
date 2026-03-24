"""Scenario generator for quest generation from active scenarios."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import WORLD_SITUATIONS

_SCENARIO_TITLES = [
    "The Missing Merchant",
    "Plague of Shadows",
    "The Succession Crisis",
    "Harvest Sabotage",
    "The Sealed Tomb",
    "Border Tensions",
    "The False Prophet",
    "The Drought",
]

_PHASE_NAMES = ["setup", "escalation", "crisis", "resolution"]


class QuestGenerateGenerator(BaseScenarioGenerator):
    """Generates quest creation prompts tied to active scenarios."""

    def agent_type(self) -> str:
        return "quest_generate"

    def _generate_one(self) -> dict:
        scenario_title = self.rng.choice(_SCENARIO_TITLES)
        scenario_description = self.rng.choice(WORLD_SITUATIONS)
        phase_name = self.rng.choice(_PHASE_NAMES)

        # NPCs who could give quests (2-5)
        npc_count = self.rng.randint(2, 5)
        npcs = [self._random_npc() for _ in range(npc_count)]

        # Recent events (1-3)
        recent_events = self._random_events(self.rng.randint(1, 3))

        context = {
            "scenario_title": scenario_title,
            "scenario_description": scenario_description,
            "phase_name": phase_name,
            "npcs": npcs,
            "recent_events": recent_events,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("quest_generate.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "scenario_title": scenario_title,
                "phase": phase_name,
                "npc_count": npc_count,
            },
        }
