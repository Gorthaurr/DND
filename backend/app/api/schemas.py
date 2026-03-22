from pydantic import BaseModel


class ActionRequest(BaseModel):
    action: str  # free text: "go north", "talk to Goran", "pick up sword"


class DialogueRequest(BaseModel):
    npc_id: str
    message: str


class ActionResponse(BaseModel):
    narration: str
    npcs_involved: list[str] = []
    npcs_killed: list[str] = []
    location: dict | None = None
    items_changed: list[str] = []
    level_up: dict | None = None


class DialogueResponse(BaseModel):
    npc_name: str
    dialogue: str
    mood: str


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


class NPCInfoResponse(BaseModel):
    id: str
    name: str
    occupation: str
    mood: str
    description: str


class NPCObserveResponse(BaseModel):
    """Debug/demo: full NPC state."""
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


class TickResponse(BaseModel):
    day: int
    events: list[dict]
    npc_actions: list[dict]
    interactions: list[dict]
    active_scenarios: list[dict] = []
