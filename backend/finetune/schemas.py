"""Pydantic validation models for all agent response types."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Shared enums ──────────────────────────────────────────────────────────────

class MoodChange(str, Enum):
    SAME = "same"
    BETTER = "better"
    WORSE = "worse"


class NPCAction(str, Enum):
    WORK = "work"
    CRAFT = "craft"
    TRADE = "trade"
    TALK = "talk"
    GOSSIP = "gossip"
    HELP = "help"
    THREATEN = "threaten"
    MOVE = "move"
    PATROL = "patrol"
    SNEAK = "sneak"
    FIGHT = "fight"
    ROB = "rob"
    DEFEND = "defend"
    REST = "rest"
    PRAY = "pray"
    TRAIN = "train"
    INVESTIGATE = "investigate"
    FORAGE = "forage"


class InteractionType(str, Enum):
    CONVERSATION = "conversation"
    ARGUMENT = "argument"
    TRADE = "trade"
    FIGHT = "fight"
    ROBBERY = "robbery"
    HELP = "help"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    WARNING = "warning"


class InteractionAction(str, Enum):
    FIGHT = "fight"
    TRADE = "trade"
    ROB = "rob"
    HELP = "help"
    THREATEN = "threaten"
    GIFT = "gift"
    NONE = "none"


class ActionInitiator(str, Enum):
    A = "a"
    B = "b"
    NONE = "none"


class TensionLevel(str, Enum):
    LOW = "low"
    RISING = "rising"
    CLIMAX = "climax"
    RESOLUTION = "resolution"


class ScenarioAction(str, Enum):
    STAY = "stay"
    ADVANCE = "advance"
    TWIST = "twist"
    RESOLVE = "resolve"


class QuestDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ── 1. NPCDecisionResponse ───────────────────────────────────────────────────

class NPCDecisionResponse(BaseModel):
    action: NPCAction
    target: str | None = None
    dialogue: str | None = None
    reasoning: str
    mood_change: MoodChange
    consequence: str | None = None


# ── 2. NPCDialogueResponse ───────────────────────────────────────────────────

class NPCDialogueResponse(BaseModel):
    dialogue: str = Field(min_length=1)
    mood_change: MoodChange
    sentiment_change: float = Field(ge=-1.0, le=1.0)
    internal_thought: str


# ── 3. NPCInteractResponse ───────────────────────────────────────────────────

class NPCInteractResponse(BaseModel):
    interaction_type: InteractionType
    summary: str
    dialogue_a: str
    dialogue_b: str
    action: InteractionAction
    action_initiator: ActionInitiator
    action_details: dict[str, Any] = Field(default_factory=dict)
    a_sentiment_change: float = Field(ge=-1.0, le=1.0)
    b_sentiment_change: float = Field(ge=-1.0, le=1.0)
    a_mood_change: MoodChange
    b_mood_change: MoodChange


# ── 4. NPCInterjectionResponse ───────────────────────────────────────────────

class NPCInterjectionResponse(BaseModel):
    should_interject: bool
    reason: str
    dialogue: str | None = None
    mood_change: MoodChange


# ── 5. CombatIntentResponse ──────────────────────────────────────────────────

class CombatTarget(BaseModel):
    npc_id: str
    npc_name: str


class CombatIntentResponse(BaseModel):
    is_combat: bool
    targets: list[CombatTarget] = Field(default_factory=list)
    player_has_advantage: bool
    player_has_disadvantage: bool
    npcs_join_fight: list[CombatTarget] = Field(default_factory=list)
    context: str


# ── 6. CombatNarrateResponse ─────────────────────────────────────────────────

class CombatNarrateResponse(BaseModel):
    narration: str
    summary: str


# ── 7. DMNarrateResponse ─────────────────────────────────────────────────────

class DMNarrateResponse(BaseModel):
    narration: str
    npcs_involved: list[str] = Field(default_factory=list)
    npcs_killed: list[str] = Field(default_factory=list)
    npcs_mood_changes: dict[str, str] = Field(default_factory=dict)
    items_changed: list[Any] = Field(default_factory=list)
    items_gained: list[str] = Field(default_factory=list)
    items_lost: list[str] = Field(default_factory=list)
    location_changed: str | None = None
    reputation_changes: dict[str, int] = Field(default_factory=dict)
    player_hp_change: int = 0
    player_killed: bool = False


# ── 8. ScenarioGenerateResponse ──────────────────────────────────────────────

class ScenarioGenerateResponse(BaseModel):
    title: str
    description: str
    scenario_type: str
    tension_level: str
    involved_npc_ids: list[str] = Field(default_factory=list)
    phases: list[dict[str, Any]] = Field(default_factory=list)


# ── 9. ScenarioAdvanceResponse ───────────────────────────────────────────────

class ScenarioAdvanceResponse(BaseModel):
    action: ScenarioAction
    tension_level: TensionLevel
    narrative_update: str
    events_to_inject: list[Any] = Field(default_factory=list)
    npc_directives: dict[str, Any] = Field(default_factory=dict)


# ── 10. EventGenerateResponse ────────────────────────────────────────────────

class EventEntry(BaseModel):
    description: str
    type: str
    location_id: str
    severity: str


class EventGenerateResponse(BaseModel):
    events: list[EventEntry] = Field(default_factory=list)


# ── 11. QuestGenerateResponse ────────────────────────────────────────────────

class QuestObjective(BaseModel):
    description: str


class QuestGenerateResponse(BaseModel):
    title: str
    description: str
    giver_npc_id: str
    giver_npc_name: str
    objectives: list[QuestObjective] = Field(default_factory=list)
    reward_gold: int
    reward_description: str
    difficulty: QuestDifficulty


# ── Schema map & validation helper ───────────────────────────────────────────

SCHEMA_MAP: dict[str, type[BaseModel]] = {
    "npc_decision": NPCDecisionResponse,
    "npc_dialogue": NPCDialogueResponse,
    "npc_interact": NPCInteractResponse,
    "npc_interjection": NPCInterjectionResponse,
    "combat_intent": CombatIntentResponse,
    "combat_narrate": CombatNarrateResponse,
    "dm_narrate": DMNarrateResponse,
    "scenario_generate": ScenarioGenerateResponse,
    "scenario_advance": ScenarioAdvanceResponse,
    "event_generate": EventGenerateResponse,
    "quest_generate": QuestGenerateResponse,
}


def validate_response(agent_type: str, data: dict) -> tuple[bool, str | None]:
    """Validate *data* against the Pydantic model for *agent_type*.

    Returns:
        (True, None) on success.
        (False, error_message) on validation failure or unknown agent type.
    """
    schema = SCHEMA_MAP.get(agent_type)
    if schema is None:
        return False, f"Unknown agent_type: {agent_type}"
    try:
        schema.model_validate(data)
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
