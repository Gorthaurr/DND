"""Nemesis system — persistent enemy escalation. Pure deterministic, no LLM."""

from __future__ import annotations

import random

from app.models.evolution import (
    NemesisStage, NemesisState, NPCEvolutionState,
    Fear, Goal, GoalStatus, RelationshipTag, EvolutionLogEntry,
)

# ── Escalation timing (days since last escalation) ──
ESCALATION_THRESHOLDS: dict[str, int] = {
    NemesisStage.GRUDGE: 3,       # GRUDGE → RIVAL after 3 days
    NemesisStage.RIVAL: 10,       # RIVAL → NEMESIS after 10 days
    NemesisStage.NEMESIS: 20,     # NEMESIS → ARCH_NEMESIS after 20 days
}

# Defeats that also force escalation (regardless of time)
DEFEAT_ESCALATION: dict[str, int] = {
    NemesisStage.GRUDGE: 2,       # 2nd defeat → RIVAL
    NemesisStage.RIVAL: 3,        # 3rd defeat → NEMESIS
    NemesisStage.NEMESIS: 4,      # 4th defeat → ARCH_NEMESIS
}

# 3+ defeats with 0 victories → BROKEN
BROKEN_DEFEAT_THRESHOLD = 3

_STAGE_ORDER = [
    NemesisStage.GRUDGE,
    NemesisStage.RIVAL,
    NemesisStage.NEMESIS,
    NemesisStage.ARCH_NEMESIS,
]


def check_nemesis_trigger(
    evo: NPCEvolutionState,
    opponent_id: str,
    opponent_name: str,
    combat_lost: bool,
    robbed: bool,
    nearly_killed: bool,
    world_day: int,
) -> bool:
    """Check if a nemesis relationship should be created. Returns True if created."""
    if evo.nemesis is not None:
        return False  # already has a nemesis

    should_create = combat_lost or robbed or nearly_killed
    if not should_create:
        return False

    reason_parts = []
    if combat_lost:
        reason_parts.append("defeated in combat")
    if robbed:
        reason_parts.append("robbed")
    if nearly_killed:
        reason_parts.append("nearly killed")

    evo.nemesis = NemesisState(
        target_id=opponent_id,
        target_name=opponent_name,
        stage=NemesisStage.GRUDGE,
        defeats_suffered=1 if combat_lost else 0,
        encounters=1,
        escalation_day=world_day,
        created_day=world_day,
    )

    # Add "nemesis" relationship tag
    tags = evo.relationship_tags.setdefault(opponent_id, [])
    tags.append(RelationshipTag(
        tag="nemesis", since_day=world_day,
        reason=", ".join(reason_parts), strength=1.0,
    ))

    return True


def record_nemesis_combat(evo: NPCEvolutionState, won: bool) -> None:
    """Record a combat outcome against the nemesis target."""
    if evo.nemesis is None:
        return
    evo.nemesis.encounters += 1
    if won:
        evo.nemesis.victories_achieved += 1
    else:
        evo.nemesis.defeats_suffered += 1


def escalate_nemesis(
    evo: NPCEvolutionState,
    world_day: int,
) -> list[EvolutionLogEntry]:
    """Attempt to escalate nemesis stage. Returns log entries for changes."""
    nem = evo.nemesis
    if nem is None or nem.stage == NemesisStage.BROKEN or nem.stage == NemesisStage.ARCH_NEMESIS:
        return []

    logs: list[EvolutionLogEntry] = []

    # Check BROKEN condition: 3+ defeats, 0 victories
    if nem.defeats_suffered >= BROKEN_DEFEAT_THRESHOLD and nem.victories_achieved == 0:
        old = nem.stage
        nem.stage = NemesisStage.BROKEN
        nem.escalation_day = world_day
        logs.append(EvolutionLogEntry(
            day=world_day, change_type="nemesis_broken",
            description=f"Broken by {nem.target_name} after {nem.defeats_suffered} defeats",
            old_value=old, new_value=NemesisStage.BROKEN,
        ))
        # Add fear of the nemesis
        evo.fears.append(Fear(
            trigger=nem.target_name.lower(), intensity=0.8,
            origin_day=world_day, origin_event=f"broken by {nem.target_name}",
        ))
        return logs

    # Check time-based or defeat-based escalation
    current_idx = _STAGE_ORDER.index(nem.stage)
    days_since = world_day - nem.escalation_day
    time_threshold = ESCALATION_THRESHOLDS.get(nem.stage, 999)
    defeat_threshold = DEFEAT_ESCALATION.get(nem.stage, 999)

    should_escalate = days_since >= time_threshold or nem.defeats_suffered >= defeat_threshold

    if should_escalate and current_idx < len(_STAGE_ORDER) - 1:
        old = nem.stage
        nem.stage = _STAGE_ORDER[current_idx + 1]
        nem.escalation_day = world_day
        logs.append(EvolutionLogEntry(
            day=world_day, change_type="nemesis_escalation",
            description=f"Nemesis towards {nem.target_name} escalated: {old} → {nem.stage}",
            old_value=old, new_value=nem.stage,
        ))

    return logs


