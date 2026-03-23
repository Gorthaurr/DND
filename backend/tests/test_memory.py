"""Tests for NPC memory system."""

import json
import sqlite3
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest


def _insert_memory(db_path, npc_id: str, content: str, day: int = 0, embedding: list | None = None, summarized: int = 0):
    """Helper: insert memory directly into DB."""
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO memories (id, npc_id, content, embedding, importance, day, created_at, summarized) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), npc_id, content, json.dumps(embedding or [0.0] * 10), 0.5, day, datetime.utcnow().isoformat(), summarized),
    )
    conn.commit()
    conn.close()


def _count_memories(db_path, npc_id: str, summarized: int | None = None) -> int:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    if summarized is not None:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM memories WHERE npc_id = ? AND summarized = ?", (npc_id, summarized))
    else:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM memories WHERE npc_id = ?", (npc_id,))
    count = cur.fetchone()["cnt"]
    conn.close()
    return count


class TestMemoryStorage:
    def test_add_and_retrieve(self, memory_db):
        """add_memory stores and get_recent_memories retrieves."""
        with patch("app.models.memory._get_db_path", return_value=memory_db), \
             patch("app.utils.embeddings.encode", return_value=[0.1] * 10):
            from app.models.memory import add_memory, get_recent_memories

            add_memory("npc-1", "Met the blacksmith", day=1)
            add_memory("npc-1", "Bought a sword", day=2)

            memories = get_recent_memories("npc-1", limit=10)
            assert len(memories) == 2
            assert "Bought a sword" in memories[0]  # most recent first

    def test_mark_summarized_hides(self, memory_db):
        """Summarized memories don't appear in get_recent_memories."""
        _insert_memory(memory_db, "npc-1", "Old memory", day=1)
        _insert_memory(memory_db, "npc-1", "New memory", day=5)

        with patch("app.models.memory._get_db_path", return_value=memory_db):
            from app.models.memory import get_recent_memories, mark_summarized

            # Get IDs of old memories
            conn = sqlite3.connect(str(memory_db))
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT id FROM memories WHERE npc_id = 'npc-1' AND day = 1").fetchall()
            old_ids = [r["id"] for r in rows]
            conn.close()

            mark_summarized(old_ids)

            memories = get_recent_memories("npc-1", limit=10)
            assert len(memories) == 1
            assert "New memory" in memories[0]

    def test_memory_count(self, memory_db):
        """get_memory_count returns count of unsummarized memories."""
        _insert_memory(memory_db, "npc-1", "Active 1", summarized=0)
        _insert_memory(memory_db, "npc-1", "Active 2", summarized=0)
        _insert_memory(memory_db, "npc-1", "Old summarized", summarized=1)

        with patch("app.models.memory._get_db_path", return_value=memory_db):
            from app.models.memory import get_memory_count

            count = get_memory_count("npc-1")
            assert count == 2

    def test_get_old_memories_order(self, memory_db):
        """get_old_memories returns oldest first."""
        _insert_memory(memory_db, "npc-1", "Oldest memory", day=1)
        _insert_memory(memory_db, "npc-1", "Middle memory", day=5)
        _insert_memory(memory_db, "npc-1", "Newest memory", day=10)

        with patch("app.models.memory._get_db_path", return_value=memory_db):
            from app.models.memory import get_old_memories

            old = get_old_memories("npc-1", limit=2)
            assert len(old) == 2
            assert "Oldest memory" in old[0]["content"]

    def test_different_npcs_isolated(self, memory_db):
        """Memories from different NPCs don't overlap."""
        _insert_memory(memory_db, "npc-1", "NPC1 memory")
        _insert_memory(memory_db, "npc-2", "NPC2 memory")

        with patch("app.models.memory._get_db_path", return_value=memory_db):
            from app.models.memory import get_recent_memories

            mem1 = get_recent_memories("npc-1")
            mem2 = get_recent_memories("npc-2")
            assert len(mem1) == 1
            assert len(mem2) == 1
            assert "NPC1" in mem1[0]
            assert "NPC2" in mem2[0]
