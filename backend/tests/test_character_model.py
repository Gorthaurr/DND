"""Tests for PlayerCharacter model."""

from app.models.character import PlayerCharacter, EquipmentSlot, ABILITY_NAMES


class TestEquipmentSlot:
    def test_defaults(self):
        s = EquipmentSlot(item_id="longsword")
        assert s.item_type == "weapon"
        assert not s.equipped


class TestPlayerCharacter:
    def test_defaults(self):
        pc = PlayerCharacter()
        assert pc.id == "player-1"
        assert pc.level == 1
        assert pc.gold == 50
        assert len(pc.ability_scores) == 6

    def test_ability_modifiers(self):
        pc = PlayerCharacter(ability_scores={"STR": 16, "DEX": 14, "CON": 12, "INT": 10, "WIS": 8, "CHA": 6})
        mods = pc.ability_modifiers
        assert mods["STR"] == 3
        assert mods["DEX"] == 2
        assert mods["CHA"] == -2

    def test_prof_bonus(self):
        pc = PlayerCharacter(level=1)
        assert pc.prof_bonus == 2
        pc5 = PlayerCharacter(level=5)
        assert pc5.prof_bonus == 3

    def test_ac_unarmored(self):
        pc = PlayerCharacter(ability_scores={"STR": 10, "DEX": 14, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10})
        assert pc.ac == 12  # 10 + DEX mod 2

    def test_initiative(self):
        pc = PlayerCharacter(ability_scores={"STR": 10, "DEX": 16, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10})
        assert pc.initiative == 3  # DEX mod

    def test_apply_race_bonuses(self):
        pc = PlayerCharacter(race_id="human", ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10})
        pc.apply_race_bonuses()
        # Human gets +1 to all
        assert all(v >= 10 for v in pc.ability_scores.values())

    def test_compute_hp(self):
        pc = PlayerCharacter(class_id="fighter", level=1, ability_scores={"STR": 10, "DEX": 10, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10})
        pc.compute_hp()
        assert pc.max_hp == 12  # d10 + CON mod 2
        assert pc.current_hp == 12

    def test_to_sheet_dict(self):
        pc = PlayerCharacter(name="Hero")
        pc.compute_hp()
        d = pc.to_sheet_dict()
        assert d["name"] == "Hero"
        assert "ability_scores" in d
        assert "ac" in d

    def test_spell_slots_wizard(self):
        pc = PlayerCharacter(class_id="wizard", level=1)
        slots = pc.spell_slots
        assert isinstance(slots, dict)

    def test_spell_slots_fighter(self):
        pc = PlayerCharacter(class_id="fighter", level=5)
        slots = pc.spell_slots
        assert slots == {}

    def test_ability_names_constant(self):
        assert len(ABILITY_NAMES) == 6
        assert "STR" in ABILITY_NAMES
