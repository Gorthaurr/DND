"""D&D 5e conditions — all standard conditions with mechanical effects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConditionType(str, Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"
    CONCENTRATING = "concentrating"


@dataclass
class Condition:
    type: ConditionType
    description: str
    # Mechanical effects
    attack_advantage: bool = False      # attacker has advantage
    attack_disadvantage: bool = False   # creature has disadvantage on attacks
    save_advantage: dict[str, bool] = field(default_factory=dict)  # ability: True/False
    save_disadvantage: dict[str, bool] = field(default_factory=dict)
    auto_fail_saves: list[str] = field(default_factory=list)  # auto-fail these saves
    speed_zero: bool = False
    can_act: bool = True
    can_move: bool = True
    grants_advantage_to_melee: bool = False  # melee attacks within 5ft have advantage
    check_disadvantage: bool = False     # disadvantage on ability checks


# ── All D&D 5e Conditions ──

CONDITIONS: dict[str, Condition] = {}


def _define() -> None:
    c = CONDITIONS

    c["blinded"] = Condition(
        type=ConditionType.BLINDED,
        description="Can't see. Auto-fail sight checks. Attack rolls have disadvantage. Attacks against have advantage.",
        attack_disadvantage=True,
        attack_advantage=True,
    )

    c["charmed"] = Condition(
        type=ConditionType.CHARMED,
        description="Can't attack the charmer. Charmer has advantage on social checks.",
    )

    c["deafened"] = Condition(
        type=ConditionType.DEAFENED,
        description="Can't hear. Auto-fail hearing checks.",
    )

    c["exhaustion"] = Condition(
        type=ConditionType.EXHAUSTION,
        description="Levels 1-6. L1: disadvantage on checks. L2: speed halved. L3: disadvantage on attacks/saves. L4: HP max halved. L5: speed 0. L6: death.",
        check_disadvantage=True,
    )

    c["frightened"] = Condition(
        type=ConditionType.FRIGHTENED,
        description="Disadvantage on checks and attacks while source of fear is in sight. Can't willingly move closer.",
        attack_disadvantage=True,
        check_disadvantage=True,
    )

    c["grappled"] = Condition(
        type=ConditionType.GRAPPLED,
        description="Speed becomes 0. Ends if grappler is incapacitated or moved out of range.",
        speed_zero=True,
    )

    c["incapacitated"] = Condition(
        type=ConditionType.INCAPACITATED,
        description="Can't take actions or reactions.",
        can_act=False,
    )

    c["invisible"] = Condition(
        type=ConditionType.INVISIBLE,
        description="Can't be seen without magic/special sense. Advantage on attacks. Attacks against have disadvantage.",
        attack_advantage=False,  # the INVISIBLE creature gets advantage
        attack_disadvantage=True,  # attacks AGAINST invisible have disadvantage
    )

    c["paralyzed"] = Condition(
        type=ConditionType.PARALYZED,
        description="Incapacitated, can't move or speak. Auto-fail STR/DEX saves. Attacks have advantage. Melee hits within 5ft are auto-crits.",
        can_act=False,
        can_move=False,
        speed_zero=True,
        auto_fail_saves=["STR", "DEX"],
        grants_advantage_to_melee=True,
    )

    c["petrified"] = Condition(
        type=ConditionType.PETRIFIED,
        description="Transformed to stone. Incapacitated, can't move/speak. Resistance to all damage. Auto-fail STR/DEX saves. Attacks have advantage.",
        can_act=False,
        can_move=False,
        speed_zero=True,
        auto_fail_saves=["STR", "DEX"],
        attack_advantage=True,
    )

    c["poisoned"] = Condition(
        type=ConditionType.POISONED,
        description="Disadvantage on attack rolls and ability checks.",
        attack_disadvantage=True,
        check_disadvantage=True,
    )

    c["prone"] = Condition(
        type=ConditionType.PRONE,
        description="Disadvantage on attacks. Melee within 5ft has advantage, ranged has disadvantage. Standing costs half movement.",
        attack_disadvantage=True,
        grants_advantage_to_melee=True,
    )

    c["restrained"] = Condition(
        type=ConditionType.RESTRAINED,
        description="Speed 0. Disadvantage on attacks. Attacks against have advantage. Disadvantage on DEX saves.",
        speed_zero=True,
        attack_disadvantage=True,
        attack_advantage=True,
        save_disadvantage={"DEX": True},
    )

    c["stunned"] = Condition(
        type=ConditionType.STUNNED,
        description="Incapacitated, can't move, can only speak falteringly. Auto-fail STR/DEX saves. Attacks have advantage.",
        can_act=False,
        can_move=False,
        auto_fail_saves=["STR", "DEX"],
        attack_advantage=True,
    )

    c["unconscious"] = Condition(
        type=ConditionType.UNCONSCIOUS,
        description="Incapacitated, can't move/speak, unaware. Drop what held, fall prone. Auto-fail STR/DEX saves. Attacks have advantage. Melee within 5ft auto-crit.",
        can_act=False,
        can_move=False,
        speed_zero=True,
        auto_fail_saves=["STR", "DEX"],
        grants_advantage_to_melee=True,
    )

    c["concentrating"] = Condition(
        type=ConditionType.CONCENTRATING,
        description="Maintaining a concentration spell. Broken by: casting another concentration spell, taking damage (CON save DC = max(10, damage/2)), incapacitation, death.",
    )


_define()


def get_condition(condition_id: str) -> Condition | None:
    return CONDITIONS.get(condition_id)


def list_conditions() -> list[Condition]:
    return list(CONDITIONS.values())


def has_attack_advantage(conditions: list[str]) -> bool:
    """Check if any active condition grants advantage to attackers."""
    return any(
        CONDITIONS.get(c, Condition(type=ConditionType.BLINDED, description="")).attack_advantage
        for c in conditions
    )


def has_attack_disadvantage(conditions: list[str]) -> bool:
    """Check if any active condition gives disadvantage on attacks."""
    return any(
        CONDITIONS.get(c, Condition(type=ConditionType.BLINDED, description="")).attack_disadvantage
        for c in conditions
    )


def can_take_actions(conditions: list[str]) -> bool:
    """Check if creature can take actions given its conditions."""
    for c_id in conditions:
        c = CONDITIONS.get(c_id)
        if c and not c.can_act:
            return False
    return True


def can_move(conditions: list[str]) -> bool:
    """Check if creature can move given its conditions."""
    for c_id in conditions:
        c = CONDITIONS.get(c_id)
        if c and (not c.can_move or c.speed_zero):
            return False
    return True


def auto_fail_save(conditions: list[str], ability: str) -> bool:
    """Check if any condition causes auto-fail on a given saving throw."""
    for c_id in conditions:
        c = CONDITIONS.get(c_id)
        if c and ability in c.auto_fail_saves:
            return True
    return False
