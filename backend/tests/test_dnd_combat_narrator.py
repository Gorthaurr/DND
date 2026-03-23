"""Tests for D&D combat narrator."""

from app.dnd.combat_narrator import resolve_attack, resolve_skill_check, CombatResult


class TestResolveAttack:
    def test_returns_combat_result(self):
        attacker = {"name": "Goran", "level": 5, "ability_scores": {"STR": 16, "DEX": 12},
                    "armor_id": None, "has_shield": False, "class_id": "fighter"}
        defender = {"name": "Goblin", "level": 1, "ability_scores": {"STR": 8, "DEX": 14},
                    "armor_id": "leather", "has_shield": False, "class_id": "rogue"}
        result = resolve_attack(attacker, defender, "longsword")
        assert isinstance(result, CombatResult)
        assert result.attacker_name == "Goran"
        assert result.defender_name == "Goblin"
        assert isinstance(result.narrative, str)
        assert len(result.narrative) > 0

    def test_unarmed_attack(self):
        attacker = {"name": "Monk", "level": 3, "ability_scores": {"STR": 14, "DEX": 16},
                    "armor_id": None, "has_shield": False, "class_id": "monk"}
        defender = {"name": "Thug", "level": 1, "ability_scores": {"STR": 12, "DEX": 10},
                    "armor_id": None, "has_shield": False, "class_id": "fighter"}
        result = resolve_attack(attacker, defender, None)
        assert isinstance(result, CombatResult)

    def test_hp_changes_are_ints(self):
        attacker = {"name": "A", "level": 1, "ability_scores": {"STR": 10, "DEX": 10},
                    "armor_id": None, "has_shield": False, "class_id": "fighter"}
        defender = {"name": "B", "level": 1, "ability_scores": {"STR": 10, "DEX": 10},
                    "armor_id": None, "has_shield": False, "class_id": "fighter"}
        result = resolve_attack(attacker, defender, "dagger")
        assert isinstance(result.attacker_hp_change, int)
        assert isinstance(result.defender_hp_change, int)


class TestResolveSkillCheck:
    def test_basic_check(self):
        char = {"name": "Rogue", "level": 5, "ability_scores": {"DEX": 18},
                "proficiencies": ["stealth"], "class_id": "rogue"}
        result = resolve_skill_check(char, "stealth", dc=15, ability="DEX")
        # Result may have 'success' at top level or nested in 'result'
        assert "result" in result or "success" in result
        assert "narrative" in result

    def test_unproficient_check(self):
        char = {"name": "Fighter", "level": 1, "ability_scores": {"INT": 8},
                "proficiencies": [], "class_id": "fighter"}
        result = resolve_skill_check(char, "arcana", dc=10, ability="INT")
        assert "result" in result or "success" in result
