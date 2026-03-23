"""Tests for API routes — action, dialogue, look endpoints."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_player(**overrides) -> dict:
    base = {
        "id": "player-1",
        "name": "Hero",
        "reputation": 0,
        "gold": 50,
        "level": 1,
        "class_id": "fighter",
        "current_hp": 12,
        "max_hp": 12,
        "ac": 14,
        "day": 1,
        "xp": 0,
    }
    base.update(overrides)
    return base


def _make_npc(npc_id="npc-1", name="Goran", **overrides) -> dict:
    base = {
        "id": npc_id,
        "name": name,
        "personality": "friendly",
        "backstory": "A local blacksmith",
        "goals": ["forge weapons"],
        "mood": "content",
        "occupation": "blacksmith",
        "age": 45,
        "alive": True,
        "level": 3,
        "max_hp": 20,
        "ac": 12,
    }
    base.update(overrides)
    return base


def _make_location(loc_id="loc-market", name="Market Square", **overrides) -> dict:
    base = {
        "id": loc_id,
        "name": name,
        "type": "market",
        "description": "A bustling market square",
    }
    base.update(overrides)
    return base


# ── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_gq(mock_graph_queries):
    """Pre-configured GraphQueries mock for route tests."""
    gq = mock_graph_queries
    gq.get_player.return_value = _make_player()
    gq.get_player_location.return_value = _make_location()
    gq.get_npcs_at_location.return_value = [_make_npc()]
    gq.get_dead_npcs_at_location.return_value = []
    gq.get_recent_events.return_value = []
    gq.get_player_items.return_value = []
    gq.get_connected_locations.return_value = []
    gq.get_player_reputation.return_value = 0
    gq.get_relationships.return_value = []
    return gq


@pytest.fixture
def client(mock_gq):
    """FastAPI TestClient with mocked dependencies."""
    with patch("app.api.routes._gq", return_value=mock_gq), \
         patch("app.api.routes._load_chat_log", return_value=[]), \
         patch("app.api.routes._save_chat_entry"):
        from app.api.routes import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        yield TestClient(app)


# ── Action Tests ─────────────────────────────────────────────────────────


class TestActionEndpoint:
    """Tests for POST /action."""

    @patch("app.api.routes.dm_agent")
    def test_action_basic(self, mock_dm, client, mock_gq):
        mock_dm.narrate = AsyncMock(return_value={
            "narration": "You look around the market.",
            "npcs_involved": ["npc-1"],
            "npcs_killed": [],
            "npcs_mood_changes": {},
            "items_changed": [],
            "items_gained": [],
            "items_lost": [],
            "location_changed": None,
            "reputation_changes": {},
            "player_hp_change": 0,
            "player_killed": False,
        })

        resp = client.post("/action", json={"action": "look around"})
        assert resp.status_code == 200
        data = resp.json()
        assert "narration" in data
        assert data["player_hp_change"] == 0
        assert data["player_killed"] is False

    @patch("app.api.routes.dm_agent")
    def test_action_with_lang(self, mock_dm, client, mock_gq):
        mock_dm.narrate = AsyncMock(return_value={
            "narration": "Вы осматриваетесь на рынке.",
            "npcs_involved": [],
            "npcs_killed": [],
            "npcs_mood_changes": {},
            "items_changed": [],
            "items_gained": [],
            "items_lost": [],
            "location_changed": None,
            "reputation_changes": {},
            "player_hp_change": 0,
            "player_killed": False,
        })

        resp = client.post("/action", json={"action": "look around", "lang": "ru"})
        assert resp.status_code == 200
        # Verify lang was passed to narrate
        call_kwargs = mock_dm.narrate.call_args.kwargs
        assert call_kwargs["lang"] == "ru"

    @patch("app.api.routes.dm_agent")
    def test_action_passes_dead_npcs(self, mock_dm, client, mock_gq):
        mock_gq.get_dead_npcs_at_location.return_value = [
            {"id": "npc-dead-1", "name": "Dead Guard", "occupation": "guard"}
        ]
        mock_dm.narrate = AsyncMock(return_value={
            "narration": "A dead guard lies on the ground.",
            "npcs_involved": [],
            "npcs_killed": [],
            "npcs_mood_changes": {},
            "items_changed": [],
            "items_gained": [],
            "items_lost": [],
            "location_changed": None,
            "reputation_changes": {},
            "player_hp_change": 0,
            "player_killed": False,
        })

        resp = client.post("/action", json={"action": "look at bodies"})
        assert resp.status_code == 200
        call_kwargs = mock_dm.narrate.call_args.kwargs
        assert len(call_kwargs["dead_npcs"]) == 1
        assert call_kwargs["dead_npcs"][0]["name"] == "Dead Guard"


# ── Dialogue Tests ───────────────────────────────────────────────────────


class TestDialogueEndpoint:
    """Tests for POST /dialogue."""

    @patch("app.api.routes.search_memories", return_value=[])
    @patch("app.api.routes.init_memory_db")
    @patch("app.api.routes.add_memory")
    @patch("app.api.routes.npc_agent")
    def test_dialogue_basic(self, mock_npc, mock_add_mem, mock_init_mem, mock_search, client, mock_gq):
        mock_gq.get_npc.return_value = _make_npc()
        mock_npc.dialogue = AsyncMock(return_value={
            "dialogue": "Welcome, traveler!",
            "mood_change": "same",
            "sentiment_change": 0.1,
            "internal_thought": "seems friendly",
        })

        resp = client.post("/dialogue", json={"npc_id": "npc-1", "message": "hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["npc_name"] == "Goran"
        assert data["dialogue"] == "Welcome, traveler!"

    @patch("app.api.routes.search_memories", return_value=[])
    @patch("app.api.routes.init_memory_db")
    @patch("app.api.routes.add_memory")
    @patch("app.api.routes.npc_agent")
    def test_dialogue_dead_npc(self, mock_npc, mock_add_mem, mock_init_mem, mock_search, client, mock_gq):
        mock_gq.get_npc.return_value = _make_npc(alive=False, mood="dead")

        resp = client.post("/dialogue", json={"npc_id": "npc-1", "message": "hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mood"] == "dead"
        assert "motionless" in data["dialogue"]

    @patch("app.api.routes.search_memories", return_value=[])
    @patch("app.api.routes.init_memory_db")
    @patch("app.api.routes.add_memory")
    @patch("app.api.routes.npc_agent")
    def test_dialogue_passes_lang(self, mock_npc, mock_add_mem, mock_init_mem, mock_search, client, mock_gq):
        mock_gq.get_npc.return_value = _make_npc()
        mock_npc.dialogue = AsyncMock(return_value={
            "dialogue": "Добро пожаловать!",
            "mood_change": "same",
            "sentiment_change": 0.0,
            "internal_thought": "interesting",
        })

        resp = client.post("/dialogue", json={"npc_id": "npc-1", "message": "привет", "lang": "ru"})
        assert resp.status_code == 200
        call_kwargs = mock_npc.dialogue.call_args.kwargs
        assert call_kwargs["lang"] == "ru"
        assert "recent_chat" in call_kwargs


# ── Look Tests ───────────────────────────────────────────────────────────


class TestLookEndpoint:
    """Tests for GET /look."""

    def test_look_basic(self, client, mock_gq):
        resp = client.get("/look")
        assert resp.status_code == 200
        data = resp.json()
        assert "location" in data
        assert "npcs" in data
        assert "dead_npcs" in data
        assert data["dead_npcs"] == []

    def test_look_with_dead_npcs(self, client, mock_gq):
        mock_gq.get_dead_npcs_at_location.return_value = [
            {"id": "npc-dead-1", "name": "Dead Guard", "occupation": "guard"}
        ]

        resp = client.get("/look")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["dead_npcs"]) == 1
        assert data["dead_npcs"][0]["name"] == "Dead Guard"
