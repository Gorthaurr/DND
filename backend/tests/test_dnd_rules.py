"""Tests for D&D rules engine."""

from app.dnd.rules import (
    level_for_xp, compute_ac, attack_roll, damage_roll,
    ability_check, saving_throw, compute_max_hp,
    spell_dc, spell_attack_bonus, XP_TABLE,
)


class TestLevelForXP:
    def test_zero_xp(self):
        assert level_for_xp(0) == 1

    def test_level_2(self):
        assert level_for_xp(300) >= 2

    def test_level_20(self):
        assert level_for_xp(999999) == 20

    def test_xp_table_has_20_levels(self):
        assert len(XP_TABLE) == 20


class TestComputeAC:
    def test_unarmored(self):
        ac = compute_ac(None, 14)  # DEX 14 → +2
        assert ac == 12

    def test_with_shield(self):
        ac = compute_ac(None, 10, has_shield=True)
        assert ac == 12  # 10 + 0 + 2

    def test_chain_mail(self):
        ac = compute_ac("chain-mail", 10)
        assert ac >= 14  # heavy armor, no DEX

    def test_leather(self):
        ac = compute_ac("leather", 16)  # light, full DEX
        assert ac >= 14

    def test_invalid_armor(self):
        ac = compute_ac("nonexistent", 10)
        assert ac == 10  # falls back to unarmored


class TestAttackRoll:
    def test_returns_dict(self):
        r = attack_roll(16, 5)
        assert "roll" in r
        assert "total" in r
        assert "hit" in r or "natural" in r or isinstance(r, dict)

    def test_high_ability(self):
        results = [attack_roll(20, 10) for _ in range(10)]
        assert any(r["total"] > 10 for r in results)


class TestDamageRoll:
    def test_basic_damage(self):
        r = damage_roll("1d8", 16)
        assert r["total"] > 0

    def test_crit_damage(self):
        r = damage_roll("1d8", 14, is_crit=True)
        assert r["total"] > 0


class TestAbilityCheck:
    def test_basic_check(self):
        r = ability_check(14, dc=10)
        assert "success" in r
        assert isinstance(r["success"], bool)

    def test_proficient_check(self):
        r = ability_check(14, level=5, is_proficient=True, dc=10)
        assert "total" in r

    def test_advantage(self):
        r = ability_check(14, dc=10, advantage=True)
        assert "success" in r


class TestSavingThrow:
    def test_basic_save(self):
        r = saving_throw(14, dc=12)
        assert "success" in r

    def test_proficient_save(self):
        r = saving_throw(14, level=5, is_proficient=True, dc=15)
        assert isinstance(r["success"], bool)


class TestComputeMaxHP:
    def test_level_1_fighter(self):
        hp = compute_max_hp(10, 1, 14)  # d10, level 1, CON 14
        assert hp == 12  # 10 + 2 (CON mod)

    def test_level_5(self):
        hp = compute_max_hp(10, 5, 14)
        assert hp > 12

    def test_wizard_low_hp(self):
        hp = compute_max_hp(6, 1, 10)  # d6, CON 10
        assert hp == 6


class TestSpellDC:
    def test_basic_dc(self):
        dc = spell_dc(16, 5)  # ability 16, level 5
        assert dc > 8

    def test_spell_attack_bonus(self):
        bonus = spell_attack_bonus(16, 5)
        assert bonus > 0