# ── Adaptation pools by stage ──
_RIVAL_ADAPTATIONS = [
    "acquired a better weapon",
    "recruited an ally",
    "trained combat skills",
    "studied opponent's tactics",
    "fortified their position",
]

_NEMESIS_ADAPTATIONS = [
    "learned a new combat spell",
    "improved a key ability score",
    "acquired enchanted armor",
    "set a trap for the target",
    "gathered intelligence on target's weaknesses",
]

_ARCH_NEMESIS_ADAPTATIONS = [
    "acquired a powerful magic item",
    "recruited a small warband",
    "made a dark pact for power",
    "mastered a devastating technique",
    "built a fortified hideout",
]


def apply_nemesis_adaptations(
    evo: NPCEvolutionState,
    world_day: int,
    rng: random.Random | None = None,
) -> list[EvolutionLogEntry]:
    """Apply stage-appropriate adaptations. Called once per escalation."""
    nem = evo.nemesis
    if nem is None or nem.stage in (NemesisStage.GRUDGE, NemesisStage.BROKEN):
        return []

    rng = rng or random.Random()

    pool = {
        NemesisStage.RIVAL: _RIVAL_ADAPTATIONS,
        NemesisStage.NEMESIS: _NEMESIS_ADAPTATIONS,
        NemesisStage.ARCH_NEMESIS: _ARCH_NEMESIS_ADAPTATIONS,
    }.get(nem.stage, [])

    if not pool:
        return []

    adaptation = rng.choice(pool)
    old_adapt = nem.adaptation
    nem.adaptation = adaptation

    return [EvolutionLogEntry(
        day=world_day, change_type="nemesis_adaptation",
        description=f"Adapted against {nem.target_name}: {adaptation}",
        old_value=old_adapt or "none", new_value=adaptation,
    )]


# ── LLM prompt directives ──

_STAGE_DIRECTIVES: dict[str, str] = {
    NemesisStage.GRUDGE: (
        "You harbour deep resentment towards {name}. You glare at them when nearby "
        "and mutter bitter words. You haven't acted yet, but the anger festers."
    ),
    NemesisStage.RIVAL: (
        "You actively seek to challenge {name} and prove yourself their equal. "
        "You train harder, gather resources, and look for the right moment to strike."
    ),
    NemesisStage.NEMESIS: (
        "Defeating {name} has become your obsession. You plot, scheme, and prepare. "
        "Every decision you make is coloured by this burning need for revenge."
    ),
    NemesisStage.ARCH_NEMESIS: (
        "You will stop at nothing to destroy {name}. This is personal, total, final. "
        "You have sacrificed everything for this moment. There is no going back."
    ),
    NemesisStage.BROKEN: (
        "You flinch at the mere mention of {name}. They have broken your spirit. "
        "You avoid them at all costs and live in fear of another encounter."
    ),
}


def get_nemesis_directive(nemesis: NemesisState) -> str:
    """Generate a narrative directive for the LLM decision prompt."""
    template = _STAGE_DIRECTIVES.get(nemesis.stage, "")
    return template.format(name=nemesis.target_name)
