"""Scenario generator for world event generation."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import LOCATIONS, WORLD_SITUATIONS


class EventGenerateGenerator(BaseScenarioGenerator):
    """Generates world event prompts with varying tension levels."""

    def agent_type(self) -> str:
        return "event_generate"

    def _generate_one(self) -> dict:
        world_day = self.rng.randint(1, 300)

        # Locations (3-8)
        loc_count = self.rng.randint(3, 8)
        locations = self.rng.sample(LOCATIONS, min(loc_count, len(LOCATIONS)))

        # Recent events for context (1-4)
        recent_events = self._random_events(self.rng.randint(1, 4))

        # Current tensions (0-3)
        tension_count = self.rng.randint(0, 3)
        tensions = self.rng.sample(WORLD_SITUATIONS, min(tension_count, len(WORLD_SITUATIONS)))

        context = {
            "world_day": world_day,
            "locations": locations,
            "recent_events": recent_events,
            "tensions": tensions,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("event_generate.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "world_day": world_day,
                "location_count": loc_count,
                "tension_count": tension_count,
            },
        }
