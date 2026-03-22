"""Narrative combat resolver — auto-rolls dice and produces text descriptions."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.dnd.dice import ability_modifier, roll
from app.dnd.equipment import get_weapon
from app.dnd.rules import attack_roll, compute_ac, damage_roll


@dataclass
class CombatResult:
    """Result of a narrative combat exchange."""
    narrative: str
    rolls: list[dict] = field(default_factory=list)
    attacker_hp_change: int = 0
    defender_hp_change: int = 0
    attacker_name: str = ""
    defender_name: str = ""


def resolve_attack(
    attacker: dict,
    defender: dict,
    weapon_id: str | None = None,
) -> CombatResult:
    """Resolve a single attack between two entities (player/NPC).

    attacker/defender dicts should have:
      name, level, ability_scores (dict), armor_id, has_shield, weapon_ids (list)
    """
    attacker_name = attacker.get("name", "Attacker")
    defender_name = defender.get("name", "Defender")

    # Determine weapon
    weapon = None
    if weapon_id:
        weapon = get_weapon(weapon_id)
    elif attacker.get("weapon_ids"):
        weapon = get_weapon(attacker["weapon_ids"][0])

    if not weapon:
        # Unarmed strike
        damage_dice = "1d1"
        damage_type = "bludgeoning"
        weapon_name = "fist"
        is_finesse = False
    else:
        damage_dice = weapon.damage_dice
        damage_type = weapon.damage_type
        weapon_name = weapon.name
        is_finesse = "finesse" in weapon.properties

    # Determine attack ability (STR or DEX for finesse)
    abilities = attacker.get("ability_scores", {})
    str_score = abilities.get("STR", 10)
    dex_score = abilities.get("DEX", 10)

    if is_finesse:
        atk_ability = max(str_score, dex_score)
    elif weapon and "ranged" in weapon.weapon_type:
        atk_ability = dex_score
    else:
        atk_ability = str_score

    level = attacker.get("level", 1)

    # Compute defender AC
    def_dex = defender.get("ability_scores", {}).get("DEX", 10)
    target_ac = compute_ac(
        defender.get("armor_id"),
        def_dex,
        defender.get("has_shield", False),
    )

    # Attack roll
    atk = attack_roll(atk_ability, level)
    is_hit = atk["is_crit"] or (not atk["is_fumble"] and atk["total"] >= target_ac)

    rolls = [{"type": "attack", **atk}]
    narrative_parts = []

    if atk["is_fumble"]:
        narrative_parts.append(
            f"{attacker_name} swings their {weapon_name} at {defender_name} "
            f"[d20 = 1 — CRITICAL MISS!] but stumbles, the blow going wide."
        )
        return CombatResult(
            narrative=" ".join(narrative_parts),
            rolls=rolls,
            attacker_name=attacker_name,
            defender_name=defender_name,
        )

    if not is_hit:
        narrative_parts.append(
            f"{attacker_name} attacks {defender_name} with their {weapon_name} "
            f"[{atk['description']} vs AC {target_ac} — MISS!]. "
            f"The blow glances off harmlessly."
        )
        return CombatResult(
            narrative=" ".join(narrative_parts),
            rolls=rolls,
            attacker_name=attacker_name,
            defender_name=defender_name,
        )

    # Hit! Roll damage
    dmg = damage_roll(damage_dice, atk_ability, atk["is_crit"])
    rolls.append({"type": "damage", **dmg})

    if atk["is_crit"]:
        narrative_parts.append(
            f"{attacker_name} strikes {defender_name} with devastating precision "
            f"[{atk['description']} vs AC {target_ac} — CRITICAL HIT!]. "
            f"The {weapon_name} bites deep [{dmg['description']}], dealing {dmg['total']} {damage_type} damage!"
        )
    else:
        narrative_parts.append(
            f"{attacker_name} swings their {weapon_name} at {defender_name} "
            f"[{atk['description']} vs AC {target_ac} — HIT!]. "
            f"The blow connects [{dmg['description']}], dealing {dmg['total']} {damage_type} damage."
        )

    return CombatResult(
        narrative=" ".join(narrative_parts),
        rolls=rolls,
        defender_hp_change=-dmg["total"],
        attacker_name=attacker_name,
        defender_name=defender_name,
    )


def resolve_skill_check(
    character: dict,
    skill: str,
    dc: int,
    ability: str = "STR",
) -> dict:
    """Resolve a narrative skill check."""
    from app.dnd.rules import ability_check

    abilities = character.get("ability_scores", {})
    score = abilities.get(ability, 10)
    level = character.get("level", 1)
    is_prof = skill in character.get("proficiencies", [])

    result = ability_check(score, level, is_prof, dc)
    name = character.get("name", "Character")

    if result["success"]:
        narrative = f"{name} attempts a {skill} check [{result['description']}] and succeeds!"
    else:
        narrative = f"{name} attempts a {skill} check [{result['description']}] but fails."

    return {"narrative": narrative, "result": result, "character": name}
