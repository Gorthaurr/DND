from pydantic import BaseModel, Field


class NPCRelationship(BaseModel):
    npc_id: str
    name: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    reason: str


class NPCDecision(BaseModel):
    action: str  # work|craft|trade|talk|gossip|help|threaten|move|patrol|sneak|fight|rob|defend|rest|pray|train|investigate|forage
    target: str | None = None
    dialogue: str | None = None
    reasoning: str = ""
    mood_change: str = "same"  # same|better|worse
    consequence: str | None = None  # brief description of what happens


class NPCContext(BaseModel):
    """Full context for NPC decision-making."""
    npc_id: str
    name: str
    personality: str
    backstory: str
    goals: list[str]
    mood: str
    occupation: str
    age: int
    location_name: str
    location_description: str
    nearby_npcs: list[dict]
    relationships: list[NPCRelationship]
    recent_memories: list[str]
    recent_events: list[str]
    world_day: int
    # Archetype-driven fields
    archetype_name: str | None = None
    archetype_dialogue_style: str | None = None
    archetype_decision_bias: str | None = None
    archetype_group_role: str | None = None
    # Phase & scene context
    current_phase: str | None = None  # morning|afternoon|evening
    active_scene_context: str | None = None  # injected by SceneSetter
    # Equipment & combat context
    equipment_summary: str | None = None  # "Armed with longsword, wearing chain mail (AC 16), carrying 30gp"
    combat_capability: str | None = None  # "Capable fighter (level 5, AC 16, ~40 HP)"
    gold: int = 0
    nearby_locations: list[str] = Field(default_factory=list)  # connected location names
    # Speech & biography
    speech_instructions: str | None = None  # concrete speech rules from Big Five mapping
    biography: str | None = None  # full biography (childhood, trauma, secrets)
    # Long-term evolution baselines
    trust_baseline: float = 0.0       # -1.0 (paranoid) to 1.0 (naive)
    mood_baseline: float = 0.0        # -1.0 (depressed) to 1.0 (optimistic)
    aggression_baseline: float = 0.0  # -1.0 (pacifist) to 1.0 (aggressive)
    confidence_baseline: float = 0.0  # -1.0 (coward) to 1.0 (fearless)
    # Environment
    season: str | None = None
    weather: str | None = None
    location_condition: str | None = None
    # Economy
    local_shortages: list[str] = Field(default_factory=list)
    # Faction
    faction_directive: str | None = None
    faction_strategy: str | None = None


class NPC(BaseModel):
    id: str
    name: str
    personality: str
    backstory: str
    biography: str = ""
    goals: list[str]
    mood: str
    occupation: str
    age: int
    alive: bool = True
    archetype: str | None = None
    current_activity: str | None = None
    # D&D 5e stats
    race: str | None = None
    class_id: str | None = None
    level: int = 1
    ability_scores: dict[str, int] = Field(default_factory=lambda: {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10})
    equipment_ids: list[str] = Field(default_factory=list)
    armor_id: str | None = None
    has_shield: bool = False
    gold: int = 0
    max_hp: int = 10
    current_hp: int = 10
    # Evolution baselines
    trust_baseline: float = 0.0
    mood_baseline: float = 0.0
    aggression_baseline: float = 0.0
    confidence_baseline: float = 0.0
