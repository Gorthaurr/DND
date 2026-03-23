"""Tests for D&D races."""

from app.dnd.races import get_race, list_races, RACES


class TestRaceRegistry:
    def test_9_races_registered(self):
        assert len(RACES) == 9

    def test_list_races_returns_all(self):
        assert len(list_races()) == 9

    def test_get_human(self):
        r = get_race("human")
        assert r is not None
        assert r.name == "Human"
        assert r.speed == 30

    def test_get_elf(self):
        r = get_race("elf")
        assert r is not None
        assert r.darkvision > 0

    def test_get_dwarf(self):
        r = get_race("dwarf")
        assert r is not None
        assert r.speed == 25

    def test_get_invalid(self):
        assert get_race("alien") is None

    def test_all_have_speed(self):
        for r in list_races():
            assert r.speed > 0

    def test_all_have_size(self):
        for r in list_races():
            assert r.size in ("Small", "Medium")

    def test_all_have_ability_bonuses(self):
        for r in list_races():
            assert isinstance(r.ability_bonuses, dict)
