"""World Builder API — CRUD for custom worlds, locations, NPCs, and AI generation."""

import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.connection import get_driver
from app.graph.seed import seed_world
from app.utils.llm import generate_json
from app.utils.logger import get_logger

log = get_logger("world_builder")

world_builder_router = APIRouter(prefix="/api/worlds", tags=["world-builder"])


# ── Storage helpers ──────────────────────────────────────────────────────


def _worlds_root() -> Path:
    root = settings.data_dir / "custom_worlds"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _world_dir(world_id: str) -> Path:
    return _worlds_root() / world_id


def _load_meta(world_id: str) -> dict:
    meta_file = _world_dir(world_id) / "meta.json"
    if not meta_file.exists():
        raise HTTPException(404, f"World '{world_id}' not found")
    with open(meta_file, encoding="utf-8") as f:
        return json.load(f)


def _save_meta(world_id: str, data: dict) -> None:
    meta_file = _world_dir(world_id) / "meta.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_world_data(world_id: str) -> dict:
    world_file = _world_dir(world_id) / "world.json"
    if not world_file.exists():
        return {"locations": [], "connections": [], "factions": [], "items": []}
    with open(world_file, encoding="utf-8") as f:
        return json.load(f)


def _save_world_data(world_id: str, data: dict) -> None:
    world_file = _world_dir(world_id) / "world.json"
    with open(world_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_npcs_data(world_id: str) -> dict:
    npcs_file = _world_dir(world_id) / "npcs.json"
    if not npcs_file.exists():
        return {"npcs": []}
    with open(npcs_file, encoding="utf-8") as f:
        return json.load(f)


def _save_npcs_data(world_id: str, data: dict) -> None:
    npcs_file = _world_dir(world_id) / "npcs.json"
    with open(npcs_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Request / Response models ────────────────────────────────────────────


class CreateWorldRequest(BaseModel):
    name: str
    description: str = ""


class WorldSummary(BaseModel):
    id: str
    name: str
    description: str
    location_count: int = 0
    npc_count: int = 0


class LocationCreate(BaseModel):
    name: str
    type: str = "generic"
    description: str = ""


class LocationUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    description: str | None = None


class ConnectionCreate(BaseModel):
    from_id: str
    to_id: str
    distance: int = 1


class NPCCreate(BaseModel):
    name: str
    personality: str = ""
    backstory: str = ""
    goals: list[str] = Field(default_factory=list)
    mood: str = "neutral"
    occupation: str = "commoner"
    age: int = 30
    archetype: str | None = None
    race: str | None = None
    npc_class: str | None = None
    location_id: str | None = None


class NPCUpdate(BaseModel):
    name: str | None = None
    personality: str | None = None
    backstory: str | None = None
    goals: list[str] | None = None
    mood: str | None = None
    occupation: str | None = None
    age: int | None = None
    archetype: str | None = None
    race: str | None = None
    npc_class: str | None = None
    location_id: str | None = None


class GeneratePrompt(BaseModel):
    description: str


# ── World CRUD ───────────────────────────────────────────────────────────


@world_builder_router.get("", response_model=list[WorldSummary])
async def list_worlds():
    root = _worlds_root()
    worlds: list[WorldSummary] = []
    for child in sorted(root.iterdir()):
        meta_file = child / "meta.json"
        if child.is_dir() and meta_file.exists():
            with open(meta_file, encoding="utf-8") as f:
                meta = json.load(f)
            wd = _load_world_data(child.name)
            nd = _load_npcs_data(child.name)
            worlds.append(WorldSummary(
                id=child.name,
                name=meta["name"],
                description=meta.get("description", ""),
                location_count=len(wd.get("locations", [])),
                npc_count=len(nd.get("npcs", [])),
            ))
    return worlds


@world_builder_router.post("", response_model=WorldSummary, status_code=201)
async def create_world(req: CreateWorldRequest):
    world_id = str(uuid.uuid4())[:8]
    wdir = _world_dir(world_id)
    wdir.mkdir(parents=True, exist_ok=True)
    meta = {"name": req.name, "description": req.description}
    _save_meta(world_id, meta)
    _save_world_data(world_id, {"locations": [], "connections": [], "factions": [], "items": []})
    _save_npcs_data(world_id, {"npcs": []})
    log.info("world_created", world_id=world_id, name=req.name)
    return WorldSummary(id=world_id, name=req.name, description=req.description)


@world_builder_router.get("/{world_id}")
async def get_world(world_id: str):
    meta = _load_meta(world_id)
    world_data = _load_world_data(world_id)
    npcs_data = _load_npcs_data(world_id)
    return {**meta, "id": world_id, "world": world_data, "npcs": npcs_data["npcs"]}


@world_builder_router.delete("/{world_id}")
async def delete_world(world_id: str):
    import shutil
    wdir = _world_dir(world_id)
    if not wdir.exists():
        raise HTTPException(404, f"World '{world_id}' not found")
    shutil.rmtree(wdir)
    log.info("world_deleted", world_id=world_id)
    return {"status": "deleted", "world_id": world_id}


@world_builder_router.post("/{world_id}/load")
async def load_world(world_id: str):
    wdir = _world_dir(world_id)
    if not wdir.exists():
        raise HTTPException(404, f"World '{world_id}' not found")
    driver = get_driver()
    await seed_world(driver, wdir)
    log.info("world_loaded", world_id=world_id)
    return {"status": "loaded", "world_id": world_id}


# ── Locations ────────────────────────────────────────────────────────────


@world_builder_router.get("/{world_id}/locations")
async def list_locations(world_id: str):
    _load_meta(world_id)  # existence check
    return _load_world_data(world_id).get("locations", [])


@world_builder_router.post("/{world_id}/locations", status_code=201)
async def create_location(world_id: str, req: LocationCreate):
    _load_meta(world_id)
    wd = _load_world_data(world_id)
    loc_id = f"loc-{uuid.uuid4().hex[:6]}"
    location = {"id": loc_id, "name": req.name, "type": req.type, "description": req.description}
    wd["locations"].append(location)
    _save_world_data(world_id, wd)
    return location


@world_builder_router.put("/{world_id}/locations/{loc_id}")
async def update_location(world_id: str, loc_id: str, req: LocationUpdate):
    _load_meta(world_id)
    wd = _load_world_data(world_id)
    for loc in wd["locations"]:
        if loc["id"] == loc_id:
            if req.name is not None:
                loc["name"] = req.name
            if req.type is not None:
                loc["type"] = req.type
            if req.description is not None:
                loc["description"] = req.description
            _save_world_data(world_id, wd)
            return loc
    raise HTTPException(404, f"Location '{loc_id}' not found")


@world_builder_router.delete("/{world_id}/locations/{loc_id}")
async def delete_location(world_id: str, loc_id: str):
    _load_meta(world_id)
    wd = _load_world_data(world_id)
    before = len(wd["locations"])
    wd["locations"] = [l for l in wd["locations"] if l["id"] != loc_id]
    wd["connections"] = [c for c in wd["connections"] if c["from"] != loc_id and c["to"] != loc_id]
    if len(wd["locations"]) == before:
        raise HTTPException(404, f"Location '{loc_id}' not found")
    _save_world_data(world_id, wd)
    return {"status": "deleted", "loc_id": loc_id}


@world_builder_router.post("/{world_id}/connections", status_code=201)
async def create_connection(world_id: str, req: ConnectionCreate):
    _load_meta(world_id)
    wd = _load_world_data(world_id)
    loc_ids = {l["id"] for l in wd["locations"]}
    if req.from_id not in loc_ids or req.to_id not in loc_ids:
        raise HTTPException(400, "One or both location IDs not found in this world")
    conn = {"from": req.from_id, "to": req.to_id, "distance": req.distance}
    wd["connections"].append(conn)
    _save_world_data(world_id, wd)
    return conn


# ── NPCs ─────────────────────────────────────────────────────────────────


@world_builder_router.get("/{world_id}/npcs")
async def list_npcs(world_id: str):
    _load_meta(world_id)
    return _load_npcs_data(world_id).get("npcs", [])


@world_builder_router.post("/{world_id}/npcs", status_code=201)
async def create_npc(world_id: str, req: NPCCreate):
    _load_meta(world_id)
    nd = _load_npcs_data(world_id)
    npc_id = f"npc-{uuid.uuid4().hex[:6]}"
    npc = {
        "id": npc_id,
        "name": req.name,
        "personality": req.personality,
        "backstory": req.backstory,
        "goals": req.goals,
        "mood": req.mood,
        "occupation": req.occupation,
        "age": req.age,
        "alive": True,
        "archetype": req.archetype,
        "race": req.race,
        "class": req.npc_class,
        "location_id": req.location_id,
        "relationships": [],
    }
    nd["npcs"].append(npc)
    _save_npcs_data(world_id, nd)
    return npc


@world_builder_router.put("/{world_id}/npcs/{npc_id}")
async def update_npc(world_id: str, npc_id: str, req: NPCUpdate):
    _load_meta(world_id)
    nd = _load_npcs_data(world_id)
    for npc in nd["npcs"]:
        if npc["id"] == npc_id:
            updates = req.model_dump(exclude_none=True)
            if "npc_class" in updates:
                updates["class"] = updates.pop("npc_class")
            npc.update(updates)
            _save_npcs_data(world_id, nd)
            return npc
    raise HTTPException(404, f"NPC '{npc_id}' not found")


@world_builder_router.delete("/{world_id}/npcs/{npc_id}")
async def delete_npc(world_id: str, npc_id: str):
    _load_meta(world_id)
    nd = _load_npcs_data(world_id)
    before = len(nd["npcs"])
    nd["npcs"] = [n for n in nd["npcs"] if n["id"] != npc_id]
    if len(nd["npcs"]) == before:
        raise HTTPException(404, f"NPC '{npc_id}' not found")
    _save_npcs_data(world_id, nd)
    return {"status": "deleted", "npc_id": npc_id}


# ── AI Generation ────────────────────────────────────────────────────────


NPC_GEN_SYSTEM = (
    "You are a D&D world builder assistant. Generate a detailed NPC as JSON with fields: "
    "name, personality, backstory, goals (array), mood, occupation, age (int), "
    "archetype, race, class. Be creative and consistent with the description."
)

LOCATION_GEN_SYSTEM = (
    "You are a D&D world builder assistant. Generate a detailed location as JSON with fields: "
    "name, type (tavern|market|temple|forest|dungeon|castle|village|cave|road|other), "
    "description. Be vivid and atmospheric."
)


@world_builder_router.post("/{world_id}/generate/npc")
async def generate_npc(world_id: str, req: GeneratePrompt):
    _load_meta(world_id)
    prompt = f"Generate a D&D NPC based on this description:\n{req.description}\nReturn ONLY valid JSON."
    result = await generate_json(prompt, system=NPC_GEN_SYSTEM, temperature=0.9)
    if not result:
        raise HTTPException(500, "AI generation failed — no valid JSON returned")
    npc_id = f"npc-{uuid.uuid4().hex[:6]}"
    result["id"] = npc_id
    result.setdefault("alive", True)
    result.setdefault("relationships", [])
    result.setdefault("goals", [])
    nd = _load_npcs_data(world_id)
    nd["npcs"].append(result)
    _save_npcs_data(world_id, nd)
    log.info("npc_generated", world_id=world_id, name=result.get("name"))
    return result


@world_builder_router.post("/{world_id}/generate/location")
async def generate_location(world_id: str, req: GeneratePrompt):
    _load_meta(world_id)
    prompt = f"Generate a D&D location based on this description:\n{req.description}\nReturn ONLY valid JSON."
    result = await generate_json(prompt, system=LOCATION_GEN_SYSTEM, temperature=0.9)
    if not result:
        raise HTTPException(500, "AI generation failed — no valid JSON returned")
    loc_id = f"loc-{uuid.uuid4().hex[:6]}"
    result["id"] = loc_id
    wd = _load_world_data(world_id)
    wd["locations"].append(result)
    _save_world_data(world_id, wd)
    log.info("location_generated", world_id=world_id, name=result.get("name"))
    return result
