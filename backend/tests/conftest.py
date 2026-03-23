"""Shared fixtures for all tests."""

import sqlite3
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_graph_queries():
    """Mock GraphQueries with all async methods."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[])
    gq.get_npc = AsyncMock(return_value=None)
    gq.get_npc_location = AsyncMock(return_value={"id": "loc-tavern", "name": "Tavern", "description": "A cozy tavern."})
    gq.get_npcs_at_location = AsyncMock(return_value=[])
    gq.get_connected_locations = AsyncMock(return_value=[])
    gq.get_relationships = AsyncMock(return_value=[])
    gq.get_recent_events = AsyncMock(return_value=[])
    gq.update_npc = AsyncMock()
    gq.set_npc_location = AsyncMock()
    gq.set_relationship = AsyncMock()
    gq.transfer_gold = AsyncMock(return_value=True)
    gq.kill_npc = AsyncMock()
    gq.heal_npc = AsyncMock()
    gq.create_world_event = AsyncMock()
    gq.link_event_to_location = AsyncMock()
    gq.link_event_to_npc = AsyncMock()
    gq.increment_world_day = AsyncMock(return_value=1)
    gq.get_all_locations = AsyncMock(return_value=[])
    gq.get_active_scenarios = AsyncMock(return_value=[])
    return gq


@pytest.fixture
def sample_npc_attacker():
    return {
        "id": "npc-attacker",
        "name": "Goran",
        "level": 5,
        "current_hp": 30,
        "max_hp": 30,
        "gold": 10,
        "alive": True,
        "mood": "angry",
        "occupation": "hunter",
    }


@pytest.fixture
def sample_npc_defender():
    return {
        "id": "npc-defender",
        "name": "Finn",
        "level": 2,
        "current_hp": 15,
        "max_hp": 15,
        "gold": 5,
        "alive": True,
        "mood": "content",
        "occupation": "thief",
    }


@pytest.fixture
def memory_db(tmp_path):
    """Create a temporary SQLite memory database."""
    db_path = tmp_path / "test_memories.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            npc_id TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            day INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            summarized INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_npc ON memories(npc_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_day ON memories(day)")
    conn.commit()
    conn.close()
    return db_path
