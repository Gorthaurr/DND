"""D&D 5e Death Saving Throws mechanics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.dnd.dice import roll_d20


class DeathState(str, Enum):
    ALIVE = "alive"
    DYING = "dying"          # at 0 HP, making death saves
    STABLE = "stable"        # at 0 HP but stabilized
    DEAD = "dead"
    INSTANT_DEATH = "instant_death"  # massive damage


@dataclass
class DeathSaveResult:
    """Result of a single death saving throw."""
    roll: int
    natural_20: bool = False
    natural_1: bool = False
    success: bool = False
    total_successes: int = 0
    total_failures: int = 0
    outcome: DeathState = DeathState.DYING
    description: str = ""


@dataclass
class DeathTracker:
    """Tracks death saving throws for a creature."""
    successes: int = 0
    failures: int = 0
    state: DeathState = DeathState.ALIVE

    def reset(self) -> None:
        """Reset when creature regains HP or is stabilized."""
        self.successes = 0
        self.failures = 0

    @property
    def is_dying(self) -> bool:
        return self.state == DeathState.DYING

    @property
    def is_dead(self) -> bool:
        return self.state in (DeathState.DEAD, DeathState.INSTANT_DEATH)


def check_instant_death(damage: int, current_hp: int, max_hp: int) -> bool:
    """
    Check for instant death from massive damage.

    D&D 5e rule: If remaining damage after reaching 0 HP
    equals or exceeds your max HP, you die instantly.
    """
    if current_hp > 0:
        return False
    remaining_damage = damage - current_hp  # how much damage past 0
    return remaining_damage >= max_hp


def drop_to_zero(
    current_hp: int,
    damage: int,
    max_hp: int,
) -> tuple[DeathState, str]:
    """
    Handle a creature dropping to 0 HP.

    Returns (new_state, description).
    """
    if current_hp > 0:
        return DeathState.ALIVE, "Still standing"

    # Check instant death from massive damage
    overflow = damage - (current_hp + damage)  # damage beyond 0
    # Actually: creature was at current_hp, took damage, new hp would be current_hp - damage
    effective_hp = current_hp - damage
    if effective_hp <= 0:
        overflow = abs(effective_hp)
        if overflow >= max_hp:
            return (
                DeathState.INSTANT_DEATH,
                f"Massive damage ({overflow} overflow >= {max_hp} max HP) — instant death!",
            )

    return DeathState.DYING, "Knocked to 0 HP — making death saving throws"


def make_death_save(tracker: DeathTracker) -> DeathSaveResult:
    """
    Make a death saving throw.

    D&D 5e rules:
    - Roll d20 (no modifiers by default)
    - 10+ = success, 9 or lower = failure
    - Natural 20 = regain 1 HP, wake up (count as stabilized + conscious)
    - Natural 1 = 2 failures instead of 1
    - 3 successes = stabilized (unconscious but no longer dying)
    - 3 failures = dead
    """
    if tracker.state != DeathState.DYING:
        return DeathSaveResult(
            roll=0, outcome=tracker.state,
            description=f"Not dying (state: {tracker.state.value})",
        )

    r = roll_d20(modifier=0)
    natural = r.natural
    result = DeathSaveResult(roll=natural)

    # Natural 20: wake up with 1 HP
    if natural == 20:
        result.natural_20 = True
        result.success = True
        tracker.reset()
        tracker.state = DeathState.ALIVE
        result.outcome = DeathState.ALIVE
        result.description = "Natural 20! Regains 1 HP and wakes up!"
        return result

    # Natural 1: count as 2 failures
    if natural == 1:
        result.natural_1 = True
        result.success = False
        tracker.failures += 2
    elif natural >= 10:
        result.success = True
        tracker.successes += 1
    else:
        result.success = False
        tracker.failures += 1

    result.total_successes = tracker.successes
    result.total_failures = tracker.failures

    # Check outcomes
    if tracker.failures >= 3:
        tracker.state = DeathState.DEAD
        result.outcome = DeathState.DEAD
        result.description = (
            f"Death save: d20({natural}) — FAILURE "
            f"({tracker.failures} failures) — DEAD!"
        )
    elif tracker.successes >= 3:
        tracker.state = DeathState.STABLE
        result.outcome = DeathState.STABLE
        tracker.reset()
        result.description = (
            f"Death save: d20({natural}) — SUCCESS "
            f"({tracker.successes} successes) — Stabilized!"
        )
    else:
        result.outcome = DeathState.DYING
        status = "SUCCESS" if result.success else "FAILURE"
        if natural == 1:
            status = "CRITICAL FAILURE (2 failures)"
        result.description = (
            f"Death save: d20({natural}) — {status} "
            f"(successes: {tracker.successes}/3, failures: {tracker.failures}/3)"
        )

    return result


def take_damage_while_dying(
    tracker: DeathTracker,
    damage: int,
    is_critical: bool = False,
    max_hp: int = 0,
) -> DeathSaveResult:
    """
    Handle taking damage while at 0 HP.

    D&D 5e rules:
    - Any damage = 1 death save failure
    - Critical hit = 2 death save failures
    - Damage >= max HP = instant death
    """
    if damage >= max_hp > 0:
        tracker.state = DeathState.INSTANT_DEATH
        return DeathSaveResult(
            roll=0, outcome=DeathState.INSTANT_DEATH,
            total_failures=tracker.failures,
            description=f"Damage ({damage}) >= max HP ({max_hp}) — instant death!",
        )

    failures_added = 2 if is_critical else 1
    tracker.failures += failures_added

    result = DeathSaveResult(
        roll=0,
        total_successes=tracker.successes,
        total_failures=tracker.failures,
    )

    if tracker.failures >= 3:
        tracker.state = DeathState.DEAD
        result.outcome = DeathState.DEAD
        result.description = (
            f"Took {damage} damage while dying "
            f"(+{failures_added} failure{'s' if failures_added > 1 else ''}) — DEAD!"
        )
    else:
        result.outcome = DeathState.DYING
        result.description = (
            f"Took {damage} damage while dying "
            f"(+{failures_added} failure{'s' if failures_added > 1 else ''}, "
            f"total: {tracker.failures}/3)"
        )

    return result


def stabilize(tracker: DeathTracker) -> str:
    """
    Stabilize a dying creature (e.g., via Spare the Dying, Healer's Kit,
    or Medicine check DC 10).

    The creature is unconscious at 0 HP but no longer dying.
    """
    if tracker.state != DeathState.DYING:
        return f"Cannot stabilize — not dying (state: {tracker.state.value})"

    tracker.state = DeathState.STABLE
    tracker.reset()
    return "Stabilized! Unconscious at 0 HP, no longer making death saves."


def heal_from_zero(tracker: DeathTracker, healing: int) -> str:
    """
    Apply healing to a creature at 0 HP.

    Any healing brings them back to consciousness with that many HP.
    Resets death saves.
    """
    if tracker.state not in (DeathState.DYING, DeathState.STABLE):
        return f"Not at 0 HP (state: {tracker.state.value})"

    tracker.state = DeathState.ALIVE
    tracker.reset()
    return f"Healed for {healing} HP — conscious and alive!"
