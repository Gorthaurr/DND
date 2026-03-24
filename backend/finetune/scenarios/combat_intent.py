"""Scenario generator for combat intent detection."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import NAMES

_CLEAR_COMBAT = [
    "I attack {name} with my sword!",
    "I stab the {occ} in the back!",
    "I shoot an arrow at {name}!",
    "I cast fireball at everyone!",
    "I charge at {name} and swing my axe!",
    "I punch {name} in the face!",
    "I throw my dagger at the {occ}!",
]

_NON_COMBAT = [
    "I want to talk to {name}.",
    "I buy a health potion from the {occ}.",
    "I ask {name} about the missing villagers.",
    "I sit down at the tavern and order an ale.",
    "I try to persuade {name} to help me.",
    "I examine the notice board.",
    "I pray at the altar.",
]

_AMBIGUOUS = [
    "I reach for my sword and approach {name}.",
    "I grip my dagger tightly and stare at {name}.",
    "I step toward the {occ} with clenched fists.",
    "I push past {name} roughly.",
    "I draw my bow but don't aim it yet.",
    "I crack my knuckles and walk toward {name}.",
]


class CombatIntentGenerator(BaseScenarioGenerator):
    """Generates combat intent detection scenarios: clear, non-combat, ambiguous."""

    def agent_type(self) -> str:
        return "combat_intent"

    def _generate_one(self) -> dict:
        # Pick intent category
        category = self.rng.choices(
            ["clear_combat", "non_combat", "ambiguous"],
            weights=[40, 35, 25],
            k=1,
        )[0]

        pool = {"clear_combat": _CLEAR_COMBAT, "non_combat": _NON_COMBAT, "ambiguous": _AMBIGUOUS}
        template = self.rng.choice(pool[category])

        # Present NPCs (1-4)
        npc_count = self.rng.randint(1, 4)
        present_npcs = []
        for i in range(npc_count):
            npc = self._random_npc()
            npc["npc_id"] = f"npc-{i+1:03d}"
            rel = self._random_relationship()
            npc["sentiment"] = rel["sentiment"]
            present_npcs.append(npc)

        target = self.rng.choice(present_npcs)
        action = template.format(name=target["name"], occ=target["occupation"])

        # Player
        player_npc = self._random_npc()
        player = {
            "name": "Adventurer",
            "level": player_npc["level"],
            "weapon_ids": player_npc["equipment_ids"][:2],
        }

        context = {
            "player_action": action,
            "present_npcs": present_npcs,
            "player": player,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("combat_intent.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "intent_category": category,
                "target_name": target["name"],
                "npc_count": npc_count,
            },
        }
