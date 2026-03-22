from pydantic import BaseModel


class WorldState(BaseModel):
    day: int = 1
    player_location_id: str = ""
    player_location_name: str = ""
    player_gold: int = 50
    tick_running: bool = False


class WorldLogEntry(BaseModel):
    day: int
    summary: str
    events: list[str] = []
    npc_actions: list[str] = []


class Location(BaseModel):
    id: str
    name: str
    type: str
    description: str


class WorldMap(BaseModel):
    locations: list[Location]
    connections: list[dict]
