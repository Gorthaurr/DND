"""Tests for D&D equipment (weapons, armor, items)."""

from app.dnd.equipment import (
    get_weapon, get_armor, get_item,
    list_weapons, list_armors, list_items,
    WEAPONS, ARMORS, ITEMS,
)


class TestWeapons:
    def test_weapons_registered(self):
        assert len(WEAPONS) >= 20

    def test_get_longsword(self):
        w = get_weapon("longsword")
        assert w is not None
        assert w.damage_type in ("slashing", "piercing", "bludgeoning")
        assert "d" in w.damage_dice

    def test_get_dagger(self):
        w = get_weapon("dagger")
        assert w is not None

    def test_get_invalid(self):
        assert get_weapon("lightsaber") is None

    def test_list_weapons(self):
        weapons = list_weapons()
        assert len(weapons) == len(WEAPONS)

    def test_all_have_damage_dice(self):
        for w in list_weapons():
            assert w.damage_dice
            assert w.damage_type


class TestArmors:
    def test_armors_registered(self):
        assert len(ARMORS) >= 10

    def test_get_chain_mail(self):
        a = get_armor("chain-mail")
        assert a is not None
        assert a.ac_base >= 14

    def test_get_shield(self):
        a = get_armor("shield")
        assert a is not None

    def test_get_invalid(self):
        assert get_armor("force-field") is None

    def test_list_armors(self):
        assert len(list_armors()) == len(ARMORS)

    def test_all_have_ac(self):
        for a in list_armors():
            assert a.ac_base >= 0
            assert a.armor_type in ("light", "medium", "heavy", "shield")


class TestItems:
    def test_items_registered(self):
        assert len(ITEMS) >= 10

    def test_get_health_potion(self):
        i = get_item("health-potion")
        assert i is not None

    def test_get_invalid(self):
        assert get_item("infinity-stone") is None

    def test_list_items(self):
        assert len(list_items()) == len(ITEMS)
