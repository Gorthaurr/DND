"""D&D 5e class features by level (core features only, no subclass)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassFeature:
    id: str
    name: str
    class_id: str
    level: int
    description: str
    feature_type: str  # passive / active / resource / aura / reaction
    uses_per: str | None = None  # short_rest / long_rest / at_will / None
    uses_count: int | None = None
    mechanic: dict | None = None


FEATURES: dict[str, ClassFeature] = {}

_ALL_BY_CLASS: dict[str, list[ClassFeature]] = {}


def _f(feat: ClassFeature) -> None:
    """Register a class feature."""
    FEATURES[feat.id] = feat
    _ALL_BY_CLASS.setdefault(feat.class_id, []).append(feat)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_features_for_class(class_id: str) -> list[ClassFeature]:
    """All features for a given class, sorted by level."""
    return sorted(_ALL_BY_CLASS.get(class_id, []), key=lambda f: f.level)


def get_features_at_level(class_id: str, level: int) -> list[ClassFeature]:
    """Features gained exactly at the specified level."""
    return [f for f in _ALL_BY_CLASS.get(class_id, []) if f.level == level]


def get_features_up_to_level(class_id: str, level: int) -> list[ClassFeature]:
    """All features up to and including the given level, sorted."""
    return sorted(
        [f for f in _ALL_BY_CLASS.get(class_id, []) if f.level <= level],
        key=lambda f: f.level,
    )


def get_feature(feature_id: str) -> ClassFeature | None:
    return FEATURES.get(feature_id)


# ═══════════════════════════════════════════════════════════════════════════
# Helper to register ASI at standard levels for a class
# ═══════════════════════════════════════════════════════════════════════════

def _asi(class_id: str, levels: list[int]) -> None:
    for lvl in levels:
        _f(ClassFeature(
            id=f"{class_id}_asi_{lvl}",
            name="Ability Score Improvement",
            class_id=class_id,
            level=lvl,
            description=(
                "Increase one ability score by 2, or two ability scores by 1. "
                "Alternatively, choose a feat."
            ),
            feature_type="passive",
            uses_per=None,
            mechanic={"type": "asi", "points": 2},
        ))


# ═══════════════════════════════════════════════════════════════════════════
#  BARBARIAN
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="barbarian_rage",
    name="Rage",
    class_id="barbarian",
    level=1,
    description=(
        "In battle, you fight with primal ferocity. On your turn, you can enter "
        "a rage as a bonus action. While raging, you gain bonus damage, resistance "
        "to bludgeoning/piercing/slashing damage, and advantage on STR checks/saves."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=2,
    mechanic={
        "type": "buff",
        "bonus_damage": 2,
        "resistance": ["bludgeoning", "piercing", "slashing"],
        "advantage": ["STR"],
        "duration": "1 minute",
        "scaling": {5: {"bonus_damage": 2, "uses": 3},
                    9: {"bonus_damage": 3, "uses": 4},
                    12: {"uses": 5},
                    16: {"bonus_damage": 4, "uses": 5},
                    17: {"uses": 6},
                    20: {"uses": "unlimited"}},
    },
))

_f(ClassFeature(
    id="barbarian_unarmored_defense",
    name="Unarmored Defense",
    class_id="barbarian",
    level=1,
    description=(
        "While not wearing armor, your AC equals 10 + DEX modifier + CON modifier. "
        "You can use a shield and still gain this benefit."
    ),
    feature_type="passive",
    mechanic={"type": "ac_formula", "formula": "10 + DEX + CON", "allows_shield": True},
))

_f(ClassFeature(
    id="barbarian_reckless_attack",
    name="Reckless Attack",
    class_id="barbarian",
    level=2,
    description=(
        "When you make your first attack on your turn, you can decide to attack "
        "recklessly, giving you advantage on melee weapon attack rolls using STR "
        "during this turn, but attack rolls against you have advantage until your "
        "next turn."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "attack_modifier",
        "grants_advantage": True,
        "grants_enemies_advantage": True,
        "ability": "STR",
    },
))

_f(ClassFeature(
    id="barbarian_danger_sense",
    name="Danger Sense",
    class_id="barbarian",
    level=2,
    description=(
        "You have advantage on DEX saving throws against effects that you can see, "
        "such as traps and spells. You cannot be blinded, deafened, or incapacitated "
        "to gain this benefit."
    ),
    feature_type="passive",
    mechanic={"type": "save_advantage", "ability": "DEX", "condition": "can_see_effect"},
))

_f(ClassFeature(
    id="barbarian_extra_attack",
    name="Extra Attack",
    class_id="barbarian",
    level=5,
    description="You can attack twice, instead of once, whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 2},
))

_f(ClassFeature(
    id="barbarian_fast_movement",
    name="Fast Movement",
    class_id="barbarian",
    level=5,
    description="Your speed increases by 10 feet while you aren't wearing heavy armor.",
    feature_type="passive",
    mechanic={"type": "speed_bonus", "bonus": 10, "condition": "no_heavy_armor"},
))

_f(ClassFeature(
    id="barbarian_feral_instinct",
    name="Feral Instinct",
    class_id="barbarian",
    level=7,
    description=(
        "You have advantage on initiative rolls. Additionally, if you are surprised "
        "at the start of combat and aren't incapacitated, you can act normally on "
        "your first turn if you enter your rage before doing anything else."
    ),
    feature_type="passive",
    mechanic={"type": "initiative_advantage", "anti_surprise": True},
))

_f(ClassFeature(
    id="barbarian_brutal_critical_9",
    name="Brutal Critical (1 die)",
    class_id="barbarian",
    level=9,
    description="You can roll one additional weapon damage die when determining the extra damage for a critical hit.",
    feature_type="passive",
    mechanic={"type": "critical_bonus_dice", "extra_dice": 1},
))

_f(ClassFeature(
    id="barbarian_relentless_rage",
    name="Relentless Rage",
    class_id="barbarian",
    level=11,
    description=(
        "Your rage can keep you fighting despite grievous wounds. If you drop to 0 HP "
        "while raging and don't die outright, you can make a DC 10 CON save to drop to "
        "1 HP instead. The DC increases by 5 each time until you finish a rest."
    ),
    feature_type="passive",
    mechanic={"type": "death_save_override", "initial_dc": 10, "dc_increment": 5, "condition": "raging"},
))

_f(ClassFeature(
    id="barbarian_brutal_critical_13",
    name="Brutal Critical (2 dice)",
    class_id="barbarian",
    level=13,
    description="You can roll two additional weapon damage dice when determining the extra damage for a critical hit.",
    feature_type="passive",
    mechanic={"type": "critical_bonus_dice", "extra_dice": 2},
))

_f(ClassFeature(
    id="barbarian_persistent_rage",
    name="Persistent Rage",
    class_id="barbarian",
    level=15,
    description="Your rage is so fierce that it ends early only if you fall unconscious or if you choose to end it.",
    feature_type="passive",
    mechanic={"type": "rage_modifier", "no_early_end": True},
))

_f(ClassFeature(
    id="barbarian_brutal_critical_17",
    name="Brutal Critical (3 dice)",
    class_id="barbarian",
    level=17,
    description="You can roll three additional weapon damage dice when determining the extra damage for a critical hit.",
    feature_type="passive",
    mechanic={"type": "critical_bonus_dice", "extra_dice": 3},
))

_f(ClassFeature(
    id="barbarian_indomitable_might",
    name="Indomitable Might",
    class_id="barbarian",
    level=18,
    description=(
        "If your total for a STR check is less than your STR score, you can use "
        "that score in place of the total."
    ),
    feature_type="passive",
    mechanic={"type": "ability_floor", "ability": "STR"},
))

_f(ClassFeature(
    id="barbarian_primal_champion",
    name="Primal Champion",
    class_id="barbarian",
    level=20,
    description="Your STR and CON scores each increase by 4. Your maximum for those scores is now 24.",
    feature_type="passive",
    mechanic={"type": "ability_increase", "STR": 4, "CON": 4, "new_max": 24},
))

_asi("barbarian", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  BARD
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="bard_spellcasting",
    name="Spellcasting",
    class_id="bard",
    level=1,
    description=(
        "You have learned to untangle and reshape the fabric of reality in harmony "
        "with your wishes and music. Your spells are part of your vast repertoire."
    ),
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "CHA", "caster_type": "full"},
))

_f(ClassFeature(
    id="bard_bardic_inspiration",
    name="Bardic Inspiration",
    class_id="bard",
    level=1,
    description=(
        "You can inspire others through stirring words or music. A creature that "
        "can hear you within 60 feet gains a Bardic Inspiration die (d6) to add "
        "to one ability check, attack roll, or saving throw."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=None,  # equals CHA modifier
    mechanic={
        "type": "inspiration_die",
        "die": "d6",
        "uses": "CHA_mod",
        "range": 60,
        "scaling": {5: {"die": "d8"}, 10: {"die": "d10"}, 15: {"die": "d12"}},
    },
))

_f(ClassFeature(
    id="bard_jack_of_all_trades",
    name="Jack of All Trades",
    class_id="bard",
    level=2,
    description="You can add half your proficiency bonus, rounded down, to any ability check you make that doesn't already include your proficiency bonus.",
    feature_type="passive",
    mechanic={"type": "half_proficiency", "applies_to": "non_proficient_checks"},
))

_f(ClassFeature(
    id="bard_song_of_rest",
    name="Song of Rest",
    class_id="bard",
    level=2,
    description=(
        "You can use soothing music or oration to help revitalize your wounded allies "
        "during a short rest. If you or any friendly creatures regain HP at the end of "
        "a short rest by spending Hit Dice, each gains an extra 1d6 HP."
    ),
    feature_type="passive",
    mechanic={
        "type": "rest_healing",
        "die": "d6",
        "scaling": {9: {"die": "d8"}, 13: {"die": "d10"}, 17: {"die": "d12"}},
    },
))

_f(ClassFeature(
    id="bard_expertise_3",
    name="Expertise",
    class_id="bard",
    level=3,
    description="Choose two of your skill proficiencies. Your proficiency bonus is doubled for any ability check you make that uses either of the chosen proficiencies.",
    feature_type="passive",
    mechanic={"type": "expertise", "num_skills": 2},
))

_f(ClassFeature(
    id="bard_font_of_inspiration",
    name="Font of Inspiration",
    class_id="bard",
    level=5,
    description="You regain all expended uses of Bardic Inspiration on a short or long rest.",
    feature_type="passive",
    mechanic={"type": "resource_recovery", "resource": "bardic_inspiration", "on": "short_rest"},
))

_f(ClassFeature(
    id="bard_countercharm",
    name="Countercharm",
    class_id="bard",
    level=6,
    description=(
        "As an action, you can start a performance that lasts until the end of your "
        "next turn. During that time, you and any friendly creatures within 30 feet "
        "have advantage on saving throws against being frightened or charmed."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "aura_buff",
        "radius": 30,
        "advantage_saves": ["frightened", "charmed"],
        "duration": "end_of_next_turn",
    },
))

_f(ClassFeature(
    id="bard_expertise_10",
    name="Expertise",
    class_id="bard",
    level=10,
    description="Choose two more of your skill proficiencies to gain expertise in.",
    feature_type="passive",
    mechanic={"type": "expertise", "num_skills": 2},
))

_f(ClassFeature(
    id="bard_magical_secrets_10",
    name="Magical Secrets",
    class_id="bard",
    level=10,
    description="Choose two spells from any class, including this one. The chosen spells count as bard spells for you.",
    feature_type="passive",
    mechanic={"type": "learn_spells", "num_spells": 2, "source": "any_class"},
))

_f(ClassFeature(
    id="bard_magical_secrets_14",
    name="Magical Secrets",
    class_id="bard",
    level=14,
    description="Choose two more spells from any class.",
    feature_type="passive",
    mechanic={"type": "learn_spells", "num_spells": 2, "source": "any_class"},
))

_f(ClassFeature(
    id="bard_magical_secrets_18",
    name="Magical Secrets",
    class_id="bard",
    level=18,
    description="Choose two more spells from any class.",
    feature_type="passive",
    mechanic={"type": "learn_spells", "num_spells": 2, "source": "any_class"},
))

_f(ClassFeature(
    id="bard_superior_inspiration",
    name="Superior Inspiration",
    class_id="bard",
    level=20,
    description="When you roll initiative and have no uses of Bardic Inspiration left, you regain one use.",
    feature_type="passive",
    mechanic={"type": "resource_recovery", "resource": "bardic_inspiration", "trigger": "initiative", "amount": 1},
))

_asi("bard", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  CLERIC
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="cleric_spellcasting",
    name="Spellcasting",
    class_id="cleric",
    level=1,
    description=(
        "As a conduit for divine power, you can cast cleric spells. Wisdom is your "
        "spellcasting ability. You prepare spells from the entire cleric spell list."
    ),
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "WIS", "caster_type": "full", "prepared": True},
))

_f(ClassFeature(
    id="cleric_channel_divinity",
    name="Channel Divinity (1/rest)",
    class_id="cleric",
    level=2,
    description=(
        "You gain the ability to channel divine energy directly from your deity, "
        "using it to fuel magical effects. You start with Turn Undead and one "
        "effect determined by your domain."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=1,
    mechanic={
        "type": "resource",
        "options": ["turn_undead", "subclass_option"],
        "scaling": {6: {"uses": 2}, 18: {"uses": 3}},
    },
))

_f(ClassFeature(
    id="cleric_channel_divinity_6",
    name="Channel Divinity (2/rest)",
    class_id="cleric",
    level=6,
    description="You can use Channel Divinity twice between rests.",
    feature_type="passive",
    mechanic={"type": "resource_upgrade", "resource": "channel_divinity", "uses": 2},
))

_f(ClassFeature(
    id="cleric_destroy_undead_5",
    name="Destroy Undead (CR 1/2)",
    class_id="cleric",
    level=5,
    description="When an undead fails its save against Turn Undead and has CR 1/2 or lower, it is instantly destroyed.",
    feature_type="passive",
    mechanic={
        "type": "destroy_undead",
        "cr_threshold": 0.5,
        "scaling": {8: {"cr": 1}, 11: {"cr": 2}, 14: {"cr": 3}, 17: {"cr": 4}},
    },
))

_f(ClassFeature(
    id="cleric_destroy_undead_8",
    name="Destroy Undead (CR 1)",
    class_id="cleric",
    level=8,
    description="Destroy Undead now affects undead of CR 1 or lower.",
    feature_type="passive",
    mechanic={"type": "destroy_undead", "cr_threshold": 1},
))

_f(ClassFeature(
    id="cleric_destroy_undead_11",
    name="Destroy Undead (CR 2)",
    class_id="cleric",
    level=11,
    description="Destroy Undead now affects undead of CR 2 or lower.",
    feature_type="passive",
    mechanic={"type": "destroy_undead", "cr_threshold": 2},
))

_f(ClassFeature(
    id="cleric_destroy_undead_14",
    name="Destroy Undead (CR 3)",
    class_id="cleric",
    level=14,
    description="Destroy Undead now affects undead of CR 3 or lower.",
    feature_type="passive",
    mechanic={"type": "destroy_undead", "cr_threshold": 3},
))

_f(ClassFeature(
    id="cleric_destroy_undead_17",
    name="Destroy Undead (CR 4)",
    class_id="cleric",
    level=17,
    description="Destroy Undead now affects undead of CR 4 or lower.",
    feature_type="passive",
    mechanic={"type": "destroy_undead", "cr_threshold": 4},
))

_f(ClassFeature(
    id="cleric_divine_intervention",
    name="Divine Intervention",
    class_id="cleric",
    level=10,
    description=(
        "You can call on your deity to intervene on your behalf. Roll percentile "
        "dice. If you roll a number equal to or lower than your cleric level, your "
        "deity intervenes. If successful, you can't use this again for 7 days."
    ),
    feature_type="active",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "divine_intervention", "success_threshold": "cleric_level_percent"},
))

_f(ClassFeature(
    id="cleric_channel_divinity_18",
    name="Channel Divinity (3/rest)",
    class_id="cleric",
    level=18,
    description="You can use Channel Divinity three times between rests.",
    feature_type="passive",
    mechanic={"type": "resource_upgrade", "resource": "channel_divinity", "uses": 3},
))

_f(ClassFeature(
    id="cleric_divine_intervention_20",
    name="Divine Intervention Improvement",
    class_id="cleric",
    level=20,
    description="Your call for divine intervention automatically succeeds, no roll required.",
    feature_type="active",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "divine_intervention", "auto_success": True},
))

_asi("cleric", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  DRUID
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="druid_druidic",
    name="Druidic",
    class_id="druid",
    level=1,
    description=(
        "You know Druidic, the secret language of druids. You can speak and leave "
        "hidden messages in this language."
    ),
    feature_type="passive",
    mechanic={"type": "language", "language": "Druidic"},
))

_f(ClassFeature(
    id="druid_spellcasting",
    name="Spellcasting",
    class_id="druid",
    level=1,
    description="Drawing on the divine essence of nature itself, you can cast spells to shape that essence to your will.",
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "WIS", "caster_type": "full", "prepared": True},
))

_f(ClassFeature(
    id="druid_wild_shape",
    name="Wild Shape",
    class_id="druid",
    level=2,
    description=(
        "You can use your action to magically assume the shape of a beast you have "
        "seen before. You can use this feature twice per short rest. Max CR and "
        "limitations improve as you level."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=2,
    mechanic={
        "type": "wild_shape",
        "max_cr": 0.25,
        "limitations": ["no_flying", "no_swimming"],
        "duration_hours": 1,
        "scaling": {
            4: {"max_cr": 0.5, "limitations": ["no_flying"]},
            8: {"max_cr": 1, "limitations": []},
        },
    },
))

_f(ClassFeature(
    id="druid_timeless_body",
    name="Timeless Body",
    class_id="druid",
    level=18,
    description="The primal magic causes you to age more slowly. For every 10 years that pass, your body ages only 1 year.",
    feature_type="passive",
    mechanic={"type": "aging_resistance", "ratio": 10},
))

_f(ClassFeature(
    id="druid_beast_spells",
    name="Beast Spells",
    class_id="druid",
    level=18,
    description="You can cast many of your druid spells in any shape you assume using Wild Shape. You can perform the somatic and verbal components while in beast form.",
    feature_type="passive",
    mechanic={"type": "wild_shape_modifier", "can_cast": True},
))

_f(ClassFeature(
    id="druid_archdruid",
    name="Archdruid",
    class_id="druid",
    level=20,
    description=(
        "You can use your Wild Shape an unlimited number of times. Additionally, you "
        "can ignore the verbal and somatic components of your druid spells as well as "
        "any material components that lack a cost and aren't consumed."
    ),
    feature_type="passive",
    mechanic={
        "type": "wild_shape_modifier",
        "unlimited_uses": True,
        "ignore_components": ["verbal", "somatic", "material_no_cost"],
    },
))

_asi("druid", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  FIGHTER
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="fighter_fighting_style",
    name="Fighting Style",
    class_id="fighter",
    level=1,
    description=(
        "You adopt a particular style of fighting as your specialty. Choose one: "
        "Archery, Defense, Dueling, Great Weapon Fighting, Protection, Two-Weapon Fighting."
    ),
    feature_type="passive",
    mechanic={
        "type": "fighting_style",
        "options": ["archery", "defense", "dueling", "great_weapon", "protection", "two_weapon"],
    },
))

_f(ClassFeature(
    id="fighter_second_wind",
    name="Second Wind",
    class_id="fighter",
    level=1,
    description=(
        "You have a limited well of stamina. On your turn, you can use a bonus action "
        "to regain HP equal to 1d10 + your fighter level."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=1,
    mechanic={"type": "self_heal", "dice": "1d10", "bonus": "fighter_level"},
))

_f(ClassFeature(
    id="fighter_action_surge",
    name="Action Surge",
    class_id="fighter",
    level=2,
    description=(
        "You can push yourself beyond your normal limits. On your turn, you can take "
        "one additional action. Once you use this feature, you must finish a short or "
        "long rest before you can use it again."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=1,
    mechanic={
        "type": "extra_action",
        "scaling": {17: {"uses": 2}},
    },
))

_f(ClassFeature(
    id="fighter_extra_attack_5",
    name="Extra Attack",
    class_id="fighter",
    level=5,
    description="You can attack twice, instead of once, whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 2},
))

_f(ClassFeature(
    id="fighter_indomitable_9",
    name="Indomitable (1 use)",
    class_id="fighter",
    level=9,
    description="You can reroll a saving throw that you fail. You must use the new roll.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "save_reroll"},
))

_f(ClassFeature(
    id="fighter_extra_attack_11",
    name="Extra Attack (2)",
    class_id="fighter",
    level=11,
    description="You can attack three times whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 3},
))

_f(ClassFeature(
    id="fighter_indomitable_13",
    name="Indomitable (2 uses)",
    class_id="fighter",
    level=13,
    description="You can use Indomitable twice between long rests.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=2,
    mechanic={"type": "save_reroll", "uses": 2},
))

_f(ClassFeature(
    id="fighter_indomitable_17",
    name="Indomitable (3 uses)",
    class_id="fighter",
    level=17,
    description="You can use Indomitable three times between long rests.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=3,
    mechanic={"type": "save_reroll", "uses": 3},
))

_f(ClassFeature(
    id="fighter_action_surge_17",
    name="Action Surge (2 uses)",
    class_id="fighter",
    level=17,
    description="You can use Action Surge twice between rests, but only once on the same turn.",
    feature_type="passive",
    mechanic={"type": "resource_upgrade", "resource": "action_surge", "uses": 2},
))

_f(ClassFeature(
    id="fighter_extra_attack_20",
    name="Extra Attack (3)",
    class_id="fighter",
    level=20,
    description="You can attack four times whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 4},
))

_asi("fighter", [4, 6, 8, 12, 14, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  MONK
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="monk_unarmored_defense",
    name="Unarmored Defense",
    class_id="monk",
    level=1,
    description=(
        "While you are wearing no armor and not wielding a shield, your AC equals "
        "10 + DEX modifier + WIS modifier."
    ),
    feature_type="passive",
    mechanic={"type": "ac_formula", "formula": "10 + DEX + WIS", "allows_shield": False},
))

_f(ClassFeature(
    id="monk_martial_arts",
    name="Martial Arts",
    class_id="monk",
    level=1,
    description=(
        "Your practice of martial arts gives you mastery of combat styles that use "
        "unarmed strikes and monk weapons. You gain benefits: use DEX for unarmed/monk "
        "weapons, roll a d4 in place of normal damage, make bonus unarmed strike."
    ),
    feature_type="passive",
    mechanic={
        "type": "martial_arts",
        "die": "d4",
        "bonus_unarmed_strike": True,
        "use_dex": True,
        "scaling": {
            5: {"die": "d6"},
            11: {"die": "d8"},
            17: {"die": "d10"},
        },
    },
))

_f(ClassFeature(
    id="monk_ki",
    name="Ki",
    class_id="monk",
    level=2,
    description=(
        "Your training allows you to harness the mystic energy of ki. You have a "
        "number of ki points equal to your monk level. You can spend these points "
        "to fuel ki features: Flurry of Blows, Patient Defense, Step of the Wind."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=2,  # equals monk level
    mechanic={
        "type": "resource_pool",
        "points": "monk_level",
        "options": ["flurry_of_blows", "patient_defense", "step_of_the_wind"],
        "save_dc": "8 + proficiency + WIS",
    },
))

_f(ClassFeature(
    id="monk_unarmored_movement",
    name="Unarmored Movement",
    class_id="monk",
    level=2,
    description="Your speed increases by 10 feet while you are not wearing armor or wielding a shield.",
    feature_type="passive",
    mechanic={
        "type": "speed_bonus",
        "bonus": 10,
        "condition": "unarmored_no_shield",
        "scaling": {
            6: {"bonus": 15}, 10: {"bonus": 20},
            14: {"bonus": 25}, 18: {"bonus": 30},
        },
    },
))

_f(ClassFeature(
    id="monk_deflect_missiles",
    name="Deflect Missiles",
    class_id="monk",
    level=3,
    description=(
        "You can use your reaction to deflect or catch the missile when you are hit "
        "by a ranged weapon attack. Reduce damage by 1d10 + DEX mod + monk level. "
        "If reduced to 0, you can catch and throw it back (1 ki point)."
    ),
    feature_type="reaction",
    uses_per="at_will",
    mechanic={
        "type": "damage_reduction",
        "trigger": "ranged_weapon_hit",
        "reduction": "1d10 + DEX + monk_level",
        "can_return": True,
        "return_cost": 1,
    },
))

_f(ClassFeature(
    id="monk_slow_fall",
    name="Slow Fall",
    class_id="monk",
    level=4,
    description="You can use your reaction when you fall to reduce any falling damage you take by an amount equal to five times your monk level.",
    feature_type="reaction",
    uses_per="at_will",
    mechanic={"type": "damage_reduction", "trigger": "falling", "reduction": "5 * monk_level"},
))

_f(ClassFeature(
    id="monk_extra_attack",
    name="Extra Attack",
    class_id="monk",
    level=5,
    description="You can attack twice, instead of once, whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 2},
))

_f(ClassFeature(
    id="monk_stunning_strike",
    name="Stunning Strike",
    class_id="monk",
    level=5,
    description=(
        "You can interfere with the flow of ki in an opponent's body. When you hit "
        "a creature with a melee weapon attack, you can spend 1 ki point to attempt "
        "a stunning strike. The target must succeed on a CON save or be stunned."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "debuff",
        "cost": 1,
        "cost_resource": "ki",
        "save": "CON",
        "condition": "stunned",
        "duration": "end_of_your_next_turn",
    },
))

_f(ClassFeature(
    id="monk_ki_empowered_strikes",
    name="Ki-Empowered Strikes",
    class_id="monk",
    level=6,
    description="Your unarmed strikes count as magical for the purpose of overcoming resistance and immunity to nonmagical attacks.",
    feature_type="passive",
    mechanic={"type": "magical_attacks", "applies_to": "unarmed"},
))

_f(ClassFeature(
    id="monk_evasion",
    name="Evasion",
    class_id="monk",
    level=7,
    description=(
        "When you are subjected to an effect that allows you to make a DEX saving throw "
        "to take only half damage, you instead take no damage on success, and half on failure."
    ),
    feature_type="passive",
    mechanic={"type": "save_modifier", "ability": "DEX", "on_success": "no_damage", "on_fail": "half_damage"},
))

_f(ClassFeature(
    id="monk_stillness_of_mind",
    name="Stillness of Mind",
    class_id="monk",
    level=7,
    description="You can use your action to end one effect on yourself that is causing you to be charmed or frightened.",
    feature_type="active",
    uses_per="at_will",
    mechanic={"type": "condition_removal", "conditions": ["charmed", "frightened"]},
))

_f(ClassFeature(
    id="monk_purity_of_body",
    name="Purity of Body",
    class_id="monk",
    level=10,
    description="Your mastery of ki flowing through you makes you immune to disease and poison.",
    feature_type="passive",
    mechanic={"type": "immunity", "conditions": ["disease", "poisoned"], "damage_types": ["poison"]},
))

_f(ClassFeature(
    id="monk_tongue_of_sun_and_moon",
    name="Tongue of the Sun and Moon",
    class_id="monk",
    level=13,
    description="You learn to touch the ki of other minds so that you understand all spoken languages. Any creature that can understand a language can understand what you say.",
    feature_type="passive",
    mechanic={"type": "language", "language": "all_spoken"},
))

_f(ClassFeature(
    id="monk_diamond_soul",
    name="Diamond Soul",
    class_id="monk",
    level=14,
    description="You gain proficiency in all saving throws. Additionally, whenever you fail a saving throw, you can spend 1 ki point to reroll it.",
    feature_type="passive",
    mechanic={"type": "all_save_proficiency", "reroll_cost": 1, "reroll_resource": "ki"},
))

_f(ClassFeature(
    id="monk_timeless_body",
    name="Timeless Body",
    class_id="monk",
    level=15,
    description="Your ki sustains you so that you suffer none of the frailty of old age. You can still die of old age. You no longer need food or water.",
    feature_type="passive",
    mechanic={"type": "aging_immunity", "no_food_water": True},
))

_f(ClassFeature(
    id="monk_empty_body",
    name="Empty Body",
    class_id="monk",
    level=18,
    description=(
        "You can spend 4 ki points to become invisible for 1 minute and gain resistance "
        "to all damage except force. You can also spend 8 ki points to cast Astral "
        "Projection without material components."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "ki_ability",
        "options": [
            {"cost": 4, "effect": "invisible", "duration": "1 minute",
             "resistance": "all_except_force"},
            {"cost": 8, "effect": "astral_projection"},
        ],
    },
))

_f(ClassFeature(
    id="monk_perfect_self",
    name="Perfect Self",
    class_id="monk",
    level=20,
    description="When you roll initiative and have no ki points remaining, you regain 4 ki points.",
    feature_type="passive",
    mechanic={"type": "resource_recovery", "resource": "ki", "trigger": "initiative", "amount": 4},
))

_asi("monk", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  PALADIN
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="paladin_divine_sense",
    name="Divine Sense",
    class_id="paladin",
    level=1,
    description=(
        "As an action, you can detect the presence of any celestial, fiend, or "
        "undead within 60 feet, as well as any consecrated or desecrated place or "
        "object within the same range."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=None,  # 1 + CHA modifier
    mechanic={"type": "detection", "range": 60, "detects": ["celestial", "fiend", "undead"],
              "uses": "1 + CHA_mod"},
))

_f(ClassFeature(
    id="paladin_lay_on_hands",
    name="Lay on Hands",
    class_id="paladin",
    level=1,
    description=(
        "You have a pool of healing power that replenishes on a long rest. You can "
        "restore a total number of HP equal to your paladin level x 5. You can also "
        "expend 5 HP from the pool to cure a disease or neutralize a poison."
    ),
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "healing_pool", "pool": "paladin_level * 5", "cure_cost": 5},
))

_f(ClassFeature(
    id="paladin_fighting_style",
    name="Fighting Style",
    class_id="paladin",
    level=2,
    description="You adopt a particular style of fighting. Choose one: Defense, Dueling, Great Weapon Fighting, Protection.",
    feature_type="passive",
    mechanic={
        "type": "fighting_style",
        "options": ["defense", "dueling", "great_weapon", "protection"],
    },
))

_f(ClassFeature(
    id="paladin_spellcasting",
    name="Spellcasting",
    class_id="paladin",
    level=2,
    description="You have learned to draw on divine magic through meditation and prayer to cast spells.",
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "CHA", "caster_type": "half", "prepared": True},
))

_f(ClassFeature(
    id="paladin_divine_smite",
    name="Divine Smite",
    class_id="paladin",
    level=2,
    description=(
        "When you hit a creature with a melee weapon attack, you can expend one "
        "spell slot to deal radiant damage to the target, in addition to weapon "
        "damage. The extra damage is 2d8 for a 1st-level slot, plus 1d8 for each "
        "slot level higher than 1st, to a max of 5d8. +1d8 against undead/fiend."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "extra_damage",
        "base_dice": "2d8",
        "per_slot_level": "1d8",
        "max_dice": "5d8",
        "damage_type": "radiant",
        "bonus_vs": ["undead", "fiend"],
        "bonus_dice": "1d8",
        "cost": "spell_slot",
    },
))

_f(ClassFeature(
    id="paladin_divine_health",
    name="Divine Health",
    class_id="paladin",
    level=3,
    description="The divine magic flowing through you makes you immune to disease.",
    feature_type="passive",
    mechanic={"type": "immunity", "conditions": ["disease"]},
))

_f(ClassFeature(
    id="paladin_extra_attack",
    name="Extra Attack",
    class_id="paladin",
    level=5,
    description="You can attack twice, instead of once, whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 2},
))

_f(ClassFeature(
    id="paladin_aura_of_protection",
    name="Aura of Protection",
    class_id="paladin",
    level=6,
    description=(
        "Whenever you or a friendly creature within 10 feet of you must make a "
        "saving throw, the creature gains a bonus to the save equal to your CHA "
        "modifier (minimum +1). You must be conscious."
    ),
    feature_type="aura",
    mechanic={
        "type": "aura_save_bonus",
        "radius": 10,
        "bonus": "CHA_mod",
        "min_bonus": 1,
        "scaling": {18: {"radius": 30}},
    },
))

_f(ClassFeature(
    id="paladin_aura_of_courage",
    name="Aura of Courage",
    class_id="paladin",
    level=10,
    description="You and friendly creatures within 10 feet of you can't be frightened while you are conscious.",
    feature_type="aura",
    mechanic={
        "type": "aura_immunity",
        "radius": 10,
        "condition": "frightened",
        "scaling": {18: {"radius": 30}},
    },
))

_f(ClassFeature(
    id="paladin_improved_divine_smite",
    name="Improved Divine Smite",
    class_id="paladin",
    level=11,
    description="Whenever you hit a creature with a melee weapon, the creature takes an extra 1d8 radiant damage.",
    feature_type="passive",
    mechanic={"type": "extra_damage", "dice": "1d8", "damage_type": "radiant", "trigger": "melee_hit"},
))

_f(ClassFeature(
    id="paladin_cleansing_touch",
    name="Cleansing Touch",
    class_id="paladin",
    level=14,
    description="You can use your action to end one spell on yourself or on one willing creature that you touch. Uses equal to CHA modifier per long rest.",
    feature_type="active",
    uses_per="long_rest",
    uses_count=None,  # CHA modifier
    mechanic={"type": "spell_removal", "uses": "CHA_mod"},
))

_asi("paladin", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  RANGER
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="ranger_favored_enemy_1",
    name="Favored Enemy",
    class_id="ranger",
    level=1,
    description=(
        "You have significant experience studying, tracking, hunting, and even "
        "talking to a certain type of enemy. Choose a type of favored enemy. You "
        "have advantage on WIS (Survival) checks to track them and INT checks to "
        "recall information about them. You also learn one language of your choice."
    ),
    feature_type="passive",
    mechanic={
        "type": "favored_enemy",
        "num_choices": 1,
        "advantage": ["survival_track", "int_recall"],
        "bonus_language": 1,
    },
))

_f(ClassFeature(
    id="ranger_natural_explorer_1",
    name="Natural Explorer",
    class_id="ranger",
    level=1,
    description=(
        "You are a master of navigating the natural world. Choose one type of "
        "favored terrain. You gain various benefits when traveling or foraging in "
        "that terrain."
    ),
    feature_type="passive",
    mechanic={"type": "favored_terrain", "num_choices": 1},
))

_f(ClassFeature(
    id="ranger_fighting_style",
    name="Fighting Style",
    class_id="ranger",
    level=2,
    description="You adopt a particular style of fighting. Choose one: Archery, Defense, Dueling, Two-Weapon Fighting.",
    feature_type="passive",
    mechanic={
        "type": "fighting_style",
        "options": ["archery", "defense", "dueling", "two_weapon"],
    },
))

_f(ClassFeature(
    id="ranger_spellcasting",
    name="Spellcasting",
    class_id="ranger",
    level=2,
    description="You have learned to use the magical essence of nature to cast spells, much as a druid does.",
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "WIS", "caster_type": "half"},
))

_f(ClassFeature(
    id="ranger_primeval_awareness",
    name="Primeval Awareness",
    class_id="ranger",
    level=3,
    description=(
        "You can use your action and expend one ranger spell slot to focus your "
        "awareness on the region around you. You can sense whether aberrations, "
        "celestials, dragons, elementals, fey, fiends, or undead are present within "
        "1 mile (6 miles in favored terrain)."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "detection",
        "range_miles": 1,
        "favored_terrain_range": 6,
        "detects": ["aberration", "celestial", "dragon", "elemental", "fey", "fiend", "undead"],
        "cost": "spell_slot",
    },
))

_f(ClassFeature(
    id="ranger_extra_attack",
    name="Extra Attack",
    class_id="ranger",
    level=5,
    description="You can attack twice, instead of once, whenever you take the Attack action on your turn.",
    feature_type="passive",
    mechanic={"type": "extra_attack", "attacks": 2},
))

_f(ClassFeature(
    id="ranger_favored_enemy_6",
    name="Favored Enemy (additional)",
    class_id="ranger",
    level=6,
    description="Choose an additional favored enemy and an associated language.",
    feature_type="passive",
    mechanic={"type": "favored_enemy", "num_choices": 1, "bonus_language": 1},
))

_f(ClassFeature(
    id="ranger_natural_explorer_6",
    name="Natural Explorer (additional)",
    class_id="ranger",
    level=6,
    description="Choose an additional favored terrain type.",
    feature_type="passive",
    mechanic={"type": "favored_terrain", "num_choices": 1},
))

_f(ClassFeature(
    id="ranger_lands_stride",
    name="Land's Stride",
    class_id="ranger",
    level=8,
    description=(
        "Moving through nonmagical difficult terrain costs you no extra movement. "
        "You can also pass through nonmagical plants without being slowed or taking "
        "damage. You have advantage on saves against magically created plants."
    ),
    feature_type="passive",
    mechanic={
        "type": "movement_modifier",
        "ignore_difficult_terrain": True,
        "ignore_plant_hazards": True,
        "advantage_vs": "magical_plants",
    },
))

_f(ClassFeature(
    id="ranger_natural_explorer_10",
    name="Natural Explorer (additional)",
    class_id="ranger",
    level=10,
    description="Choose an additional favored terrain type.",
    feature_type="passive",
    mechanic={"type": "favored_terrain", "num_choices": 1},
))

_f(ClassFeature(
    id="ranger_hide_in_plain_sight",
    name="Hide in Plain Sight",
    class_id="ranger",
    level=10,
    description=(
        "You can spend 1 minute creating camouflage for yourself. You gain a +10 "
        "bonus to DEX (Stealth) checks as long as you remain in place without moving."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={"type": "stealth_bonus", "bonus": 10, "condition": "stationary", "setup_time": "1 minute"},
))

_f(ClassFeature(
    id="ranger_favored_enemy_14",
    name="Favored Enemy (additional)",
    class_id="ranger",
    level=14,
    description="Choose an additional favored enemy and an associated language.",
    feature_type="passive",
    mechanic={"type": "favored_enemy", "num_choices": 1, "bonus_language": 1},
))

_f(ClassFeature(
    id="ranger_vanish",
    name="Vanish",
    class_id="ranger",
    level=14,
    description="You can use the Hide action as a bonus action on your turn. Also, you can't be tracked by nonmagical means unless you choose to leave a trail.",
    feature_type="passive",
    mechanic={"type": "bonus_action_hide", "untrackable": True},
))

_f(ClassFeature(
    id="ranger_feral_senses",
    name="Feral Senses",
    class_id="ranger",
    level=18,
    description=(
        "You gain preternatural senses. You have no disadvantage on attacks against "
        "creatures you can't see. You are aware of the location of any invisible "
        "creature within 30 feet if you aren't blinded or deafened."
    ),
    feature_type="passive",
    mechanic={
        "type": "blindsight_lite",
        "range": 30,
        "no_disadvantage_vs_unseen": True,
    },
))

_f(ClassFeature(
    id="ranger_foe_slayer",
    name="Foe Slayer",
    class_id="ranger",
    level=20,
    description=(
        "Once on each of your turns, you can add your WIS modifier to the attack "
        "roll or the damage roll of an attack you make against one of your favored "
        "enemies."
    ),
    feature_type="passive",
    mechanic={
        "type": "attack_bonus",
        "bonus": "WIS_mod",
        "applies_to": "attack_or_damage",
        "condition": "favored_enemy",
        "per_turn": 1,
    },
))

_asi("ranger", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  ROGUE
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="rogue_expertise_1",
    name="Expertise",
    class_id="rogue",
    level=1,
    description="Choose two of your skill proficiencies, or one skill and thieves' tools. Your proficiency bonus is doubled for those.",
    feature_type="passive",
    mechanic={"type": "expertise", "num_skills": 2},
))

_f(ClassFeature(
    id="rogue_sneak_attack_1",
    name="Sneak Attack (1d6)",
    class_id="rogue",
    level=1,
    description=(
        "Once per turn, you can deal extra damage to one creature you hit with an "
        "attack if you have advantage on the attack roll or if another enemy of the "
        "target is within 5 feet of it. The attack must use a finesse or ranged weapon."
    ),
    feature_type="passive",
    mechanic={
        "type": "extra_damage",
        "dice": "1d6",
        "condition": "advantage_or_ally_adjacent",
        "once_per_turn": True,
        "scaling": {
            3: {"dice": "2d6"}, 5: {"dice": "3d6"}, 7: {"dice": "4d6"},
            9: {"dice": "5d6"}, 11: {"dice": "6d6"}, 13: {"dice": "7d6"},
            15: {"dice": "8d6"}, 17: {"dice": "9d6"}, 19: {"dice": "10d6"},
        },
    },
))

_f(ClassFeature(
    id="rogue_thieves_cant",
    name="Thieves' Cant",
    class_id="rogue",
    level=1,
    description=(
        "You have learned thieves' cant, a secret mix of dialect, jargon, and code "
        "that allows you to hide messages in seemingly normal conversation."
    ),
    feature_type="passive",
    mechanic={"type": "language", "language": "Thieves' Cant"},
))

_f(ClassFeature(
    id="rogue_cunning_action",
    name="Cunning Action",
    class_id="rogue",
    level=2,
    description="You can take a bonus action on each of your turns to Dash, Disengage, or Hide.",
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "bonus_action_options",
        "options": ["dash", "disengage", "hide"],
    },
))

_f(ClassFeature(
    id="rogue_uncanny_dodge",
    name="Uncanny Dodge",
    class_id="rogue",
    level=5,
    description=(
        "When an attacker that you can see hits you with an attack, you can use your "
        "reaction to halve the attack's damage against you."
    ),
    feature_type="reaction",
    uses_per="at_will",
    mechanic={"type": "damage_reduction", "trigger": "attack_hit", "reduction": "half", "condition": "can_see_attacker"},
))

_f(ClassFeature(
    id="rogue_expertise_6",
    name="Expertise",
    class_id="rogue",
    level=6,
    description="Choose two more of your proficiencies (skills or thieves' tools) to gain expertise in.",
    feature_type="passive",
    mechanic={"type": "expertise", "num_skills": 2},
))

_f(ClassFeature(
    id="rogue_evasion",
    name="Evasion",
    class_id="rogue",
    level=7,
    description=(
        "When you are subjected to an effect that allows a DEX saving throw for half "
        "damage, you instead take no damage on success and half damage on failure."
    ),
    feature_type="passive",
    mechanic={"type": "save_modifier", "ability": "DEX", "on_success": "no_damage", "on_fail": "half_damage"},
))

_f(ClassFeature(
    id="rogue_reliable_talent",
    name="Reliable Talent",
    class_id="rogue",
    level=11,
    description=(
        "Whenever you make an ability check that lets you add your proficiency bonus, "
        "you can treat a d20 roll of 9 or lower as a 10."
    ),
    feature_type="passive",
    mechanic={"type": "roll_floor", "minimum": 10, "applies_to": "proficient_checks"},
))

_f(ClassFeature(
    id="rogue_blindsense",
    name="Blindsense",
    class_id="rogue",
    level=14,
    description="If you are able to hear, you are aware of the location of any hidden or invisible creature within 10 feet of you.",
    feature_type="passive",
    mechanic={"type": "blindsense", "range": 10, "condition": "can_hear"},
))

_f(ClassFeature(
    id="rogue_slippery_mind",
    name="Slippery Mind",
    class_id="rogue",
    level=15,
    description="You gain proficiency in WIS saving throws.",
    feature_type="passive",
    mechanic={"type": "save_proficiency", "ability": "WIS"},
))

_f(ClassFeature(
    id="rogue_elusive",
    name="Elusive",
    class_id="rogue",
    level=18,
    description="No attack roll has advantage against you while you aren't incapacitated.",
    feature_type="passive",
    mechanic={"type": "deny_advantage", "condition": "not_incapacitated"},
))

_f(ClassFeature(
    id="rogue_stroke_of_luck",
    name="Stroke of Luck",
    class_id="rogue",
    level=20,
    description=(
        "You have an uncanny knack for succeeding when you need to. If your attack "
        "misses, you can turn it into a hit. Alternatively, if you fail an ability "
        "check, you can treat the d20 roll as a 20."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=1,
    mechanic={"type": "auto_success", "applies_to": ["attack", "ability_check"]},
))

_asi("rogue", [4, 8, 10, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  SORCERER
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="sorcerer_spellcasting",
    name="Spellcasting",
    class_id="sorcerer",
    level=1,
    description="An event in your past, or in the life of a parent or ancestor, left an indelible mark on you, infusing you with arcane magic.",
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "CHA", "caster_type": "full"},
))

_f(ClassFeature(
    id="sorcerer_sorcery_points",
    name="Sorcery Points",
    class_id="sorcerer",
    level=2,
    description=(
        "You have a wellspring of magic represented by sorcery points. You have "
        "a number of sorcery points equal to your sorcerer level. You can use them "
        "to gain additional spell slots or fuel Metamagic."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=2,  # equals sorcerer level
    mechanic={"type": "resource_pool", "points": "sorcerer_level"},
))

_f(ClassFeature(
    id="sorcerer_flexible_casting",
    name="Flexible Casting",
    class_id="sorcerer",
    level=2,
    description=(
        "You can use sorcery points to create spell slots, or sacrifice spell slots "
        "to gain sorcery points. Creating a 1st-level slot costs 2 points; a "
        "2nd-level 3 points; a 3rd-level 5 points; a 4th-level 6 points; a "
        "5th-level 7 points."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "resource_conversion",
        "slot_to_points": {1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        "points_to_slot": {1: 2, 2: 3, 3: 5, 4: 6, 5: 7},
        "max_created_slot": 5,
    },
))

_f(ClassFeature(
    id="sorcerer_metamagic_3",
    name="Metamagic",
    class_id="sorcerer",
    level=3,
    description=(
        "You gain the ability to twist your spells to suit your needs. You gain two "
        "Metamagic options of your choice."
    ),
    feature_type="active",
    uses_per="at_will",
    mechanic={
        "type": "metamagic",
        "num_choices": 2,
        "options": [
            "careful", "distant", "empowered", "extended",
            "heightened", "quickened", "subtle", "twinned",
        ],
    },
))

_f(ClassFeature(
    id="sorcerer_metamagic_10",
    name="Metamagic (additional)",
    class_id="sorcerer",
    level=10,
    description="You learn one additional Metamagic option.",
    feature_type="passive",
    mechanic={"type": "metamagic", "num_choices": 1},
))

_f(ClassFeature(
    id="sorcerer_metamagic_17",
    name="Metamagic (additional)",
    class_id="sorcerer",
    level=17,
    description="You learn one additional Metamagic option.",
    feature_type="passive",
    mechanic={"type": "metamagic", "num_choices": 1},
))

_asi("sorcerer", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  WARLOCK
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="warlock_pact_magic",
    name="Pact Magic",
    class_id="warlock",
    level=1,
    description=(
        "Your arcane research and the magic bestowed on you by your patron have given "
        "you facility with spells. Your spell slots refresh on a short rest."
    ),
    feature_type="resource",
    uses_per="short_rest",
    mechanic={"type": "spellcasting", "ability": "CHA", "caster_type": "pact"},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_2",
    name="Eldritch Invocations (2)",
    class_id="warlock",
    level=2,
    description=(
        "In your study of occult lore, you have unearthed eldritch invocations, "
        "fragments of forbidden knowledge that imbue you with abiding magical ability. "
        "You gain two invocations of your choice."
    ),
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 2},
))

_f(ClassFeature(
    id="warlock_pact_boon",
    name="Pact Boon",
    class_id="warlock",
    level=3,
    description=(
        "Your otherworldly patron bestows a gift upon you for your loyal service. "
        "Choose one: Pact of the Chain, Pact of the Blade, or Pact of the Tome."
    ),
    feature_type="passive",
    mechanic={
        "type": "pact_boon",
        "options": ["chain", "blade", "tome"],
    },
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_5",
    name="Eldritch Invocations (3)",
    class_id="warlock",
    level=5,
    description="You learn one additional eldritch invocation (3 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 3},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_7",
    name="Eldritch Invocations (4)",
    class_id="warlock",
    level=7,
    description="You learn one additional eldritch invocation (4 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 4},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_9",
    name="Eldritch Invocations (5)",
    class_id="warlock",
    level=9,
    description="You learn one additional eldritch invocation (5 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 5},
))

_f(ClassFeature(
    id="warlock_mystic_arcanum_11",
    name="Mystic Arcanum (6th level)",
    class_id="warlock",
    level=11,
    description="Your patron bestows upon you a magical secret called an arcanum. Choose one 6th-level spell. You can cast it once without expending a spell slot. You regain this ability on a long rest.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "mystic_arcanum", "spell_level": 6},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_12",
    name="Eldritch Invocations (6)",
    class_id="warlock",
    level=12,
    description="You learn one additional eldritch invocation (6 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 6},
))

_f(ClassFeature(
    id="warlock_mystic_arcanum_13",
    name="Mystic Arcanum (7th level)",
    class_id="warlock",
    level=13,
    description="Choose one 7th-level spell as a mystic arcanum.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "mystic_arcanum", "spell_level": 7},
))

_f(ClassFeature(
    id="warlock_mystic_arcanum_15",
    name="Mystic Arcanum (8th level)",
    class_id="warlock",
    level=15,
    description="Choose one 8th-level spell as a mystic arcanum.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "mystic_arcanum", "spell_level": 8},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_15",
    name="Eldritch Invocations (7)",
    class_id="warlock",
    level=15,
    description="You learn one additional eldritch invocation (7 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 7},
))

_f(ClassFeature(
    id="warlock_mystic_arcanum_17",
    name="Mystic Arcanum (9th level)",
    class_id="warlock",
    level=17,
    description="Choose one 9th-level spell as a mystic arcanum.",
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "mystic_arcanum", "spell_level": 9},
))

_f(ClassFeature(
    id="warlock_eldritch_invocations_18",
    name="Eldritch Invocations (8)",
    class_id="warlock",
    level=18,
    description="You learn one additional eldritch invocation (8 total).",
    feature_type="passive",
    mechanic={"type": "invocations", "num_known": 8},
))

_f(ClassFeature(
    id="warlock_eldritch_master",
    name="Eldritch Master",
    class_id="warlock",
    level=20,
    description=(
        "You can draw on your inner reserve of mystical power while entreating your "
        "patron. You can spend 1 minute entreating your patron to regain all your "
        "expended spell slots from Pact Magic."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={"type": "resource_recovery", "resource": "pact_magic_slots", "recovery": "all"},
))

_asi("warlock", [4, 8, 12, 16, 19])


# ═══════════════════════════════════════════════════════════════════════════
#  WIZARD
# ═══════════════════════════════════════════════════════════════════════════

_f(ClassFeature(
    id="wizard_spellcasting",
    name="Spellcasting",
    class_id="wizard",
    level=1,
    description=(
        "As a student of arcane magic, you have a spellbook containing spells that "
        "show the first glimmerings of your true power."
    ),
    feature_type="resource",
    uses_per="long_rest",
    mechanic={"type": "spellcasting", "ability": "INT", "caster_type": "full", "spellbook": True, "prepared": True},
))

_f(ClassFeature(
    id="wizard_arcane_recovery",
    name="Arcane Recovery",
    class_id="wizard",
    level=1,
    description=(
        "Once per day when you finish a short rest, you can recover expended spell "
        "slots. The spell slots can have a combined level equal to or less than half "
        "your wizard level (rounded up), and none can be 6th level or higher."
    ),
    feature_type="resource",
    uses_per="long_rest",
    uses_count=1,
    mechanic={
        "type": "slot_recovery",
        "max_total_level": "ceil(wizard_level / 2)",
        "max_slot_level": 5,
        "trigger": "short_rest",
    },
))

_f(ClassFeature(
    id="wizard_spell_mastery",
    name="Spell Mastery",
    class_id="wizard",
    level=18,
    description=(
        "You have achieved mastery over certain spells. Choose a 1st-level and a "
        "2nd-level spell in your spellbook. You can cast them at their lowest level "
        "without expending a spell slot when you have them prepared."
    ),
    feature_type="passive",
    mechanic={
        "type": "at_will_spells",
        "choices": [{"level": 1, "count": 1}, {"level": 2, "count": 1}],
    },
))

_f(ClassFeature(
    id="wizard_signature_spells",
    name="Signature Spells",
    class_id="wizard",
    level=20,
    description=(
        "You gain mastery over two powerful spells. Choose two 3rd-level spells in "
        "your spellbook. You always have them prepared, they don't count against "
        "prepared spells, and you can cast each once at 3rd level without expending "
        "a slot. You regain the ability to do so on a short or long rest."
    ),
    feature_type="resource",
    uses_per="short_rest",
    uses_count=2,
    mechanic={
        "type": "signature_spells",
        "spell_level": 3,
        "count": 2,
        "always_prepared": True,
        "free_cast": True,
    },
))

_asi("wizard", [4, 8, 12, 16, 19])
