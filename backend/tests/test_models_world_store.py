"""Tests for app.models.world_store — WorldStore file-based CRUD."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.world_store import WorldStore


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def store(tmp_path) -> WorldStore:
    """WorldStore backed by a temp directory."""
    return WorldStore(base_dir=tmp_path)


@pytest.fixture
def store_with_world(tmp_path) -> tuple[WorldStore, str]:
    """WorldStore with one pre-created world."""
    s = WorldStore(base_dir=tmp_path)
    world_id = s.create_world({
        "name": "Eldoria",
        "description": "A magical realm.",
        "locations": [{"id": "loc-castle", "name": "Castle", "type": "castle", "description": "Grand."}],
        "connections": [{"from": "loc-castle", "to": "loc-village", "distance": 1}],
        "factions": [{"id": "fac-guild", "name": "Mage Guild"}],
        "npcs": [{"id": "npc-wizard", "name": "Gandorf"}],
        "events": [{"id": "evt-1", "description": "Storm."}],
        "start_location": "loc-castle",
    })
    return s, world_id


# ── list_worlds ──────────────────────────────────────────────────────────

def test_list_worlds_empty(store):
    assert store.list_worlds() == []


def test_list_worlds(store_with_world):
    s, wid = store_with_world
    worlds = s.list_worlds()
    assert len(worlds) == 1
    assert worlds[0]["name"] == "Eldoria"
    assert worlds[0]["id"] == wid


# ── create_world ─────────────────────────────────────────────────────────

def test_create_world_returns_id(store):
    wid = store.create_world({"name": "Test", "description": "Desc"})
    assert isinstance(wid, str) and len(wid) > 0


def test_create_world_writes_files(store, tmp_path):
    wid = store.create_world({"name": "Files Test"})
    wdir = tmp_path / wid
    assert (wdir / "world.json").exists()
    assert (wdir / "npcs.json").exists()
    assert (wdir / "events.json").exists()


def test_create_world_with_id(store):
    wid = store.create_world({"id": "custom-id", "name": "Custom"})
    assert wid == "custom-id"


def test_create_world_stores_data(store):
    wid = store.create_world({
        "name": "Data World",
        "locations": [{"id": "loc-1", "name": "Place"}],
        "npcs": [{"id": "npc-1", "name": "Bob"}],
    })
    data = store.get_world(wid)
    assert data["name"] == "Data World"
    assert len(data["locations"]) == 1
    assert len(data["npcs"]) == 1


# ── get_world ────────────────────────────────────────────────────────────

def test_get_world_full(store_with_world):
    s, wid = store_with_world
    data = s.get_world(wid)
    assert data["id"] == wid
    assert data["name"] == "Eldoria"
    assert len(data["locations"]) == 1
    assert len(data["connections"]) == 1
    assert len(data["factions"]) == 1
    assert len(data["npcs"]) == 1
    assert len(data["events"]) == 1
    assert data["start_location"] == "loc-castle"


def test_get_world_not_found(store):
    assert store.get_world("nonexistent") is None


# ── update_world ─────────────────────────────────────────────────────────

def test_update_world(store_with_world):
    s, wid = store_with_world
    assert s.update_world(wid, {"name": "New Eldoria", "description": "Updated."})
    data = s.get_world(wid)
    assert data["name"] == "New Eldoria"
    assert data["description"] == "Updated."


def test_update_world_npcs(store_with_world):
    s, wid = store_with_world
    assert s.update_world(wid, {"npcs": [{"id": "npc-new", "name": "NewGuy"}]})
    data = s.get_world(wid)
    assert len(data["npcs"]) == 1
    assert data["npcs"][0]["name"] == "NewGuy"


def test_update_world_not_found(store):
    assert store.update_world("ghost", {"name": "Nope"}) is False


# ── delete_world ─────────────────────────────────────────────────────────

def test_delete_world(store_with_world):
    s, wid = store_with_world
    assert s.delete_world(wid) is True
    assert s.get_world(wid) is None


def test_delete_world_not_found(store):
    assert store.delete_world("ghost") is False


# ── Location CRUD ────────────────────────────────────────────────────────

def test_add_location(store_with_world):
    s, wid = store_with_world
    assert s.add_location(wid, {"name": "Market", "type": "market"})
    data = s.get_world(wid)
    assert len(data["locations"]) == 2
    new_loc = data["locations"][-1]
    assert new_loc["name"] == "Market"
    assert new_loc["id"].startswith("loc-")


def test_add_location_with_id(store_with_world):
    s, wid = store_with_world
    s.add_location(wid, {"id": "loc-custom", "name": "Custom Place"})
    data = s.get_world(wid)
    ids = [l["id"] for l in data["locations"]]
    assert "loc-custom" in ids


def test_update_location(store_with_world):
    s, wid = store_with_world
    assert s.update_location(wid, "loc-castle", {"description": "Enormous."})
    data = s.get_world(wid)
    assert data["locations"][0]["description"] == "Enormous."


def test_update_location_not_found(store_with_world):
    s, wid = store_with_world
    assert s.update_location(wid, "loc-nope", {"name": "X"}) is False


def test_delete_location_and_connections(store_with_world):
    s, wid = store_with_world
    assert s.delete_location(wid, "loc-castle")
    data = s.get_world(wid)
    assert len(data["locations"]) == 0
    # Connection referencing loc-castle should be removed too
    assert len(data["connections"]) == 0


# ── Connection CRUD ──────────────────────────────────────────────────────

def test_add_connection(store_with_world):
    s, wid = store_with_world
    s.add_connection(wid, "loc-castle", "loc-new", distance=3)
    data = s.get_world(wid)
    assert len(data["connections"]) == 2
    last_conn = data["connections"][-1]
    assert last_conn["distance"] == 3


# ── NPC CRUD ─────────────────────────────────────────────────────────────

def test_add_npc(store_with_world):
    s, wid = store_with_world
    s.add_npc(wid, {"name": "Elara", "occupation": "healer"})
    data = s.get_world(wid)
    assert len(data["npcs"]) == 2
    new_npc = data["npcs"][-1]
    assert new_npc["name"] == "Elara"
    assert new_npc["id"].startswith("npc-")


def test_update_npc(store_with_world):
    s, wid = store_with_world
    assert s.update_npc(wid, "npc-wizard", {"mood": "excited"})
    data = s.get_world(wid)
    assert data["npcs"][0]["mood"] == "excited"


def test_update_npc_not_found(store_with_world):
    s, wid = store_with_world
    assert s.update_npc(wid, "npc-nope", {"mood": "x"}) is False


def test_delete_npc(store_with_world):
    s, wid = store_with_world
    assert s.delete_npc(wid, "npc-wizard")
    data = s.get_world(wid)
    assert len(data["npcs"]) == 0


# ── _make_id ─────────────────────────────────────────────────────────────

def test_make_id_slug():
    slug = WorldStore._make_id("My Cool World")
    assert "my_cool_world" in slug
    assert len(slug) <= 50


def test_make_id_truncates_long_names():
    slug = WorldStore._make_id("A" * 100)
    assert len(slug) <= 50
