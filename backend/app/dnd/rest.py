"""D&D 5e Short Rest / Long Rest mechanics."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.dnd.dice import roll, ability_modifier
from app.dnd.classes import get_class, get_spell_slots


@dataclass
class HitDicePool:
    """Tracks hit dice available for spending during short rests."""
    total: int          # = character level
    used: int = 0
    die_size: int = 8   # d8, d10, d12, etc.

    @property
    def remaining(self) -> int:
        return max(0, self.total - self.used)

    def spend_one(self, con_mod: int) -> int:
        """Spend one hit die, return HP healed."""
        if self.remaining <= 0:
            return 0
        self.used += 1
        r = roll(f"1d{self.die_size}")
        return max(1, r.total + con_mod)


@dataclass
class RestResult:
    """Result of taking a short or long rest."""
    rest_type: str  # "short" or "long"
    hp_healed: int = 0
    hp_after: int = 0
    max_hp: int = 0
    hit_dice_spent: int = 0
    hit_dice_remaining: int = 0
    # Resources restored
    spell_slots_restored: bool = False
    resources_restored: list[str] = field(default_factory=list)
    conditions_removed: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)


def short_rest(
    current_hp: int,
    max_hp: int,
    con_score: int,
    class_id: str,
    level: int,
    hit_dice_used: int,
    hit_dice_to_spend: int = 0,
    # Class resources
    ki_points_used: int = 0,
    channel_divinity_used: int = 0,
    second_wind_used: bool = False,
    action_surge_used: bool = False,
    bardic_inspiration_used: int = 0,
    wild_shape_used: int = 0,
    conditions: list[str] | None = None,
) -> tuple[RestResult, dict]:
    """
    Resolve a short rest (1 hour).

    D&D 5e rules:
    - Can spend hit dice to heal (roll hit die + CON mod per die)
    - Restores: Ki points, Channel Divinity (some), Second Wind, Action Surge,
      Bardic Inspiration (at lvl 5+), Wild Shape, Warlock spell slots
    - Does NOT restore: spell slots (except Warlock), HP beyond spending hit dice

    Returns (RestResult, updated_resources_dict).
    """
    cls = get_class(class_id)
    hit_die = cls.hit_die if cls else 8
    con_mod = ability_modifier(con_score)

    result = RestResult(rest_type="short", max_hp=max_hp)
    resources = {}

    # ── Spend hit dice to heal ──
    pool = HitDicePool(total=level, used=hit_dice_used, die_size=hit_die)
    dice_to_spend = min(hit_dice_to_spend, pool.remaining)
    total_healed = 0

    for _ in range(dice_to_spend):
        healed = pool.spend_one(con_mod)
        total_healed += healed

    new_hp = min(max_hp, current_hp + total_healed)
    result.hp_healed = new_hp - current_hp
    result.hp_after = new_hp
    result.hit_dice_spent = dice_to_spend
    result.hit_dice_remaining = pool.remaining
    resources["hit_dice_used"] = pool.used

    if dice_to_spend > 0:
        result.details.append(
            f"Spent {dice_to_spend} hit dice (d{hit_die}), healed {result.hp_healed} HP"
        )

    # ── Restore short rest resources ──

    # Fighter: Second Wind, Action Surge
    if class_id == "fighter":
        if second_wind_used:
            resources["second_wind_used"] = False
            result.resources_restored.append("Second Wind")
        if action_surge_used and level >= 2:
            resources["action_surge_used"] = False
            result.resources_restored.append("Action Surge")

    # Monk: Ki points (all restored)
    if class_id == "monk" and level >= 2:
        ki_max = level  # ki points = monk level
        if ki_points_used > 0:
            resources["ki_points"] = ki_max
            result.resources_restored.append(f"Ki Points ({ki_max})")

    # Cleric: Channel Divinity (restored on short rest)
    if class_id == "cleric" and level >= 2:
        if channel_divinity_used > 0:
            resources["channel_divinity_uses"] = 0
            result.resources_restored.append("Channel Divinity")

    # Bard: Bardic Inspiration (restored on short rest at level 5+)
    if class_id == "bard" and level >= 5:
        cha_mod = max(1, ability_modifier(10))  # need actual CHA, use default
        if bardic_inspiration_used > 0:
            resources["bardic_inspiration_uses"] = 0
            result.resources_restored.append("Bardic Inspiration")

    # Druid: Wild Shape (restored on short rest)
    if class_id == "druid" and level >= 2:
        if wild_shape_used > 0:
            resources["wild_shape_uses"] = 0
            result.resources_restored.append("Wild Shape")

    # Warlock: Pact Magic slots (restore on short rest)
    if class_id == "warlock":
        resources["spell_slots_used"] = {}
        result.spell_slots_restored = True
        result.resources_restored.append("Pact Magic Slots")

    return result, resources


def long_rest(
    current_hp: int,
    max_hp: int,
    class_id: str,
    level: int,
    hit_dice_used: int,
    conditions: list[str] | None = None,
) -> tuple[RestResult, dict]:
    """
    Resolve a long rest (8 hours).

    D&D 5e rules:
    - Regain ALL hit points
    - Regain spent hit dice up to half your total (minimum 1)
    - Restore ALL spell slots
    - Restore ALL class resources (rage, ki, sorcery points, etc.)
    - Remove exhaustion by 1 level
    - Does NOT automatically remove other conditions

    Returns (RestResult, updated_resources_dict).
    """
    result = RestResult(rest_type="long", max_hp=max_hp)
    resources: dict = {}

    # ── Full HP restoration ──
    result.hp_healed = max_hp - current_hp
    result.hp_after = max_hp
    result.details.append(f"Restored to full HP ({max_hp})")

    # ── Recover hit dice (half of total, min 1) ──
    dice_to_recover = max(1, level // 2)
    new_used = max(0, hit_dice_used - dice_to_recover)
    result.hit_dice_remaining = level - new_used
    resources["hit_dice_used"] = new_used
    if hit_dice_used > 0:
        result.details.append(
            f"Recovered {hit_dice_used - new_used} hit dice ({result.hit_dice_remaining}/{level} available)"
        )

    # ── Restore ALL spell slots ──
    resources["spell_slots_used"] = {}
    result.spell_slots_restored = True
    result.resources_restored.append("All Spell Slots")

    # ── Restore ALL class resources ──

    # Barbarian: Rage uses
    if class_id == "barbarian":
        rage_max = _rage_uses_by_level(level)
        resources["rage_uses"] = rage_max
        result.resources_restored.append(f"Rage ({rage_max} uses)")

    # Fighter
    if class_id == "fighter":
        resources["second_wind_used"] = False
        resources["action_surge_used"] = False
        resources["indomitable_uses"] = 0
        result.resources_restored.append("Second Wind, Action Surge, Indomitable")

    # Monk: Ki
    if class_id == "monk" and level >= 2:
        resources["ki_points"] = level
        result.resources_restored.append(f"Ki Points ({level})")

    # Paladin: Lay on Hands, Channel Divinity, Divine Sense
    if class_id == "paladin":
        loh_pool = level * 5
        resources["lay_on_hands_pool"] = loh_pool
        resources["channel_divinity_uses"] = 0
        result.resources_restored.append(f"Lay on Hands ({loh_pool} HP pool)")

    # Cleric: Channel Divinity
    if class_id == "cleric" and level >= 2:
        resources["channel_divinity_uses"] = 0
        result.resources_restored.append("Channel Divinity")

    # Sorcerer: Sorcery Points
    if class_id == "sorcerer" and level >= 2:
        resources["sorcery_points"] = level
        result.resources_restored.append(f"Sorcery Points ({level})")

    # Bard: Bardic Inspiration
    if class_id == "bard":
        resources["bardic_inspiration_uses"] = 0
        result.resources_restored.append("Bardic Inspiration")

    # Druid: Wild Shape
    if class_id == "druid" and level >= 2:
        resources["wild_shape_uses"] = 0
        result.resources_restored.append("Wild Shape")

    # Warlock: Pact Magic (already handled by spell slots)

    # ── Conditions: reduce exhaustion by 1 ──
    active_conditions = list(conditions or [])
    if "exhaustion" in active_conditions:
        result.conditions_removed.append("exhaustion (1 level)")
        result.details.append("Exhaustion reduced by 1 level")

    # Death saves reset
    resources["death_save_successes"] = 0
    resources["death_save_failures"] = 0

    return result, resources


def _rage_uses_by_level(level: int) -> int:
    """Barbarian rage uses per long rest by level."""
    if level < 3:
        return 2
    if level < 6:
        return 3
    if level < 12:
        return 4
    if level < 17:
        return 5
    if level < 20:
        return 6
    return 999  # level 20: unlimited
