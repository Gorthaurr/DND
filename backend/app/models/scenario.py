"""Scenario (story arc) data models."""

from pydantic import BaseModel, Field


class ScenarioPhase(BaseModel):
    phase_id: str
    name: str
    description: str
    trigger_day: int  # day offset from scenario start
    events_to_inject: list[dict] = Field(default_factory=list)
    npc_directives: dict[str, str] = Field(default_factory=dict)  # npc_id -> directive
    completed: bool = False


class Scenario(BaseModel):
    id: str
    title: str
    description: str
    scenario_type: str = "main"  # main | side
    start_day: int = 1
    current_phase_index: int = 0
    phases: list[ScenarioPhase] = Field(default_factory=list)
    involved_npc_ids: list[str] = Field(default_factory=list)
    active: bool = True
    tension_level: str = "low"  # low | rising | climax | resolution
