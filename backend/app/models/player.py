from pydantic import BaseModel


class Player(BaseModel):
    id: str = "player-1"
    name: str = "Adventurer"
    reputation: int = 0
    gold: int = 50


class PlayerAction(BaseModel):
    action: str  # free-form text like "go north", "talk to Goran", "pick up sword"


class DialogueRequest(BaseModel):
    npc_id: str
    message: str
