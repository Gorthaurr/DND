"""Scenario generator for DM narration responses."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import PLAYER_MESSAGES

_LANGS = ["en", "en", "en", "ru", "de"]
_TIMES_OF_DAY = ["morning", "afternoon", "evening", "night"]
_PLAYER_CLASSES = ["fighter", "rogue", "wizard", "cleric", "ranger", "bard"]

_EXPLORATION_ACTIONS = [
    "I look around the area carefully.",
    "I search for hidden passages.",
    "I examine the strange markings on the wall.",
    "I open the old wooden chest.",
    "I enter the cave cautiously.",
]

_SOCIAL_ACTIONS = [
    "I approach the group of villagers.",
    "I try to calm the angry crowd.",
    "I bow respectfully to the noble.",
    "I demand answers from the guard.",
]

_AFTERMATH_ACTIONS = [
    "I loot the bodies.",
    "I check if anyone survived the fight.",
    "I clean my sword and look around.",
    "I tend to my wounds after the battle.",
]

_PUZZLE_ACTIONS = [
    "I try to solve the riddle on the door.",
    "I arrange the symbols in the correct order.",
    "I pour water into the stone basin.",
]

_SKILL_CHECK_ACTIONS = [
    "I try to climb the wall.",
    "I attempt to pick the lock.",
    "I try to sneak past the guards.",
    "I try to persuade the merchant to lower the price.",
    "I attempt to decipher the ancient text.",
]


class DMNarrateGenerator(BaseScenarioGenerator):
    """Generates DM narration scenarios: exploration, social, combat aftermath, puzzle, skill check."""

    def agent_type(self) -> str:
        return "dm_narrate"

    def _generate_one(self) -> dict:
        # Pick scenario type
        scenario_type = self.rng.choices(
            ["exploration", "social", "aftermath", "puzzle", "skill_check"],
            weights=[30, 25, 20, 10, 15],
            k=1,
        )[0]

        action_pool = {
            "exploration": _EXPLORATION_ACTIONS,
            "social": _SOCIAL_ACTIONS,
            "aftermath": _AFTERMATH_ACTIONS,
            "puzzle": _PUZZLE_ACTIONS,
            "skill_check": _SKILL_CHECK_ACTIONS,
        }
        player_action = self.rng.choice(action_pool[scenario_type])

        loc = self._random_location()
        lang = self.rng.choice(_LANGS)
        time_of_day = self.rng.choice(_TIMES_OF_DAY)

        # Present NPCs (0-4)
        npc_count = self.rng.randint(0, 4)
        present_npcs = [self._random_npc() for _ in range(npc_count)]
        for i, npc in enumerate(present_npcs):
            npc["id"] = f"npc-{i+1:03d}"

        # Dead NPCs (only for aftermath)
        dead_npcs = []
        if scenario_type == "aftermath" and self.rng.random() > 0.4:
            dead_count = self.rng.randint(1, 2)
            for i in range(dead_count):
                d = self._random_npc()
                d["id"] = f"npc-dead-{i+1:03d}"
                dead_npcs.append(d)

        # Player stats
        player_level = self.rng.randint(1, 10)
        player_class = self.rng.choice(_PLAYER_CLASSES)
        player_max_hp = 8 + (player_level - 1) * 5 + self.rng.randint(0, 3)
        player_hp = self.rng.randint(max(1, player_max_hp // 3), player_max_hp)

        # Inventory
        weapon_pool = ["longsword", "shortbow", "staff", "dagger", "mace"]
        misc_pool = ["torch", "rope", "health potion", "rations", "bedroll"]
        inventory = self.rng.sample(weapon_pool, 1) + self.rng.sample(misc_pool, self.rng.randint(1, 3))

        context = {
            "player_action": player_action,
            "location_name": loc["name"],
            "location_description": loc["description"],
            "present_npcs": present_npcs,
            "dead_npcs": dead_npcs,
            "player_level": player_level,
            "player_class": player_class,
            "player_hp": player_hp,
            "player_max_hp": player_max_hp,
            "player_ac": 10 + self.rng.randint(0, 8),
            "reputation": self.rng.randint(-50, 50),
            "world_day": self.rng.randint(1, 120),
            "inventory": inventory,
            "time_of_day": time_of_day,
            "recent_events": self._random_events(self.rng.randint(1, 3)),
            "recent_chat": [],
            "lang": lang,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("dm_narrate.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "scenario_type": scenario_type,
                "player_class": player_class,
                "player_level": player_level,
                "npc_count": npc_count,
                "dead_count": len(dead_npcs),
                "time_of_day": time_of_day,
                "lang": lang,
            },
        }
