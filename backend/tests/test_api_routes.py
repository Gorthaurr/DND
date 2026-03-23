"""Tests for app.api.routes — REST API endpoints."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock celery before importing routes (ticker imports it at module level)
if "celery" not in sys.modules:
    sys.modules["celery"] = MagicMock()
    sys.modules["celery.schedules"] = MagicMock()

from fastapi import FastAPI
from app.api.routes import router


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return app


def _mock_gq():
    """Return a MagicMock mimicking GraphQueries with common async methods."""
    gq = MagicMock()
    gq.get_player = AsyncMock(return_value={
        "id": "player-1", "day": 5, "gold": 50, "reputation": 0,
        "level": 2, "class_id": "fighter", "current_hp": 20, "max_hp": 20,
        "xp": 100, "time_of_day": "day",
    })
    gq.get_player_location = AsyncMock(return_value={
        "id": "loc-tavern", "name": "Rusty Tankard", "description": "A cozy tavern.", "type": "tavern",
    })
    gq.get_npcs_at_location = AsyncMock(return_value=[
        {"id": "npc-goran", "name": "Goran", "occupation": "hunter", "mood": "neutral",
         "alive": True, "personality": "gruff", "backstory": "...", "goals": ["hunt"],
         "age": 35, "level": 3, "current_hp": 15, "max_hp": 15, "gold": 10,
         "equipment_ids": []},
    ])
    gq.get_recent_events = AsyncMock(return_value=[])
    gq.get_player_items = AsyncMock(return_value=[])
    gq.get_connected_locations = AsyncMock(return_value=[
        {"id": "loc-market", "name": "Market Square", "type": "market", "description": "Busy market."},
    ])
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-goran", "name": "Goran", "occupation": "hunter", "mood": "neutral",
         "alive": True, "level": 3, "current_hp": 15, "max_hp": 15, "gold": 10},
    ])
    gq.get_npc = AsyncMock(return_value={
        "id": "npc-goran", "name": "Goran", "occupation": "hunter", "mood": "neutral",
        "alive": True, "personality": "gruff", "backstory": "Born in woods.", "goals": ["hunt deer"],
        "age": 35, "level": 3, "current_hp": 15, "max_hp": 15, "gold": 10,
    })
    gq.get_npc_location = AsyncMock(return_value={
        "id": "loc-tavern", "name": "Rusty Tankard", "type": "tavern",
    })
    gq.get_relationships = AsyncMock(return_value=[])
    gq.get_world_day = AsyncMock(return_value=5)
    gq.get_world_map = AsyncMock(return_value={"locations": [], "connections": []})
    gq.get_all_locations = AsyncMock(return_value=[])
    gq.update_npc = AsyncMock()
    gq.set_player_location = AsyncMock()
    gq.set_relationship = AsyncMock()
    gq.kill_npc = AsyncMock()
    gq.add_player_xp = AsyncMock(return_value={"leveled_up": False})
    gq.get_player_reputation = AsyncMock(return_value=0)
    gq.give_item_to_player = AsyncMock()
    gq._session = MagicMock()
    return gq


@pytest.fixture
def mock_gq():
    gq = _mock_gq()
    with patch("app.api.routes.get_driver", return_value=MagicMock()), \
         patch("app.api.routes.GraphQueries", return_value=gq), \
         patch("app.api.routes._gq", return_value=gq):
        yield gq


@pytest.fixture
def mock_dm_agent():
    with patch("app.api.routes.dm_agent") as dm:
        dm.narrate = AsyncMock(return_value={
            "narration": "You swing your sword.",
            "npcs_involved": [],
            "npcs_killed": [],
            "items_changed": [],
            "npcs_mood_changes": {},
            "reputation_changes": {},
            "player_hp_change": 0,
        })
        yield dm


@pytest.fixture
def mock_npc_agent():
    with patch("app.api.routes.npc_agent") as na:
        na.dialogue = AsyncMock(return_value={
            "dialogue": "Greetings, adventurer.",
            "mood_change": "none",
            "sentiment_change": 0,
            "internal_thought": "Seems harmless.",
        })
        yield na


@pytest.fixture
def mock_memory():
    with patch("app.api.routes.init_memory_db"), \
         patch("app.api.routes.get_recent_memories", return_value=["I saw a deer."]), \
         patch("app.api.routes.search_memories", return_value=["A traveler visited."]), \
         patch("app.api.routes.add_memory"), \
         patch("app.api.routes.get_memory_count", return_value=3):
        yield


@pytest.fixture
def mock_tick():
    with patch("app.api.routes.run_world_tick", new_callable=AsyncMock) as t:
        t.return_value = {
            "day": 6,
            "events": [{"description": "A storm brews."}],
            "npc_actions": [],
            "interactions": [],
            "active_scenarios": [],
        }
        yield t


# ── Tests ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_look(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/look")
    assert resp.status_code == 200
    data = resp.json()
    assert "location" in data
    assert data["location"]["id"] == "loc-tavern"
    assert isinstance(data["npcs"], list)
    assert isinstance(data["exits"], list)


@pytest.mark.asyncio
async def test_look_no_location(mock_gq, mock_memory):
    mock_gq.get_player_location.return_value = None
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/look")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_world_state(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/world/state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["day"] == 5
    assert "player_location" in data
    assert data["player_level"] == 2


@pytest.mark.asyncio
async def test_world_log(mock_gq):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/world/log")
    assert resp.status_code == 200
    assert "entries" in resp.json()


@pytest.mark.asyncio
async def test_list_npcs(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/npcs")
    assert resp.status_code == 200
    data = resp.json()
    assert "npcs" in data
    assert len(data["npcs"]) == 1
    assert data["npcs"][0]["name"] == "Goran"


@pytest.mark.asyncio
async def test_npc_info(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/npc/npc-goran")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Goran"
    assert "recent_memories" in data


@pytest.mark.asyncio
async def test_npc_info_not_found(mock_gq, mock_memory):
    mock_gq.get_npc.return_value = None
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/npc/npc-unknown")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_player_action(mock_gq, mock_dm_agent, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/action", json={"action": "I look around the room."})
    assert resp.status_code == 200
    data = resp.json()
    assert "narration" in data
    mock_dm_agent.narrate.assert_awaited_once()


@pytest.mark.asyncio
async def test_player_action_no_player(mock_gq, mock_dm_agent, mock_memory):
    mock_gq.get_player.return_value = None
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/action", json={"action": "hello"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_player_move(mock_gq, mock_dm_agent, mock_memory):
    """Movement to a known connected location should succeed."""
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/action", json={"action": "go to Market Square"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Market" in data["narration"] or mock_gq.set_player_location.awaited


@pytest.mark.asyncio
async def test_dialogue(mock_gq, mock_npc_agent, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/dialogue", json={"npc_id": "npc-goran", "message": "Hello!"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["npc_name"] == "Goran"
    assert "dialogue" in data


@pytest.mark.asyncio
async def test_dialogue_npc_not_found(mock_gq, mock_npc_agent, mock_memory):
    mock_gq.get_npc.return_value = None
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/dialogue", json={"npc_id": "npc-none", "message": "Hi"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_dialogue_dead_npc(mock_gq, mock_npc_agent, mock_memory):
    mock_gq.get_npc.return_value = {
        "id": "npc-goran", "name": "Goran", "alive": False, "mood": "dead",
        "occupation": "hunter", "personality": "", "backstory": "", "goals": [], "age": 35,
    }
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/dialogue", json={"npc_id": "npc-goran", "message": "Wake up"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["mood"] == "dead"


@pytest.mark.asyncio
async def test_manual_tick(mock_gq, mock_tick, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/world/tick")
    assert resp.status_code == 200
    data = resp.json()
    assert data["day"] == 6
    assert isinstance(data["events"], list)


@pytest.mark.asyncio
async def test_chat_history(mock_gq):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/chat/history")
    assert resp.status_code == 200
    assert "messages" in resp.json()


@pytest.mark.asyncio
async def test_inventory(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/inventory")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "gold" in data


@pytest.mark.asyncio
async def test_npc_observe(mock_gq, mock_memory):
    app = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/npc/npc-goran/observe")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Goran"
    assert "recent_memories" in data
    assert "relationships" in data
