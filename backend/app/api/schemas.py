from pydantic import BaseModel


class ActionRequest(BaseModel):
    action: str  # free text: "go north", "talk to Goran", "pick up sword"
    lang: str = "en"


class DialogueRequest(BaseModel):
    npc_id: str
    message: str
    lang: str = "en"


class ActionResponse(BaseModel):
    narration: str
    npcs_involved: list[str] = []
    npcs_killed: list[str] = []
    location: dict | None = None
    items_changed: list[str] = []
    level_up: dict | None = None
    player_hp_change: int = 0
    player_killed: bool = False
    combat_rolls: list[dict] | None = None


class DialogueInterjection(BaseModel):
    npc_name: str
    npc_id: str
    dialogue: str
    mood: str


class DialogueResponse(BaseModel):
    npc_name: str
    dialogue: str
    mood: str
    interjections: list[DialogueInterjection] = []


class WorldStateResponse(BaseModel):
    day: int
    player_location: dict
    player_gold: int
    player_inventory: list[dict]
    player_hp: int = 10
    player_max_hp: int = 10
    player_level: int = 1
    player_class: str = "commoner"
    player_xp: int = 0


class WorldLogResponse(BaseModel):
    entries: list[dict]


class WorldMapResponse(BaseModel):
    locations: list[dict]
    connections: list[dict]
    player_location_id: str
    npc_locations: dict  # npc_id -> location_id


class LookResponse(BaseModel):
    location: dict
    npcs: list[dict]
    items: list[dict]
    exits: list[dict]
    dead_npcs: list[dict] = []


class NPCInfoResponse(BaseModel):
    id: str
    name: str
    occupation: str
    mood: str
    description: str


class NPCObserveResponse(BaseModel):
    """Full NPC state including D&D stats and evolution."""
    id: str
    name: str
    personality: str
    backstory: str
    goals: list[str]
    mood: str
    occupation: str
    age: int
    alive: bool = True
    location: dict | None
    relationships: list[dict]
    recent_memories: list[str]
    # D&D stats
    level: int = 1
    class_id: str | None = None
    race: str | None = None
    archetype: str | None = None
    current_hp: int | None = None
    max_hp: int | None = None
    ac: int | None = None
    gold: int = 0
    equipment_ids: list[str] = []
    known_spells: list[str] = []
    proficient_skills: list[str] = []
    conditions: list[str] = []
    # Evolution state
    fears: list[dict] = []
    active_goals: list[dict] = []
    nemesis: dict | None = None
    evolution_log: list[dict] = []
    trait_scale: dict | None = None
    archetype_affinity: dict[str, float] = {}
    relationship_tags: dict[str, list[dict]] = {}


class TickResponse(BaseModel):
    day: int
    events: list[dict]
    npc_actions: list[dict]
    interactions: list[dict]
    active_scenarios: list[dict] = []
    evolution_changes: list[dict] = []
