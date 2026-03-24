"""D&D 5e spell casting engine — resolves spells mechanically without LLM."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.dnd.dice import ability_modifier, proficiency_bonus, roll, roll_d20
from app.dnd.spells import get_spell, Spell
from app.dnd.classes import get_class, get_spell_slots
from app.dnd.rules import spell_dc, spell_attack_bonus


@dataclass
class SpellTarget:
    """A target of a spell."""
    id: str
    name: str
    current_hp: int
    max_hp: int
    ac: int
    ability_scores: dict[str, int]
    level: int = 1
    saving_throw_proficiencies: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)


@dataclass
class SpellResult:
    """Result of casting a spell."""
    success: bool
    spell_name: str
    caster_name: str
    targets: list[str]  # target names
    effect_type: str
    # Damage/healing
    total_damage: int = 0
    total_healing: int = 0
    damage_type: str | None = None
    # Rolls
    spell_attack_roll: dict | None = None
    saving_throw_results: list[dict] = field(default_factory=list)
    damage_rolls: list[dict] = field(default_factory=list)
    healing_rolls: list[dict] = field(default_factory=list)
    # Conditions
    conditions_applied: list[dict] = field(default_factory=list)  # [{target, condition}]
    conditions_removed: list[dict] = field(default_factory=list)
    # Resources
    slot_used: int = 0  # spell level slot consumed (0 for cantrips)
    concentration: bool = False
    # Narrative
    narrative: str = ""
    all_rolls: list[dict] = field(default_factory=list)


def can_cast_spell(
    spell_id: str,
    caster_class_id: str,
    caster_level: int,
    known_spells: list[str],
    spell_slots_used: dict[str, int],
    cast_at_level: int | None = None,
) -> tuple[bool, str]:
    """Check if a caster can cast a given spell. Returns (can_cast, reason)."""
    spell = get_spell(spell_id)
    if not spell:
        return False, f"Unknown spell: {spell_id}"

    if spell_id not in known_spells and spell.level > 0:
        return False, f"{spell.name} is not known"

    if caster_class_id not in spell.classes:
        return False, f"{spell.name} is not available to this class"

    if spell.level == 0:
        return True, "Cantrip — no slot needed"

    slot_level = cast_at_level or spell.level
    if slot_level < spell.level:
        return False, f"Cannot cast {spell.name} at level {slot_level} (minimum {spell.level})"

    available_slots = get_spell_slots(caster_class_id, caster_level)
    if slot_level not in available_slots:
        return False, f"No level {slot_level} spell slots available"

    used = spell_slots_used.get(str(slot_level), 0)
    total = available_slots.get(slot_level, 0)
    if used >= total:
        return False, f"No level {slot_level} spell slots remaining ({used}/{total} used)"

    return True, "OK"


def _resolve_spell_attack(
    spell: Spell,
    caster_ability_score: int,
    caster_level: int,
    target: SpellTarget,
) -> dict:
    """Resolve a spell attack roll vs target AC."""
    bonus = spell_attack_bonus(caster_ability_score, caster_level)
    r = roll_d20(bonus)
    hit = r.total >= target.ac or r.natural == 20
    crit = r.natural == 20
    fumble = r.natural == 1

    return {
        "type": "spell_attack",
        "roll": r.natural,
        "modifier": bonus,
        "total": r.total,
        "target_ac": target.ac,
        "hit": hit and not fumble,
        "crit": crit,
        "fumble": fumble,
        "description": (
            f"Spell Attack: d20({r.natural}) + {bonus} = {r.total} "
            f"vs AC {target.ac} -> {'HIT' if hit and not fumble else 'MISS'}"
            f"{' (CRITICAL!)' if crit else ''}"
        ),
    }


def _resolve_saving_throw(
    spell: Spell,
    dc: int,
    target: SpellTarget,
) -> dict:
    """Resolve a saving throw for a target against a spell."""
    save_ability = spell.save_ability or "DEX"
    ability_score = target.ability_scores.get(save_ability, 10)
    mod = ability_modifier(ability_score)

    is_proficient = save_ability in target.saving_throw_proficiencies
    prof = proficiency_bonus(target.level) if is_proficient else 0
    total_mod = mod + prof

    # Check for auto-fail from conditions
    from app.dnd.conditions import auto_fail_save
    if auto_fail_save(target.conditions, save_ability):
        return {
            "type": "saving_throw",
            "target": target.name,
            "ability": save_ability,
            "auto_fail": True,
            "success": False,
            "dc": dc,
            "description": f"{target.name} auto-fails {save_ability} save (condition)",
        }

    r = roll_d20(total_mod)
    success = r.total >= dc

    return {
        "type": "saving_throw",
        "target": target.name,
        "ability": save_ability,
        "roll": r.natural,
        "modifier": total_mod,
        "total": r.total,
        "dc": dc,
        "success": success,
        "proficient": is_proficient,
        "description": (
            f"{target.name} {save_ability} Save: d20({r.natural}) + {total_mod} = {r.total} "
            f"vs DC {dc} -> {'SUCCESS' if success else 'FAIL'}"
        ),
    }


def _roll_spell_damage(spell: Spell, is_crit: bool = False, upcast_level: int = 0) -> dict:
    """Roll damage for a damage spell."""
    if not spell.damage_dice:
        return {"total": 0, "rolls": [], "description": "No damage"}

    dice = spell.damage_dice
    r1 = roll(dice)
    total = r1.total

    if is_crit:
        r2 = roll(dice)
        total += r2.total
        desc = f"CRIT! {dice}x2 = {total}"
    else:
        desc = f"{dice} = {total}"

    return {
        "total": total,
        "dice": dice,
        "is_crit": is_crit,
        "damage_type": spell.damage_type,
        "description": desc,
    }


def _roll_spell_healing(spell: Spell, caster_ability_score: int) -> dict:
    """Roll healing for a healing spell."""
    if not spell.healing_dice:
        return {"total": 0, "description": "No healing"}

    r = roll(spell.healing_dice)
    mod = ability_modifier(caster_ability_score)
    total = r.total + mod

    return {
        "total": max(1, total),
        "dice": spell.healing_dice,
        "modifier": mod,
        "description": f"{spell.healing_dice} + {mod} = {total}",
    }


def cast_spell(
    spell_id: str,
    caster_name: str,
    caster_class_id: str,
    caster_level: int,
    caster_ability_scores: dict[str, int],
    known_spells: list[str],
    spell_slots_used: dict[str, int],
    targets: list[SpellTarget],
    cast_at_level: int | None = None,
) -> SpellResult:
    """
    Resolve a spell cast mechanically.

    Handles: spell attacks, saving throws, damage, healing, conditions.
    Returns SpellResult with all rolls and effects.
    """
    spell = get_spell(spell_id)
    if not spell:
        return SpellResult(
            success=False, spell_name=spell_id, caster_name=caster_name,
            targets=[], effect_type="unknown", narrative=f"Unknown spell: {spell_id}",
        )

    # Determine spellcasting ability
    cls = get_class(caster_class_id)
    cast_ability = cls.spellcasting_ability if cls else "INT"
    cast_ability_score = caster_ability_scores.get(cast_ability, 10)
    dc = spell_dc(cast_ability_score, caster_level)

    slot_level = cast_at_level or spell.level
    target_names = [t.name for t in targets]

    result = SpellResult(
        success=True,
        spell_name=spell.name,
        caster_name=caster_name,
        targets=target_names,
        effect_type=spell.effect_type,
        slot_used=slot_level if spell.level > 0 else 0,
        concentration=spell.concentration,
    )

    # Consume spell slot
    if spell.level > 0:
        key = str(slot_level)
        spell_slots_used[key] = spell_slots_used.get(key, 0) + 1

    # ── Damage spells ──
    if spell.effect_type == "damage" and spell.damage_dice:
        result.damage_type = spell.damage_type

        for target in targets:
            if spell.save_ability:
                # Save-based damage (Fireball, etc.)
                save_result = _resolve_saving_throw(spell, dc, target)
                result.saving_throw_results.append(save_result)
                result.all_rolls.append(save_result)

                dmg = _roll_spell_damage(spell)
                if save_result["success"]:
                    dmg["total"] = dmg["total"] // 2
                    dmg["description"] += " (halved on save)"

                result.damage_rolls.append({"target": target.name, **dmg})
                result.all_rolls.append(dmg)
                result.total_damage += dmg["total"]
                target.current_hp = max(0, target.current_hp - dmg["total"])

            else:
                # Attack-based damage (Fire Bolt, etc.)
                atk = _resolve_spell_attack(spell, cast_ability_score, caster_level, target)
                result.spell_attack_roll = atk
                result.all_rolls.append(atk)

                if atk["hit"]:
                    dmg = _roll_spell_damage(spell, is_crit=atk["crit"])
                    result.damage_rolls.append({"target": target.name, **dmg})
                    result.all_rolls.append(dmg)
                    result.total_damage += dmg["total"]
                    target.current_hp = max(0, target.current_hp - dmg["total"])

    # ── Healing spells ──
    elif spell.effect_type == "healing" and spell.healing_dice:
        for target in targets:
            heal = _roll_spell_healing(spell, cast_ability_score)
            result.healing_rolls.append({"target": target.name, **heal})
            result.all_rolls.append(heal)
            result.total_healing += heal["total"]
            target.current_hp = min(target.max_hp, target.current_hp + heal["total"])

    # ── Debuff/control spells (Hold Person, etc.) ──
    elif spell.effect_type in ("debuff", "control") and spell.save_ability:
        for target in targets:
            save_result = _resolve_saving_throw(spell, dc, target)
            result.saving_throw_results.append(save_result)
            result.all_rolls.append(save_result)

            if not save_result["success"] and spell.conditions_applied:
                for cond_id in spell.conditions_applied:
                    result.conditions_applied.append({
                        "target": target.name,
                        "target_id": target.id,
                        "condition": cond_id,
                    })
                    target.conditions.append(cond_id)

    # ── Buff spells (Bless, Shield, Haste, etc.) ──
    elif spell.effect_type == "buff":
        for target in targets:
            if spell.conditions_applied:
                for cond_id in spell.conditions_applied:
                    result.conditions_applied.append({
                        "target": target.name,
                        "target_id": target.id,
                        "condition": cond_id,
                    })

    # ── Auto-damage (Magic Missile, no attack roll, no save) ──
    if spell_id == "magic-missile":
        result.damage_rolls = []
        result.total_damage = 0
        num_missiles = 3 + (slot_level - 1) if slot_level > 1 else 3
        for i in range(num_missiles):
            missile = roll("1d4")
            dmg = missile.total + 1  # 1d4+1 per missile
            result.damage_rolls.append({
                "target": targets[0].name if targets else "unknown",
                "total": dmg,
                "description": f"Missile {i+1}: 1d4+1 = {dmg}",
            })
            result.total_damage += dmg
        if targets:
            targets[0].current_hp = max(0, targets[0].current_hp - result.total_damage)

    # Build narrative
    parts = [f"{caster_name} casts {spell.name}"]
    if result.total_damage > 0:
        parts.append(f"dealing {result.total_damage} {result.damage_type or ''} damage")
    if result.total_healing > 0:
        parts.append(f"healing for {result.total_healing} HP")
    if result.conditions_applied:
        conds = ", ".join(c["condition"] for c in result.conditions_applied)
        parts.append(f"applying {conds}")
    if result.concentration:
        parts.append("(concentrating)")
    result.narrative = " ".join(parts) + "."

    return result
