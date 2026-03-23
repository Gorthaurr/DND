"""Tests for D&D dice rolling system."""

from app.dnd.dice import roll, roll_d20, roll_stats, ability_modifier, proficiency_bonus, RollResult


class TestRoll:
    def test_simple_d6(self):
        r = roll("1d6")
        assert 1 <= r.total <= 6
        assert r.notation == "1d6"
        assert len(r.rolls) == 1

    def test_multiple_dice(self):
        r = roll("3d6")
        assert 3 <= r.total <= 18
        assert len(r.rolls) == 3

    def test_modifier_positive(self):
        r = roll("1d6+3")
        assert r.modifier == 3
        assert r.total >= 4

    def test_modifier_negative(self):
        r = roll("1d6-2")
        assert r.modifier == -2

    def test_keep_highest(self):
        r = roll("4d6kh3")
        assert len(r.rolls) == 4
        assert len(r.kept) == 3

    def test_keep_lowest(self):
        r = roll("2d20kl1")
        assert len(r.rolls) == 2
        assert len(r.kept) == 1
        assert r.kept[0] == min(r.rolls)

    def test_d20(self):
        r = roll("1d20")
        assert 1 <= r.total <= 20

    def test_2d6_range(self):
        for _ in range(100):
            r = roll("2d6")
            assert 2 <= r.total <= 12


class TestRollD20:
    def test_basic(self):
        r = roll_d20()
        assert 1 <= r.total <= 20

    def test_with_modifier(self):
        r = roll_d20(modifier=5)
        assert 6 <= r.total <= 25

    def test_advantage(self):
        r = roll_d20(advantage=True)
        assert len(r.rolls) == 2
        assert r.total >= r.modifier + 1

    def test_disadvantage(self):
        r = roll_d20(disadvantage=True)
        assert len(r.rolls) == 2


class TestRollStats:
    def test_returns_six_scores(self):
        stats = roll_stats()
        assert len(stats) == 6

    def test_scores_in_valid_range(self):
        stats = roll_stats()
        for s in stats:
            assert 3 <= s <= 18

    def test_sorted_descending(self):
        stats = roll_stats()
        assert stats == sorted(stats, reverse=True)


class TestAbilityModifier:
    def test_score_10(self):
        assert ability_modifier(10) == 0

    def test_score_20(self):
        assert ability_modifier(20) == 5

    def test_score_1(self):
        assert ability_modifier(1) == -5

    def test_score_14(self):
        assert ability_modifier(14) == 2

    def test_score_8(self):
        assert ability_modifier(8) == -1


class TestProficiencyBonus:
    def test_level_1(self):
        assert proficiency_bonus(1) == 2

    def test_level_5(self):
        assert proficiency_bonus(5) == 3

    def test_level_9(self):
        assert proficiency_bonus(9) == 4

    def test_level_17(self):
        assert proficiency_bonus(17) == 6

    def test_level_20(self):
        assert proficiency_bonus(20) == 6
