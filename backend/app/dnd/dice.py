"""Dice rolling engine for D&D 5e.

Supports standard notation: "2d6+3", "1d20", "4d6kh3" (keep highest 3).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from math import floor

# Pattern: NdS[kh/kl K][+/-M]  e.g. 4d6kh3, 2d8+5, 1d20
_DICE_RE = re.compile(
    r"^(\d+)d(\d+)"            # NdS
    r"(?:(kh|kl)(\d+))?"       # optional keep highest/lowest K
    r"([+-]\d+)?$",            # optional modifier
    re.IGNORECASE,
)


@dataclass
class RollResult:
    """Result of a dice roll."""
    notation: str
    rolls: list[int]
    kept: list[int]
    modifier: int
    total: int
    natural: int = 0  # raw d20 value for crit detection


def roll(notation: str) -> RollResult:
    """Roll dice from notation string like '2d6+3' or '4d6kh3'."""
    notation = notation.strip().lower().replace(" ", "")
    m = _DICE_RE.match(notation)
    if not m:
        raise ValueError(f"Invalid dice notation: {notation}")

    num_dice = int(m.group(1))
    sides = int(m.group(2))
    keep_type = m.group(3)  # "kh" or "kl" or None
    keep_count = int(m.group(4)) if m.group(4) else num_dice
    modifier = int(m.group(5)) if m.group(5) else 0

    rolls = [random.randint(1, sides) for _ in range(num_dice)]

    if keep_type == "kh":
        kept = sorted(rolls, reverse=True)[:keep_count]
    elif keep_type == "kl":
        kept = sorted(rolls)[:keep_count]
    else:
        kept = list(rolls)

    total = sum(kept) + modifier
    natural = rolls[0] if num_dice == 1 and sides == 20 else 0

    return RollResult(
        notation=notation,
        rolls=rolls,
        kept=kept,
        modifier=modifier,
        total=total,
        natural=natural,
    )


def roll_d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> RollResult:
    """Roll a d20 with optional advantage/disadvantage."""
    if advantage and disadvantage:
        advantage = disadvantage = False  # cancel out

    if advantage:
        r = roll("2d20kh1")
        return RollResult(
            notation=f"d20+{modifier} (advantage)",
            rolls=r.rolls, kept=r.kept, modifier=modifier,
            total=r.kept[0] + modifier, natural=r.kept[0],
        )
    elif disadvantage:
        r = roll("2d20kl1")
        return RollResult(
            notation=f"d20+{modifier} (disadvantage)",
            rolls=r.rolls, kept=r.kept, modifier=modifier,
            total=r.kept[0] + modifier, natural=r.kept[0],
        )
    else:
        r = roll("1d20")
        return RollResult(
            notation=f"d20+{modifier}",
            rolls=r.rolls, kept=r.kept, modifier=modifier,
            total=r.rolls[0] + modifier, natural=r.rolls[0],
        )


def roll_stats() -> list[int]:
    """Roll ability scores: 4d6 keep highest 3, six times. Sorted descending."""
    scores = [roll("4d6kh3").total for _ in range(6)]
    return sorted(scores, reverse=True)


def ability_modifier(score: int) -> int:
    """Compute ability modifier from score. floor((score - 10) / 2)."""
    return floor((score - 10) / 2)


def proficiency_bonus(level: int) -> int:
    """Compute proficiency bonus from character level."""
    return floor((max(1, level) - 1) / 4) + 2
