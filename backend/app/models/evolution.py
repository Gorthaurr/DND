"""Dynamic NPC evolution models — personality drift, fears, goals, relationship tags."""

from __future__ import annotations

import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


# ── Big Five as numeric scale ──

class TraitScale(BaseModel):
    """Big Five personality traits as 0.0-1.0 floats."""
    openness: float = Field(default=0.5, ge=0.0, le=1.0)
    conscientiousness: float = Field(default=0.5, ge=0.0, le=1.0)
    extraversion: float = Field(default=0.5, ge=0.0, le=1.0)
    agreeableness: float = Field(default=0.5, ge=0.0, le=1.0)
    neuroticism: float = Field(default=0.5, ge=0.0, le=1.0)

    def as_dict(self) -> dict[str, float]:
        return {"O": self.openness, "C": self.conscientiousness, "E": self.extraversion,
                "A": self.agreeableness, "N": self.neuroticism}


_LEVEL_MAP = {"low": 0.2, "mid": 0.5, "high": 0.8}
_REVERSE_LEVELS = [(0.0, 0.35, "low"), (0.35, 0.65, "mid"), (0.65, 1.01, "high")]


def parse_big_five(s: str) -> TraitScale:
    """Parse 'O:mid, C:high, E:mid, A:high, N:low' into TraitScale."""
    vals = {"O": 0.5, "C": 0.5, "E": 0.5, "A": 0.5, "N": 0.5}
    for part in s.split(","):
        part = part.strip()
        if ":" in part:
            key, level = part.split(":", 1)
            vals[key.strip().upper()] = _LEVEL_MAP.get(level.strip().lower(), 0.5)
    return TraitScale(
        openness=vals["O"], conscientiousness=vals["C"], extraversion=vals["E"],
        agreeableness=vals["A"], neuroticism=vals["N"],
    )


def to_big_five_string(ts: TraitScale) -> str:
    """Convert TraitScale back to 'O:mid, C:high, ...' for LLM prompts."""
    def _label(v: float) -> str:
        for lo, hi, lbl in _REVERSE_LEVELS:
            if lo <= v < hi:
                return lbl
        return "mid"
    return f"O:{_label(ts.openness)}, C:{_label(ts.conscientiousness)}, E:{_label(ts.extraversion)}, A:{_label(ts.agreeableness)}, N:{_label(ts.neuroticism)}"


# ── Fear ──

class Fear(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    trigger: str              # "fire", "betrayal", "darkness", "combat", "magic", "death"
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    origin_day: int = 0
    origin_event: str = ""
    decay_rate: float = 0.02  # per game day


# ── Goal lifecycle ──

class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class Goal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    status: GoalStatus = GoalStatus.ACTIVE
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    created_day: int = 0
    resolved_day: int | None = None


# ── Relationship tags ──

class RelationshipTag(BaseModel):
    tag: str          # "betrayer", "savior", "rival", "mentor", "killer", "ally", "enemy"
    since_day: int = 0
    reason: str = ""
    strength: float = Field(default=1.0, ge=0.0, le=1.0)


# ── Nemesis system ──

class NemesisStage(StrEnum):
    GRUDGE = "grudge"              # First defeat — harbours resentment
    RIVAL = "rival"                # Actively seeks rematch
    NEMESIS = "nemesis"            # Full antagonist with a plan
    ARCH_NEMESIS = "arch_nemesis"  # Final stage — will stop at nothing
    BROKEN = "broken"              # Shattered after repeated defeats


class NemesisState(BaseModel):
    """Tracks a persistent enemy relationship with escalation."""
    target_id: str
    target_name: str = ""
    stage: NemesisStage = NemesisStage.GRUDGE
    defeats_suffered: int = 0     # times lost to target
    victories_achieved: int = 0   # times won against target
    encounters: int = 0           # total meetings
    escalation_day: int = 0       # day of last stage change
    created_day: int = 0
    adaptation: str = ""          # "recruited allies", "acquired weapon", "learned spell"


# ── Evolution log ──

class EvolutionLogEntry(BaseModel):
    day: int
    change_type: str   # "trait_shift", "fear_acquired", "fear_faded", "goal_completed",
                       # "goal_failed", "goal_new", "archetype_drift", "relationship_tag"
    description: str
    old_value: str | None = None
    new_value: str | None = None


# ── Full evolution state per NPC ──

class NPCEvolutionState(BaseModel):
    traits: TraitScale = Field(default_factory=TraitScale)
    fears: list[Fear] = Field(default_factory=list)
    goals: list[Goal] = Field(default_factory=list)
    archetype_affinity: dict[str, float] = Field(default_factory=dict)
    relationship_tags: dict[str, list[RelationshipTag]] = Field(default_factory=dict)
    evolution_log: list[EvolutionLogEntry] = Field(default_factory=list)
    # Track consecutive days of archetype drift
    archetype_drift_days: int = 0
    archetype_drift_target: str | None = None
    # Nemesis — persistent enemy escalation
    nemesis: NemesisState | None = None
