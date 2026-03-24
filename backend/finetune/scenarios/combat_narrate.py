"""Scenario generator for combat narration."""

from __future__ import annotations

from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import DAMAGE_TYPES

_LANGS = ["en", "en", "en", "ru", "de"]


class CombatNarrateGenerator(BaseScenarioGenerator):
    """Generates combat narration scenarios: hits, misses, crits, deaths."""

    def agent_type(self) -> str:
        return "combat_narrate"

    def _generate_one(self) -> dict:
        loc = self._random_location()
        lang = self.rng.choice(_LANGS)

        # Combatant count (2-5)
        num_combatants = self.rng.randint(2, 5)
        combatants = [self._random_npc() for _ in range(num_combatants)]
        combatants[0]["name"] = "Player"  # First is always the player

        # Initiative order
        initiative_order = []
        for c in combatants:
            initiative_order.append({
                "name": c["name"],
                "initiative": self.rng.randint(1, 20) + (c.get("ac", 10) - 10) // 2,
            })
        initiative_order.sort(key=lambda x: x["initiative"], reverse=True)

        # Combat log (2-6 rounds)
        num_rounds = self.rng.randint(2, 6)
        combat_log = []
        for r in range(1, num_rounds + 1):
            attacker = self.rng.choice(combatants)
            defender = self.rng.choice([c for c in combatants if c["name"] != attacker["name"]])
            roll = self.rng.randint(1, 20)
            is_crit = roll == 20
            target_ac = defender.get("ac", 10)
            hit = roll >= target_ac or is_crit
            damage = (self.rng.randint(1, 8) + self.rng.randint(1, 8)) if is_crit else self.rng.randint(1, 8) if hit else 0
            notes = ""
            if is_crit:
                notes = "CRITICAL HIT!"
            elif roll == 1:
                notes = "Critical miss!"
            combat_log.append({
                "round": r,
                "attacker": attacker["name"],
                "defender": defender["name"],
                "attack_roll": roll,
                "target_ac": target_ac,
                "hit": hit,
                "damage": damage,
                "damage_type": self.rng.choice(DAMAGE_TYPES),
                "notes": notes,
            })

        # Outcome
        player_hp_change = -sum(e["damage"] for e in combat_log if e["defender"] == "Player" and e["hit"])
        player_killed = player_hp_change < -20 and self.rng.random() < 0.15

        npcs_killed = []
        for c in combatants[1:]:
            dmg_taken = sum(e["damage"] for e in combat_log if e["defender"] == c["name"] and e["hit"])
            if dmg_taken > c.get("max_hp", 10):
                npcs_killed.append(c["name"])

        context = {
            "location_name": loc["name"],
            "initiative_order": initiative_order,
            "combat_log": combat_log,
            "player_hp_change": player_hp_change,
            "player_killed": player_killed,
            "npcs_killed": npcs_killed,
            "lang": lang,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("combat_narrate.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "num_combatants": num_combatants,
                "num_rounds": num_rounds,
                "player_killed": player_killed,
                "npcs_killed_count": len(npcs_killed),
                "has_crit": any(e["notes"] == "CRITICAL HIT!" for e in combat_log),
                "lang": lang,
            },
        }
