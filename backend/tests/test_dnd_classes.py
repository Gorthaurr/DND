"""Tests for D&D character classes."""

from app.dnd.classes import get_class, list_classes, get_spell_slots, CLASSES


class TestClassRegistry:
    def test_12_classes_registered(self):
        assert len(CLASSES) == 12

    def test_list_classes_returns_all(self):
        assert len(list_classes()) == 12

    def test_get_fighter(self):
        c = get_class("fighter")
        assert c is not None
        assert c.name == "Fighter"
        assert c.hit_die == 10

    def test_get_wizard(self):
        c = get_class("wizard")
        assert c is not None
        assert c.hit_die == 6
        assert c.spellcasting_ability == "INT"
        assert c.caster_type == "full"

    def test_get_rogue(self):
        c = get_class("rogue")
        assert c is not None
        assert c.hit_die == 8

    def test_get_cleric(self):
        c = get_class("cleric")
        assert c is not None
        assert c.caster_type == "full"

    def test_get_invalid(self):
        assert get_class("nonexistent") is None

    def test_all_have_hit_die(self):
        for c in list_classes():
            assert c.hit_die in (6, 8, 10, 12)

    def test_all_have_primary_ability(self):
        for c in list_classes():
            assert c.primary_ability


class TestSpellSlots:
    def test_wizard_level_1(self):
        slots = get_spell_slots("wizard", 1)
        assert 1 in slots  # level 1 spell slots

    def test_fighter_no_slots(self):
        slots = get_spell_slots("fighter", 1)
        assert slots == {}

    def test_warlock_slots(self):
        slots = get_spell_slots("warlock", 1)
        assert isinstance(slots, dict)
