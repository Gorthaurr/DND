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
    # Evolution context (injected from NPCEvolutionState)
    fears: list[dict] = Field(default_factory=list)
    active_goals: list[dict] = Field(default_factory=list)
    completed_goals: list[str] = Field(default_factory=list)
    relationship_tags: dict[str, list[str]] = Field(default_factory=dict)


class NPC(BaseModel):
    id: str
    name: str
    personality: str
    backstory: str
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
    # D&D 5e abilities
    known_spells: list[str] = Field(default_factory=list)
    proficient_skills: list[str] = Field(default_factory=list)
    expertise_skills: list[str] = Field(default_factory=list)
    saving_throw_proficiencies: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)  # active conditions
    spell_slots_used: dict[str, int] = Field(default_factory=dict)
    # Resources
    rage_uses: int = 0
    ki_points: int = 0
    sorcery_points: int = 0
    channel_divinity_uses: int = 0
    lay_on_hands_pool: int = 0
    bardic_inspiration_uses: int = 0
    wild_shape_uses: int = 0
    # Evolution state (serialized NPCEvolutionState)
    evolution_state_json: str | None = None
