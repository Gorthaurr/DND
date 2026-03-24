"""Scenario generator for advancing active story arcs."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import NPC_ACTIONS, WORLD_SITUATIONS

_PHASE_NAMES = [
    ("setup", "Initial signs and rumors spread through the village."),
    ("escalation", "The situation worsens as tensions rise and sides are chosen."),
    ("crisis", "The conflict reaches a breaking point requiring immediate action."),
    ("resolution", "The aftermath — consequences are felt and new order emerges."),
]


class ScenarioAdvanceGenerator(BaseScenarioGenerator):
    """Generates scenario advancement prompts with tick events and NPC actions."""

    def agent_type(self) -> str:
        return "scenario_advance"

    def _generate_one(self) -> dict:
        world_day = self.rng.randint(5, 200)
        phase_idx = self.rng.randint(0, len(_PHASE_NAMES) - 1)
        current_name, current_desc = _PHASE_NAMES[phase_idx]
        next_phase = None
        if phase_idx < len(_PHASE_NAMES) - 1:
            nn, nd = _PHASE_NAMES[phase_idx + 1]
            next_phase = {"phase_id": f"phase_{phase_idx+1}", "name": nn, "description": nd}

        scenario = {
            "title": self.rng.choice([
                "The Missing Merchant", "Plague of Shadows", "The Succession Crisis",
                "Harvest Sabotage", "The Sealed Tomb", "Border Tensions",
            ]),
            "description": self.rng.choice(WORLD_SITUATIONS),
            "tension_level": round(self.rng.uniform(0.2, 1.0), 2),
            "start_day": world_day - self.rng.randint(1, 10),
        }

        # Tick events (1-4)
        event_types = ["social", "conflict", "discovery", "natural"]
        tick_events = [
            {"type": self.rng.choice(event_types), "description": e}
            for e in self._random_events(self.rng.randint(1, 4))
        ]

        # NPC actions (2-5)
        involved_npcs = [self._random_npc() for _ in range(self.rng.randint(2, 5))]
        npc_actions = []
        for n in involved_npcs:
            action = self.rng.choice(NPC_ACTIONS)
            npc_actions.append({
                "npc_name": n["name"],
                "action": action,
                "target": self.rng.choice(involved_npcs)["name"] if self.rng.random() > 0.5 else None,
                "dialogue": f"I need to {action} now." if self.rng.random() > 0.6 else None,
            })

        # Interactions (0-2)
        interactions = []
        if len(involved_npcs) >= 2:
            for _ in range(self.rng.randint(0, 2)):
                a, b = self.rng.sample(involved_npcs, 2)
                itype = self.rng.choice(["conversation", "argument", "trade", "fight"])
                interactions.append({
                    "summary": f"{a['name']} and {b['name']} had a {itype}.",
                })

        context = {
            "scenario": scenario,
            "world_day": world_day,
            "current_phase": {"phase_id": f"phase_{phase_idx}", "name": current_name, "description": current_desc},
            "next_phase": next_phase,
            "tick_events": tick_events,
            "npc_actions": npc_actions,
            "interactions": interactions,
            "involved_npcs": involved_npcs,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("scenario_advance.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "scenario_title": scenario["title"],
                "phase": current_name,
                "is_final": next_phase is None,
                "event_count": len(tick_events),
                "npc_count": len(involved_npcs),
            },
        }
