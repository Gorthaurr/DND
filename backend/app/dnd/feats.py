"""D&D 5e feats — SRD feats plus popular commonly-used feats with mechanical effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Feat:
    id: str
    name: str
    prerequisite: str | None  # e.g. "STR 13", "Spellcasting", None
    description: str
    mechanic: dict[str, Any] | None  # machine-readable game effect


# ── Registry ──

FEATS: dict[str, Feat] = {}


def _f(f: Feat) -> None:
    """Register a feat in the global registry."""
    FEATS[f.id] = f


# ═══════════════════════════════════════════════════════════════
#  1. Alert
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="alert",
    name="Alert",
    prerequisite=None,
    description=(
        "Always on the lookout for danger. You gain +5 to initiative, "
        "you can't be surprised while conscious, and other creatures don't "
        "gain advantage on attack rolls against you as a result of being unseen."
    ),
    mechanic={
        "initiative_bonus": 5,
        "immune_surprise": True,
        "hidden_no_advantage": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  2. Athlete
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="athlete",
    name="Athlete",
    prerequisite=None,
    description=(
        "You have undergone extensive physical training. Increase STR or DEX by 1. "
        "Standing up from prone costs only 5 feet of movement. Climbing doesn't cost "
        "extra movement. You can make a running long jump with only a 5-foot running start."
    ),
    mechanic={
        "ability_increase": {"choice": ["STR", "DEX"], "amount": 1},
        "prone_stand_cost": 5,
        "climbing_no_extra_cost": True,
        "running_long_jump_start": 5,
    },
))

# ═══════════════════════════════════════════════════════════════
#  3. Actor
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="actor",
    name="Actor",
    prerequisite=None,
    description=(
        "Skilled at mimicry and dramatics. Increase CHA by 1. You have advantage "
        "on Deception and Performance checks when trying to pass yourself off as "
        "a different person. You can mimic the speech of another creature you have "
        "heard speak for at least 1 minute."
    ),
    mechanic={
        "ability_increase": {"ability": "CHA", "amount": 1},
        "advantage": ["deception_disguise", "performance_disguise"],
        "mimic_speech": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  4. Charger
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="charger",
    name="Charger",
    prerequisite=None,
    description=(
        "When you use your action to Dash, you can use a bonus action to make one "
        "melee weapon attack or to shove a creature. If you move at least 10 feet "
        "in a straight line before the attack, you gain +5 to the damage roll or "
        "push the target up to 10 feet away."
    ),
    mechanic={
        "trigger": "dash_action",
        "bonus_action": ["melee_attack", "shove"],
        "min_straight_move": 10,
        "damage_bonus": 5,
        "shove_distance": 10,
    },
))

# ═══════════════════════════════════════════════════════════════
#  5. Crossbow Expert
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="crossbow-expert",
    name="Crossbow Expert",
    prerequisite=None,
    description=(
        "Thanks to extensive practice with crossbows, you ignore the loading "
        "property of crossbows you are proficient with. Being within 5 feet of a "
        "hostile creature doesn't impose disadvantage on your ranged attack rolls. "
        "When you use the Attack action with a one-handed weapon, you can use a "
        "bonus action to attack with a hand crossbow you are holding."
    ),
    mechanic={
        "ignore_loading": True,
        "no_melee_ranged_disadvantage": True,
        "bonus_action_hand_crossbow": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  6. Defensive Duelist
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="defensive-duelist",
    name="Defensive Duelist",
    prerequisite="DEX 13",
    description=(
        "When you are wielding a finesse weapon with which you are proficient "
        "and another creature hits you with a melee attack, you can use your "
        "reaction to add your proficiency bonus to your AC for that attack, "
        "potentially causing the attack to miss."
    ),
    mechanic={
        "trigger": "hit_by_melee",
        "reaction": True,
        "ac_bonus": "proficiency_bonus",
        "requires_finesse_weapon": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  7. Dual Wielder
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="dual-wielder",
    name="Dual Wielder",
    prerequisite=None,
    description=(
        "You master fighting with two weapons. You gain +1 bonus to AC while "
        "wielding a separate melee weapon in each hand. You can use two-weapon "
        "fighting even when the weapons aren't light. You can draw or stow two "
        "one-handed weapons when you would normally be able to draw or stow only one."
    ),
    mechanic={
        "ac_bonus_dual_wield": 1,
        "non_light_two_weapon_fighting": True,
        "draw_stow_two": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  8. Dungeon Delver
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="dungeon-delver",
    name="Dungeon Delver",
    prerequisite=None,
    description=(
        "Alert to hidden traps and secret doors. You have advantage on Perception "
        "and Investigation checks to detect secret doors. You have advantage on "
        "saving throws to avoid or resist traps. You have resistance to trap damage. "
        "Traveling at a fast pace doesn't impose a penalty on passive Perception."
    ),
    mechanic={
        "advantage": ["perception_secret_doors", "investigation_secret_doors"],
        "advantage_saves_vs_traps": True,
        "resistance_trap_damage": True,
        "fast_pace_no_perception_penalty": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  9. Durable
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="durable",
    name="Durable",
    prerequisite=None,
    description=(
        "Hardy and resilient. Increase CON by 1. When you roll a Hit Die to "
        "regain hit points, the minimum number of hit points you regain equals "
        "twice your Constitution modifier (minimum of 2)."
    ),
    mechanic={
        "ability_increase": {"ability": "CON", "amount": 1},
        "hit_die_min_heal": "2 * CON_mod",
    },
))

# ═══════════════════════════════════════════════════════════════
#  10. Elemental Adept
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="elemental-adept",
    name="Elemental Adept",
    prerequisite="Spellcasting",
    description=(
        "You have mastered a damage type. Choose acid, cold, fire, lightning, or "
        "thunder. Spells you cast ignore resistance to that type. When you roll "
        "damage of the chosen type, you can treat any 1 on a damage die as a 2. "
        "You can take this feat multiple times, choosing a different element each time."
    ),
    mechanic={
        "choose_element": ["acid", "cold", "fire", "lightning", "thunder"],
        "ignore_resistance": True,
        "min_damage_die": 2,
        "repeatable": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  11. Grappler
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="grappler",
    name="Grappler",
    prerequisite="STR 13",
    description=(
        "You've developed the skills to hold your own in close-quarters grappling. "
        "You have advantage on attack rolls against a creature you are grappling. "
        "You can use your action to try to pin a creature you have grappled. On "
        "success, both you and the creature are restrained until the grapple ends."
    ),
    mechanic={
        "advantage_vs_grappled": True,
        "pin_action": True,
        "pin_effect": "both_restrained",
    },
))

# ═══════════════════════════════════════════════════════════════
#  12. Great Weapon Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="great-weapon-master",
    name="Great Weapon Master",
    prerequisite=None,
    description=(
        "You've learned to put the weight of a weapon to your advantage. On your "
        "turn, when you score a critical hit or reduce a creature to 0 HP with a "
        "melee weapon, you can make one melee weapon attack as a bonus action. "
        "Before you make a melee attack with a heavy weapon you are proficient "
        "with, you can choose to take -5 to the attack roll. If the attack hits, "
        "you add +10 to the damage."
    ),
    mechanic={
        "bonus_attack_on_crit_or_kill": True,
        "power_attack": {"attack_penalty": -5, "damage_bonus": 10},
        "requires_heavy_weapon": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  13. Healer
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="healer",
    name="Healer",
    prerequisite=None,
    description=(
        "You are an able physician. When you use a healer's kit to stabilize a "
        "dying creature, that creature also regains 1 hit point. As an action, "
        "you can spend one use of a healer's kit to tend to a creature and restore "
        "1d6 + 4 + the creature's number of Hit Dice hit points. A creature can "
        "only benefit from this once per short or long rest."
    ),
    mechanic={
        "stabilize_restores_hp": 1,
        "heal_action": {"dice": "1d6", "flat": 4, "bonus": "target_hit_dice"},
        "once_per_rest": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  14. Heavy Armor Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="heavy-armor-master",
    name="Heavy Armor Master",
    prerequisite="Heavy Armor Proficiency",
    description=(
        "You can use your armor to deflect strikes. Increase STR by 1. While "
        "wearing heavy armor, bludgeoning, piercing, and slashing damage that "
        "you take from nonmagical weapons is reduced by 3."
    ),
    mechanic={
        "ability_increase": {"ability": "STR", "amount": 1},
        "damage_reduction": {
            "amount": 3,
            "types": ["bludgeoning", "piercing", "slashing"],
            "condition": "nonmagical",
        },
        "requires_heavy_armor": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  15. Inspiring Leader
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="inspiring-leader",
    name="Inspiring Leader",
    prerequisite="CHA 13",
    description=(
        "You can spend 10 minutes inspiring your companions. Up to 6 friendly "
        "creatures (including yourself) who can see or hear you gain temporary "
        "hit points equal to your level + your Charisma modifier. A creature "
        "can't gain temporary hit points from this feat again until it finishes "
        "a short or long rest."
    ),
    mechanic={
        "speech_duration_minutes": 10,
        "max_targets": 6,
        "temp_hp": "level + CHA_mod",
        "once_per_rest": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  16. Keen Mind
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="keen-mind",
    name="Keen Mind",
    prerequisite=None,
    description=(
        "You have a mind that can track time, direction, and detail with "
        "uncanny precision. Increase INT by 1. You always know which way is "
        "north. You always know the number of hours left before the next "
        "sunrise or sunset. You can accurately recall anything you have seen "
        "or heard within the past month."
    ),
    mechanic={
        "ability_increase": {"ability": "INT", "amount": 1},
        "always_know_north": True,
        "always_know_time": True,
        "perfect_recall_days": 30,
    },
))

# ═══════════════════════════════════════════════════════════════
#  17. Linguist
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="linguist",
    name="Linguist",
    prerequisite=None,
    description=(
        "You have studied languages and codes. Increase INT by 1. You learn "
        "three languages of your choice. You can ably create written ciphers. "
        "Others can't decipher a code you create unless you teach them, they "
        "succeed on an INT check (DC = your INT score + proficiency bonus), "
        "or they use magic."
    ),
    mechanic={
        "ability_increase": {"ability": "INT", "amount": 1},
        "languages": 3,
        "create_ciphers": True,
        "cipher_dc": "INT_score + proficiency_bonus",
    },
))

# ═══════════════════════════════════════════════════════════════
#  18. Lucky
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="lucky",
    name="Lucky",
    prerequisite=None,
    description=(
        "You have inexplicable luck. You have 3 luck points. Whenever you make "
        "an attack roll, ability check, or saving throw, you can spend one luck "
        "point to roll an additional d20 and choose which to use. You can also "
        "spend a luck point when an attack roll is made against you, rolling a "
        "d20 and choosing which roll the attacker uses. You regain all luck "
        "points on a long rest."
    ),
    mechanic={
        "luck_points": 3,
        "recharge": "long_rest",
        "applies_to": ["attack", "ability_check", "saving_throw", "enemy_attack"],
        "extra_d20_choose": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  19. Mage Slayer
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="mage-slayer",
    name="Mage Slayer",
    prerequisite=None,
    description=(
        "You have practiced techniques useful in melee combat against "
        "spellcasters. When a creature within 5 feet casts a spell, you can "
        "use your reaction to make a melee weapon attack against that creature. "
        "When you damage a creature concentrating on a spell, it has "
        "disadvantage on the saving throw to maintain concentration. You have "
        "advantage on saving throws against spells cast by creatures within "
        "5 feet of you."
    ),
    mechanic={
        "reaction_attack_on_cast": True,
        "range": 5,
        "impose_concentration_disadvantage": True,
        "advantage_saves_vs_adjacent_casters": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  20. Magic Initiate
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="magic-initiate",
    name="Magic Initiate",
    prerequisite=None,
    description=(
        "Choose a class: bard, cleric, druid, sorcerer, warlock, or wizard. "
        "You learn two cantrips of your choice from that class's spell list. "
        "In addition, choose one 1st-level spell from that same list. You can "
        "cast that spell once at its lowest level without expending a spell slot; "
        "you regain this ability after a long rest."
    ),
    mechanic={
        "choose_class": ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"],
        "cantrips": 2,
        "level_1_spell": 1,
        "free_cast_recharge": "long_rest",
    },
))

# ═══════════════════════════════════════════════════════════════
#  21. Martial Adept
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="martial-adept",
    name="Martial Adept",
    prerequisite=None,
    description=(
        "You have martial training that allows you to perform special combat "
        "maneuvers. You learn two maneuvers of your choice from the Battle "
        "Master archetype. You gain one superiority die (a d6). This die is "
        "used to fuel your maneuvers and is expended when you use it. You "
        "regain it on a short or long rest."
    ),
    mechanic={
        "maneuvers": 2,
        "superiority_dice": {"count": 1, "die": "d6"},
        "recharge": "short_rest",
    },
))

# ═══════════════════════════════════════════════════════════════
#  22. Medium Armor Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="medium-armor-master",
    name="Medium Armor Master",
    prerequisite="Medium Armor Proficiency",
    description=(
        "You have practiced moving in medium armor. Wearing medium armor "
        "doesn't impose disadvantage on your Stealth checks. When you wear "
        "medium armor, you can add up to 3 (rather than 2) from your "
        "Dexterity modifier to your AC."
    ),
    mechanic={
        "no_stealth_disadvantage_medium": True,
        "max_dex_bonus_medium": 3,
    },
))

# ═══════════════════════════════════════════════════════════════
#  23. Mobile
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="mobile",
    name="Mobile",
    prerequisite=None,
    description=(
        "You are exceptionally speedy and agile. Your speed increases by 10 feet. "
        "When you use the Dash action, difficult terrain doesn't cost you extra "
        "movement. When you make a melee attack against a creature, you don't "
        "provoke opportunity attacks from that creature for the rest of the turn, "
        "whether you hit or not."
    ),
    mechanic={
        "speed_bonus": 10,
        "dash_ignore_difficult_terrain": True,
        "no_opportunity_attack_on_melee_target": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  24. Moderately Armored
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="moderately-armored",
    name="Moderately Armored",
    prerequisite="Light Armor Proficiency",
    description=(
        "You have trained with medium armor and shields. Increase STR or DEX by 1. "
        "You gain proficiency with medium armor and shields."
    ),
    mechanic={
        "ability_increase": {"choice": ["STR", "DEX"], "amount": 1},
        "proficiency_grant": ["medium_armor", "shields"],
    },
))

# ═══════════════════════════════════════════════════════════════
#  25. Mounted Combatant
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="mounted-combatant",
    name="Mounted Combatant",
    prerequisite=None,
    description=(
        "You are a dangerous foe to face while mounted. You have advantage on "
        "melee attack rolls against any unmounted creature smaller than your mount. "
        "You can force an attack targeting your mount to target you instead. If "
        "your mount is subjected to an effect that allows a DEX save for half "
        "damage, it takes no damage on success and half damage on failure."
    ),
    mechanic={
        "advantage_vs_smaller_unmounted": True,
        "redirect_attack_from_mount": True,
        "mount_evasion": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  26. Observant
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="observant",
    name="Observant",
    prerequisite=None,
    description=(
        "Quick to notice details of your environment. Increase INT or WIS by 1. "
        "If you can see a creature's mouth while it is speaking a language you "
        "understand, you can interpret what it's saying by reading its lips. "
        "You have a +5 bonus to your passive Perception and passive Investigation."
    ),
    mechanic={
        "ability_increase": {"choice": ["INT", "WIS"], "amount": 1},
        "lip_reading": True,
        "passive_perception_bonus": 5,
        "passive_investigation_bonus": 5,
    },
))

# ═══════════════════════════════════════════════════════════════
#  27. Polearm Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="polearm-master",
    name="Polearm Master",
    prerequisite=None,
    description=(
        "You can keep enemies at bay with reach weapons. When you take the "
        "Attack action with a glaive, halberd, quarterstaff, or spear, you "
        "can use a bonus action to make a melee attack with the opposite end "
        "(1d4 bludgeoning). While wielding such a weapon, other creatures "
        "provoke an opportunity attack from you when they enter your reach."
    ),
    mechanic={
        "bonus_action_butt_attack": {"die": "1d4", "type": "bludgeoning"},
        "opportunity_attack_on_enter_reach": True,
        "weapons": ["glaive", "halberd", "quarterstaff", "spear"],
    },
))

# ═══════════════════════════════════════════════════════════════
#  28. Resilient
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="resilient",
    name="Resilient",
    prerequisite=None,
    description=(
        "Choose one ability score. Increase that score by 1, to a maximum of 20. "
        "You gain proficiency in saving throws using the chosen ability."
    ),
    mechanic={
        "ability_increase": {
            "choice": ["STR", "DEX", "CON", "INT", "WIS", "CHA"],
            "amount": 1,
        },
        "saving_throw_proficiency": "chosen_ability",
    },
))

# ═══════════════════════════════════════════════════════════════
#  29. Ritual Caster
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="ritual-caster",
    name="Ritual Caster",
    prerequisite="INT 13 or WIS 13",
    description=(
        "You have learned a number of spells that you can cast as rituals. "
        "Choose a class: bard, cleric, druid, sorcerer, warlock, or wizard. "
        "You acquire a ritual book holding two 1st-level spells with the "
        "ritual tag from that class's list. You can add ritual spells you "
        "find to your book if the spell level is no higher than half your "
        "level (rounded up) and you spend 2 hours and 50 gp per spell level."
    ),
    mechanic={
        "choose_class": ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"],
        "initial_rituals": 2,
        "max_spell_level": "ceil(level / 2)",
        "copy_cost_per_level": {"hours": 2, "gp": 50},
    },
))

# ═══════════════════════════════════════════════════════════════
#  30. Savage Attacker
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="savage-attacker",
    name="Savage Attacker",
    prerequisite=None,
    description=(
        "Once per turn when you roll damage for a melee weapon attack, you "
        "can reroll the weapon's damage dice and use either total."
    ),
    mechanic={
        "reroll_melee_damage": True,
        "frequency": "once_per_turn",
        "use_higher": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  31. Sentinel
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="sentinel",
    name="Sentinel",
    prerequisite=None,
    description=(
        "You have mastered techniques to take advantage of every drop in a "
        "creature's guard. When you hit a creature with an opportunity attack, "
        "its speed becomes 0 for the rest of the turn. Creatures provoke "
        "opportunity attacks from you even if they take the Disengage action. "
        "When a creature within 5 feet of you makes an attack against a target "
        "other than you, you can use your reaction to make a melee weapon "
        "attack against the attacking creature."
    ),
    mechanic={
        "opportunity_attack_stops_movement": True,
        "ignore_disengage": True,
        "reaction_attack_on_adjacent_ally_attacked": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  32. Sharpshooter
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="sharpshooter",
    name="Sharpshooter",
    prerequisite=None,
    description=(
        "You have mastered ranged weapons. Attacking at long range doesn't "
        "impose disadvantage on your ranged weapon attack rolls. Your ranged "
        "weapon attacks ignore half cover and three-quarters cover. Before you "
        "make an attack with a ranged weapon you are proficient with, you can "
        "choose to take -5 to the attack roll. If the attack hits, you add "
        "+10 to the damage."
    ),
    mechanic={
        "no_long_range_disadvantage": True,
        "ignore_cover": ["half", "three_quarters"],
        "power_attack": {"attack_penalty": -5, "damage_bonus": 10},
    },
))

# ═══════════════════════════════════════════════════════════════
#  33. Shield Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="shield-master",
    name="Shield Master",
    prerequisite=None,
    description=(
        "You use shields not just for protection but for offense. If you take "
        "the Attack action, you can use a bonus action to shove a creature "
        "within 5 feet with your shield. If you aren't incapacitated, you can "
        "add your shield's AC bonus to any DEX saving throw against a spell or "
        "effect that targets only you. If subjected to an effect that allows a "
        "DEX save for half damage, you can use your reaction to take no damage "
        "on a success, interposing your shield."
    ),
    mechanic={
        "bonus_action_shove": True,
        "shield_ac_to_dex_save": True,
        "evasion_with_shield": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  34. Skilled
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="skilled",
    name="Skilled",
    prerequisite=None,
    description=(
        "You gain proficiency in any combination of three skills or tools of "
        "your choice."
    ),
    mechanic={
        "proficiency_grant_count": 3,
        "proficiency_type": ["skill", "tool"],
    },
))

# ═══════════════════════════════════════════════════════════════
#  35. Skulker
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="skulker",
    name="Skulker",
    prerequisite="DEX 13",
    description=(
        "You are expert at slinking through shadows. You can try to hide when "
        "you are lightly obscured from the creature from which you are hiding. "
        "When you miss with a ranged weapon attack while hidden, making the "
        "attack doesn't reveal your position. Dim light doesn't impose "
        "disadvantage on your Perception checks relying on sight."
    ),
    mechanic={
        "hide_lightly_obscured": True,
        "ranged_miss_stays_hidden": True,
        "no_dim_light_perception_disadvantage": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  36. Spell Sniper
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="spell-sniper",
    name="Spell Sniper",
    prerequisite="Spellcasting",
    description=(
        "You have learned techniques to enhance your attacks with certain kinds "
        "of spells. When you cast a spell that requires an attack roll, the "
        "spell's range is doubled. Your ranged spell attacks ignore half cover "
        "and three-quarters cover. You learn one cantrip that requires an "
        "attack roll from any class."
    ),
    mechanic={
        "double_attack_spell_range": True,
        "ignore_cover": ["half", "three_quarters"],
        "learn_attack_cantrip": 1,
    },
))

# ═══════════════════════════════════════════════════════════════
#  37. Tavern Brawler
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="tavern-brawler",
    name="Tavern Brawler",
    prerequisite=None,
    description=(
        "Accustomed to rough-and-tumble fighting. Increase STR or CON by 1. "
        "You are proficient with improvised weapons. Your unarmed strike uses "
        "a d4 for damage. When you hit a creature with an unarmed strike or "
        "improvised weapon on your turn, you can use a bonus action to attempt "
        "to grapple the target."
    ),
    mechanic={
        "ability_increase": {"choice": ["STR", "CON"], "amount": 1},
        "proficiency_improvised_weapons": True,
        "unarmed_damage": "1d4",
        "bonus_action_grapple_on_hit": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  38. Tough
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="tough",
    name="Tough",
    prerequisite=None,
    description=(
        "Your hit point maximum increases by an amount equal to twice your "
        "level when you gain this feat. Each time you gain a level thereafter, "
        "your hit point maximum increases by an additional 2 hit points."
    ),
    mechanic={
        "hp_bonus_per_level": 2,
    },
))

# ═══════════════════════════════════════════════════════════════
#  39. War Caster
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="war-caster",
    name="War Caster",
    prerequisite="Spellcasting",
    description=(
        "You have practiced casting spells in the midst of combat. You have "
        "advantage on Constitution saving throws to maintain concentration "
        "when you take damage. You can perform somatic components of spells "
        "even when you have weapons or a shield in one or both hands. When a "
        "hostile creature's movement provokes an opportunity attack from you, "
        "you can use your reaction to cast a spell at the creature rather than "
        "making an opportunity attack. The spell must have a casting time of 1 "
        "action and target only that creature."
    ),
    mechanic={
        "advantage_concentration_saves": True,
        "somatic_with_hands_full": True,
        "cantrip_opportunity_attack": True,
    },
))

# ═══════════════════════════════════════════════════════════════
#  40. Weapon Master
# ═══════════════════════════════════════════════════════════════
_f(Feat(
    id="weapon-master",
    name="Weapon Master",
    prerequisite=None,
    description=(
        "You have practiced extensively with a variety of weapons. Increase "
        "STR or DEX by 1. You gain proficiency with four weapons of your choice. "
        "Each must be a simple or martial weapon."
    ),
    mechanic={
        "ability_increase": {"choice": ["STR", "DEX"], "amount": 1},
        "weapon_proficiencies": 4,
    },
))


# ═══════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════

def get_feat(feat_id: str) -> Feat | None:
    """Return a Feat by id, or None if not found."""
    return FEATS.get(feat_id)


def list_feats() -> list[Feat]:
    """Return all registered feats sorted by name."""
    return sorted(FEATS.values(), key=lambda f: f.name)


# ── Prerequisite parsing helpers ──

_ABILITY_NAMES = {"STR", "DEX", "CON", "INT", "WIS", "CHA"}


def _parse_prerequisite(prerequisite: str) -> list[dict[str, Any]]:
    """Parse a prerequisite string into structured conditions.

    Supports:
      - "STR 13"             -> ability score requirement
      - "INT 13 or WIS 13"  -> either ability meets threshold
      - "Spellcasting"       -> proficiency / feature requirement
      - "Heavy Armor Proficiency" -> proficiency requirement
      - "Light Armor Proficiency"  -> proficiency requirement
      - "Medium Armor Proficiency" -> proficiency requirement
      - "DEX 13"             -> ability score requirement
    """
    conditions: list[dict[str, Any]] = []

    # Handle "or" splits (e.g. "INT 13 or WIS 13")
    parts = [p.strip() for p in prerequisite.split(" or ")]

    for part in parts:
        tokens = part.split()
        if len(tokens) == 2 and tokens[0].upper() in _ABILITY_NAMES:
            try:
                conditions.append({
                    "type": "ability_score",
                    "ability": tokens[0].upper(),
                    "minimum": int(tokens[1]),
                })
            except ValueError:
                conditions.append({"type": "proficiency", "name": part})
        else:
            conditions.append({"type": "proficiency", "name": part})

    return conditions


def check_prerequisite(
    feat_id: str,
    ability_scores: dict[str, int] | None = None,
    proficiencies: list[str] | None = None,
) -> tuple[bool, str]:
    """Check whether a character meets a feat's prerequisites.

    Args:
        feat_id: The feat id to check.
        ability_scores: e.g. {"STR": 15, "DEX": 12, "CON": 14, ...}
        proficiencies: e.g. ["Spellcasting", "Heavy Armor Proficiency", ...]

    Returns:
        (True, "No prerequisites.") if no prerequisite or all met.
        (False, "Requires ...") if not met with a human-readable reason.
    """
    feat = get_feat(feat_id)
    if feat is None:
        return False, f"Feat '{feat_id}' not found."

    if feat.prerequisite is None:
        return True, "No prerequisites."

    ability_scores = ability_scores or {}
    proficiencies = proficiencies or []
    prof_lower = [p.lower() for p in proficiencies]

    conditions = _parse_prerequisite(feat.prerequisite)

    # "or" semantics: if any condition from the original prerequisite
    # string is met, the prerequisite is satisfied.
    has_or = " or " in (feat.prerequisite or "")

    results: list[bool] = []
    reasons: list[str] = []

    for cond in conditions:
        if cond["type"] == "ability_score":
            ability = cond["ability"]
            minimum = cond["minimum"]
            score = ability_scores.get(ability, 0)
            if score >= minimum:
                results.append(True)
            else:
                results.append(False)
                reasons.append(f"{ability} {score} < {minimum}")
        elif cond["type"] == "proficiency":
            name = cond["name"]
            if name.lower() in prof_lower:
                results.append(True)
            else:
                results.append(False)
                reasons.append(f"Missing: {name}")

    if has_or:
        # At least one condition must be met
        if any(results):
            return True, "Prerequisites met."
        return False, f"Requires {feat.prerequisite} ({'; '.join(reasons)})."
    else:
        # All conditions must be met
        if all(results):
            return True, "Prerequisites met."
        return False, f"Requires {feat.prerequisite} ({'; '.join(reasons)})."
