"""Scenario generator for world scenario creation (story arcs)."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import LOCATIONS, WORLD_SITUATIONS

_SCENARIO_TEMPLATES = [
    {"title": "The Missing Merchant", "description": "A well-known trader vanished on the road between villages."},
    {"title": "Plague of Shadows", "description": "Dark creatures emerge from the forest at nightfall."},
    {"title": "The Succession Crisis", "description": "The village elder is dying and two factions compete for power."},
    {"title": "Harvest Sabotage", "description": "Someone is poisoning the crops before the harvest festival."},
    {"title": "The Sealed Tomb", "description": "An earthquake revealed an ancient tomb beneath the chapel."},
    {"title": "Border Tensions", "description": "Soldiers from a neighboring kingdom are testing the village borders."},
    {"title": "The False Prophet", "description": "A charismatic stranger claims divine authority and gathers followers."},
    {"title": "The Drought", "description": "The river is drying up and villagers accuse each other of hoarding water."},
]


class ScenarioGenerateGenerator(BaseScenarioGenerator):
    """Generates world scenario creation prompts."""

    def agent_type(self) -> str:
        return "scenario_generate"

    def _generate_one(self) -> dict:
        world_day = self.rng.randint(1, 200)

        # Locations (3-6)
        loc_count = self.rng.randint(3, 6)
        locations = self.rng.sample(LOCATIONS, min(loc_count, len(LOCATIONS)))

        # NPCs with tensions
        npc_count = self.rng.randint(3, 8)
        npcs = []
        for _ in range(npc_count):
            npc = self._random_npc()
            npc["tensions"] = self.rng.choice(WORLD_SITUATIONS) if self.rng.random() > 0.5 else None
            npcs.append(npc)

        # Active scenarios (0-2)
        active_scenarios = []
        if self.rng.random() > 0.5:
            for _ in range(self.rng.randint(1, 2)):
                tmpl = self.rng.choice(_SCENARIO_TEMPLATES)
                active_scenarios.append({
                    "title": tmpl["title"],
                    "description": tmpl["description"],
                    "current_phase_index": self.rng.randint(0, 3),
                    "tension_level": round(self.rng.uniform(0.2, 1.0), 2),
                })

        # Templates for inspiration (2-4)
        templates = self.rng.sample(_SCENARIO_TEMPLATES, min(self.rng.randint(2, 4), len(_SCENARIO_TEMPLATES)))

        context = {
            "world_day": world_day,
            "locations": locations,
            "npcs": npcs,
            "recent_events": self._random_events(self.rng.randint(2, 5)),
            "active_scenarios": active_scenarios,
            "scenario_templates": templates,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("scenario_generate.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "world_day": world_day,
                "npc_count": npc_count,
                "active_scenario_count": len(active_scenarios),
            },
        }
