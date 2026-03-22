"""Quest data models."""

from pydantic import BaseModel, Field


class QuestObjective(BaseModel):
    description: str
    completed: bool = False


class Quest(BaseModel):
    id: str
    title: str
    description: str
    giver_npc_id: str | None = None
    giver_npc_name: str | None = None
    objectives: list[QuestObjective] = Field(default_factory=list)
    reward_gold: int = 0
    reward_description: str = ""
    difficulty: str = "medium"  # easy | medium | hard
    status: str = "available"  # available | active | completed | failed
    scenario_id: str | None = None  # linked scenario
