"""D&D 5e core rules — AC computation, checks, saving throws, XP tables."""

from __future__ import annotations

from app.dnd.dice import ability_modifier, proficiency_bonus, roll, roll_d20, RollResult
from app.dnd.equipment import get_armor, Armor


# ── XP Table (level -> cumulative XP required) ──

XP_TABLE: dict[int, int] = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
    6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
    11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
    16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000,
}


def level_for_xp(xp: int) -> int:
    """Determine character level from total XP."""
    for lvl in range(20, 0, -1):
        if xp >= XP_TABLE[lvl]:
            return lvl
    return 1


def compute_ac(armor_id: str | None, dex_score: int, has_shield: bool = False) -> int:
    """Compute Armor Class from equipped armor and DEX score."""
    dex_mod = ability_modifier(dex_score)
    base_ac = 10 + dex_mod  # unarmored

    if armor_id:
        armor = get_armor(armor_id)
        if armor:
            if armor.armor_type == "shield":
                base_ac += armor.ac_base
            elif armor.armor_type == "light":
                base_ac = armor.ac_base + dex_mod
            elif armor.armor_type == "medium":
                base_ac = armor.ac_base + min(dex_mod, armor.max_dex_bonus or 2)
            elif armor.armor_type == "heavy":
                base_ac = armor.ac_base

    if has_shield:
        base_ac += 2

    return base_ac


def attack_roll(
    ability_score: int,
    level: int,
    is_proficient: bool = True,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict:
    """Make an attack roll. Returns {roll, total, is_hit (needs AC), is_crit, is_fumble}."""
    mod = ability_modifier(ability_score)
    prof = proficiency_bonus(level) if is_proficient else 0
    total_mod = mod + prof

    r = roll_d20(total_mod, advantage, disadvantage)
    return {
        "roll": r,
        "modifier": total_mod,
        "total": r.total,
        "natural": r.natural,
        "is_crit": r.natural == 20,
        "is_fumble": r.natural == 1,
        "description": f"d20({r.natural}) + {total_mod} = {r.total}",
    }


def damage_roll(damage_dice: str, ability_score: int, is_crit: bool = False) -> dict:
    """Roll damage. On crit, roll damage dice twice."""
    mod = ability_modifier(ability_score)

    if is_crit:
        # Roll damage dice twice
        r1 = roll(damage_dice)
        r2 = roll(damage_dice)
        total = r1.total + r2.total - r1.modifier + mod  # only add modifier once
        return {
            "rolls": r1.rolls + r2.rolls,
            "modifier": mod,
            "total": total,
            "is_crit": True,
            "description": f"CRITICAL! {damage_dice}×2 + {mod} = {total}",
        }
    else:
        r = roll(damage_dice)
        total = r.total + mod
        return {
            "rolls": r.rolls,
            "modifier": mod,
            "total": max(0, total),
            "is_crit": False,
            "description": f"{damage_dice} + {mod} = {total}",
        }


def ability_check(
    ability_score: int,
    level: int = 1,
    is_proficient: bool = False,
    dc: int = 10,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict:
    """Make an ability/skill check vs DC."""
    mod = ability_modifier(ability_score)
    prof = proficiency_bonus(level) if is_proficient else 0
    total_mod = mod + prof

    r = roll_d20(total_mod, advantage, disadvantage)
    success = r.total >= dc

    return {
        "roll": r,
        "modifier": total_mod,
        "total": r.total,
        "dc": dc,
        "success": success,
        "natural": r.natural,
        "description": f"d20({r.natural}) + {total_mod} = {r.total} vs DC {dc} → {'SUCCESS' if success else 'FAIL'}",
    }


def saving_throw(
    ability_score: int,
    level: int = 1,
    is_proficient: bool = False,
    dc: int = 10,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict:
    """Make a saving throw vs DC. Same mechanics as ability check."""
    return ability_check(ability_score, level, is_proficient, dc, advantage, disadvantage)


def compute_max_hp(hit_die: int, level: int, con_score: int) -> int:
    """Compute max HP. Level 1 = max die + CON mod. Higher = average + CON mod per level."""
    con_mod = ability_modifier(con_score)
    # Level 1: max die + CON
    hp = hit_die + con_mod
    # Levels 2+: average die roll + CON
    avg_die = hit_die // 2 + 1  # e.g. d10 -> 6, d8 -> 5, d12 -> 7
    hp += (level - 1) * (avg_die + con_mod)
    return max(1, hp)


def spell_dc(spellcasting_ability_score: int, level: int) -> int:
    """Compute spell save DC = 8 + prof + ability mod."""
    return 8 + proficiency_bonus(level) + ability_modifier(spellcasting_ability_score)


def spell_attack_bonus(spellcasting_ability_score: int, level: int) -> int:
    """Compute spell attack bonus = prof + ability mod."""
    return proficiency_bonus(level) + ability_modifier(spellcasting_ability_score)
