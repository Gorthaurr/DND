"""D&D 5e SRD character classes with hit dice, proficiencies, and spell slots."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CharClass:
    id: str
    name: str
    hit_die: int
    primary_ability: str
    saving_throws: list[str]
    armor_proficiencies: list[str]
    weapon_proficiencies: list[str]
    skill_options: list[str]
    num_skills: int
    spellcasting_ability: str | None = None  # None = non-caster
    caster_type: str = "none"  # "full", "half", "pact", "none"
    description: str = ""


CLASSES: dict[str, CharClass] = {}


def _c(cls: CharClass) -> None:
    CLASSES[cls.id] = cls


_c(CharClass(
    id="barbarian", name="Barbarian", hit_die=12,
    primary_ability="STR", saving_throws=["STR", "CON"],
    armor_proficiencies=["light", "medium", "shields"],
    weapon_proficiencies=["simple", "martial"],
    skill_options=["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"],
    num_skills=2,
    description="A fierce warrior who can enter a battle rage.",
))

_c(CharClass(
    id="bard", name="Bard", hit_die=8,
    primary_ability="CHA", saving_throws=["DEX", "CHA"],
    armor_proficiencies=["light"],
    weapon_proficiencies=["simple", "hand crossbow", "longsword", "rapier", "shortsword"],
    skill_options=["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", "History", "Insight", "Intimidation", "Investigation", "Medicine", "Nature", "Perception", "Performance", "Persuasion", "Religion", "Sleight of Hand", "Stealth", "Survival"],
    num_skills=3, spellcasting_ability="CHA", caster_type="full",
    description="A master of song, speech, and the magic they contain.",
))

_c(CharClass(
    id="cleric", name="Cleric", hit_die=8,
    primary_ability="WIS", saving_throws=["WIS", "CHA"],
    armor_proficiencies=["light", "medium", "shields"],
    weapon_proficiencies=["simple"],
    skill_options=["History", "Insight", "Medicine", "Persuasion", "Religion"],
    num_skills=2, spellcasting_ability="WIS", caster_type="full",
    description="A priestly champion who wields divine magic.",
))

_c(CharClass(
    id="druid", name="Druid", hit_die=8,
    primary_ability="WIS", saving_throws=["INT", "WIS"],
    armor_proficiencies=["light", "medium (nonmetal)", "shields (nonmetal)"],
    weapon_proficiencies=["club", "dagger", "dart", "javelin", "mace", "quarterstaff", "scimitar", "sickle", "sling", "spear"],
    skill_options=["Arcana", "Animal Handling", "Insight", "Medicine", "Nature", "Perception", "Religion", "Survival"],
    num_skills=2, spellcasting_ability="WIS", caster_type="full",
    description="A priest of the Old Faith, wielding the powers of nature.",
))

_c(CharClass(
    id="fighter", name="Fighter", hit_die=10,
    primary_ability="STR", saving_throws=["STR", "CON"],
    armor_proficiencies=["light", "medium", "heavy", "shields"],
    weapon_proficiencies=["simple", "martial"],
    skill_options=["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"],
    num_skills=2,
    description="A master of martial combat, skilled with a variety of weapons and armor.",
))

_c(CharClass(
    id="monk", name="Monk", hit_die=8,
    primary_ability="DEX", saving_throws=["STR", "DEX"],
    armor_proficiencies=[],
    weapon_proficiencies=["simple", "shortsword"],
    skill_options=["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
    num_skills=2,
    description="A martial artist pursuing physical and spiritual perfection.",
))

_c(CharClass(
    id="paladin", name="Paladin", hit_die=10,
    primary_ability="STR", saving_throws=["WIS", "CHA"],
    armor_proficiencies=["light", "medium", "heavy", "shields"],
    weapon_proficiencies=["simple", "martial"],
    skill_options=["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
    num_skills=2, spellcasting_ability="CHA", caster_type="half",
    description="A holy warrior bound to a sacred oath.",
))

_c(CharClass(
    id="ranger", name="Ranger", hit_die=10,
    primary_ability="DEX", saving_throws=["STR", "DEX"],
    armor_proficiencies=["light", "medium", "shields"],
    weapon_proficiencies=["simple", "martial"],
    skill_options=["Animal Handling", "Athletics", "Insight", "Investigation", "Nature", "Perception", "Stealth", "Survival"],
    num_skills=3, spellcasting_ability="WIS", caster_type="half",
    description="A warrior who combats threats on the edges of civilization.",
))

_c(CharClass(
    id="rogue", name="Rogue", hit_die=8,
    primary_ability="DEX", saving_throws=["DEX", "INT"],
    armor_proficiencies=["light"],
    weapon_proficiencies=["simple", "hand crossbow", "longsword", "rapier", "shortsword"],
    skill_options=["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
    num_skills=4,
    description="A scoundrel who uses stealth and trickery to overcome obstacles.",
))

_c(CharClass(
    id="sorcerer", name="Sorcerer", hit_die=6,
    primary_ability="CHA", saving_throws=["CON", "CHA"],
    armor_proficiencies=[],
    weapon_proficiencies=["dagger", "dart", "sling", "quarterstaff", "light crossbow"],
    skill_options=["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
    num_skills=2, spellcasting_ability="CHA", caster_type="full",
    description="A spellcaster who draws on inherent magic from a gift or bloodline.",
))

_c(CharClass(
    id="warlock", name="Warlock", hit_die=8,
    primary_ability="CHA", saving_throws=["WIS", "CHA"],
    armor_proficiencies=["light"],
    weapon_proficiencies=["simple"],
    skill_options=["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
    num_skills=2, spellcasting_ability="CHA", caster_type="pact",
    description="A wielder of magic derived from a bargain with an extraplanar entity.",
))

_c(CharClass(
    id="wizard", name="Wizard", hit_die=6,
    primary_ability="INT", saving_throws=["INT", "WIS"],
    armor_proficiencies=[],
    weapon_proficiencies=["dagger", "dart", "sling", "quarterstaff", "light crossbow"],
    skill_options=["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"],
    num_skills=2, spellcasting_ability="INT", caster_type="full",
    description="A scholarly magic-user who manipulates the fabric of reality.",
))


# ── Spell Slots Table (Full Casters) ──

FULL_CASTER_SLOTS: dict[int, dict[int, int]] = {
    1: {1: 2}, 2: {1: 3}, 3: {1: 4, 2: 2}, 4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2}, 6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1}, 8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1}, 10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1}, 12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1}, 14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1}, 16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

WARLOCK_SLOTS: dict[int, tuple[int, int]] = {
    # level: (num_slots, slot_level)
    1: (1, 1), 2: (2, 1), 3: (2, 2), 4: (2, 2), 5: (2, 3),
    6: (2, 3), 7: (2, 4), 8: (2, 4), 9: (2, 5), 10: (2, 5),
    11: (3, 5), 12: (3, 5), 13: (3, 5), 14: (3, 5), 15: (3, 5),
    16: (3, 5), 17: (4, 5), 18: (4, 5), 19: (4, 5), 20: (4, 5),
}


def get_spell_slots(class_id: str, level: int) -> dict[int, int]:
    """Get spell slots for a class at a given level. Returns {spell_level: num_slots}."""
    cls = CLASSES.get(class_id)
    if not cls or cls.caster_type == "none":
        return {}

    if cls.caster_type == "pact":
        num, slot_lvl = WARLOCK_SLOTS.get(level, (0, 0))
        return {slot_lvl: num} if num else {}

    if cls.caster_type == "half":
        effective = max(1, level // 2)
    else:
        effective = level

    return dict(FULL_CASTER_SLOTS.get(effective, {}))


def get_class(class_id: str) -> CharClass | None:
    return CLASSES.get(class_id)


def list_classes() -> list[CharClass]:
    return list(CLASSES.values())
