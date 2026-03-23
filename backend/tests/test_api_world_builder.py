"""Tests for app.api.world_builder — World Builder CRUD + AI generation."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from app.api.world_builder import world_builder_router


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(world_builder_router)
    return app


@pytest.fixture
def world_fs(tmp_path):
    """Patch _worlds_root to use a temp directory; pre-create one world."""
    worlds_root = tmp_path / "custom_worlds"
    worlds_root.mkdir()

    # Pre-create a world called "demo"
    demo_dir = worlds_root / "demo123"
    demo_dir.mkdir()
    (demo_dir / "meta.json").write_text(
        json.dumps({"name": "Demo World", "description": "A test world."}), encoding="utf-8"
    )
    (demo_dir / "world.json").write_text(
        json.dumps({
            "locations": [{"id": "loc-abc", "name": "Tavern", "type": "tavern", "description": "Cozy."}],
            "connections": [],
            "factions": [],
            "items": [],
        }), encoding="utf-8"
    )
    (demo_dir / "npcs.json").write_text(
        json.dumps({"npcs": [{"id": "npc-001", "name": "Elara", "mood": "neutral"}]}), encoding="utf-8"
    )

    with patch("app.api.world_builder._worlds_root", return_value=worlds_root), \
         patch("app.api.world_builder.settings") as mock_settings:
        mock_settings.data_dir = tmp_path
        yield worlds_root


# ── World CRUD ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_worlds(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/worlds")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Demo World"
    assert data[0]["id"] == "demo123"


@pytest.mark.asyncio
async def test_create_world(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/worlds", json={"name": "New Realm", "description": "Fresh."})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "New Realm"
    assert "id" in data
    # Verify files were created
    wdir = world_fs / data["id"]
    assert wdir.exists()
    assert (wdir / "meta.json").exists()
    assert (wdir / "world.json").exists()
    assert (wdir / "npcs.json").exists()


@pytest.mark.asyncio
async def test_get_world(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/worlds/demo123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Demo World"
    assert data["id"] == "demo123"
    assert len(data["world"]["locations"]) == 1


@pytest.mark.asyncio
async def test_get_world_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/worlds/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_world(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/demo123")
    assert resp.status_code == 200
    assert not (world_fs / "demo123").exists()


@pytest.mark.asyncio
async def test_delete_world_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/nonexistent")
    assert resp.status_code == 404


# ── Locations ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_locations(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/worlds/demo123/locations")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tavern"


@pytest.mark.asyncio
async def test_create_location(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/worlds/demo123/locations", json={
            "name": "Dark Forest", "type": "forest", "description": "Scary."
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Dark Forest"
    assert data["id"].startswith("loc-")


@pytest.mark.asyncio
async def test_update_location(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/api/worlds/demo123/locations/loc-abc", json={"name": "Renamed Tavern"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed Tavern"


@pytest.mark.asyncio
async def test_update_location_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/api/worlds/demo123/locations/loc-nope", json={"name": "X"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_location(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/demo123/locations/loc-abc")
        assert resp.status_code == 200
        # Verify it's gone
        resp2 = await ac.get("/api/worlds/demo123/locations")
        assert len(resp2.json()) == 0


@pytest.mark.asyncio
async def test_delete_location_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/demo123/locations/loc-nope")
    assert resp.status_code == 404


# ── Connections ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_connection(world_fs):
    # Add a second location first
    wd = json.loads((world_fs / "demo123" / "world.json").read_text(encoding="utf-8"))
    wd["locations"].append({"id": "loc-xyz", "name": "Market", "type": "market", "description": ""})
    (world_fs / "demo123" / "world.json").write_text(json.dumps(wd), encoding="utf-8")

    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/worlds/demo123/connections", json={
            "from_id": "loc-abc", "to_id": "loc-xyz", "distance": 2,
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["from"] == "loc-abc"
    assert data["distance"] == 2


@pytest.mark.asyncio
async def test_create_connection_invalid_loc(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/worlds/demo123/connections", json={
            "from_id": "loc-abc", "to_id": "loc-nope",
        })
    assert resp.status_code == 400


# ── NPCs ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_npcs(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/worlds/demo123/npcs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Elara"


@pytest.mark.asyncio
async def test_create_npc(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/worlds/demo123/npcs", json={
            "name": "Borin", "personality": "stoic", "occupation": "blacksmith", "age": 45,
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Borin"
    assert data["id"].startswith("npc-")
    assert data["alive"] is True


@pytest.mark.asyncio
async def test_update_npc(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/api/worlds/demo123/npcs/npc-001", json={"mood": "happy"})
    assert resp.status_code == 200
    assert resp.json()["mood"] == "happy"


@pytest.mark.asyncio
async def test_update_npc_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.put("/api/worlds/demo123/npcs/npc-nope", json={"mood": "x"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_npc(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/demo123/npcs/npc-001")
        assert resp.status_code == 200
        # Verify gone
        resp2 = await ac.get("/api/worlds/demo123/npcs")
        assert len(resp2.json()) == 0


@pytest.mark.asyncio
async def test_delete_npc_not_found(world_fs):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.delete("/api/worlds/demo123/npcs/npc-nope")
    assert resp.status_code == 404


# ── AI Generation ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_npc(world_fs):
    generated = {"name": "Zara", "personality": "brave", "backstory": "...", "goals": ["glory"],
                 "mood": "neutral", "occupation": "knight", "age": 28, "archetype": "hero",
                 "race": "human", "class": "paladin"}
    with patch("app.api.world_builder.generate_json", new_callable=AsyncMock, return_value=generated):
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/worlds/demo123/generate/npc", json={"description": "A brave knight"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Zara"
    assert data["id"].startswith("npc-")


@pytest.mark.asyncio
async def test_generate_npc_llm_failure(world_fs):
    with patch("app.api.world_builder.generate_json", new_callable=AsyncMock, return_value=None):
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/worlds/demo123/generate/npc", json={"description": "test"})
    assert resp.status_code == 500


@pytest.mark.asyncio
async def test_generate_location(world_fs):
    generated = {"name": "Crystal Cave", "type": "cave", "description": "Sparkling walls."}
    with patch("app.api.world_builder.generate_json", new_callable=AsyncMock, return_value=generated):
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/worlds/demo123/generate/location", json={"description": "A cave"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Crystal Cave"
    assert data["id"].startswith("loc-")


@pytest.mark.asyncio
async def test_load_world(world_fs):
    with patch("app.api.world_builder.get_driver", return_value=MagicMock()), \
         patch("app.api.world_builder.seed_world", new_callable=AsyncMock):
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/worlds/demo123/load")
    assert resp.status_code == 200
    assert resp.json()["status"] == "loaded"


@pytest.mark.asyncio
async def test_load_world_not_found(world_fs):
    with patch("app.api.world_builder.get_driver", return_value=MagicMock()):
        app = _make_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/worlds/nonexistent/load")
    assert resp.status_code == 404
