"""Tests for app.models.memory — SQLite-based NPC memory storage."""

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def mem_db(tmp_path):
    """Patch memory module to use a temp DB, init tables, return the path."""
    db_path = tmp_path / "test_memories.db"

    with patch("app.models.memory._db_path", None), \
         patch("app.models.memory.settings") as mock_s, \
         patch("app.models.memory.encode", side_effect=lambda text: [0.1, 0.2, 0.3]), \
         patch("app.models.memory.find_most_relevant", side_effect=lambda q, embs, k: list(range(min(k, len(embs))))):
        mock_s.data_dir = tmp_path
        # Force re-init of path
        import app.models.memory as mem_mod
        mem_mod._db_path = db_path

        mem_mod.init_memory_db()
        yield mem_mod, db_path


# ── init_memory_db ───────────────────────────────────────────────────────

def test_init_creates_tables(mem_db):
    mem_mod, db_path = mem_db
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    assert "memories" in tables
    assert "location_memories" in tables


def test_init_idempotent(mem_db):
    """Calling init_memory_db twice should not fail."""
    mem_mod, _ = mem_db
    mem_mod.init_memory_db()  # second call — should be safe


# ── add_memory / get_recent_memories ─────────────────────────────────────

def test_add_and_get_recent(mem_db):
    mem_mod, _ = mem_db
    mid = mem_mod.add_memory("npc-1", "Saw a dragon.", day=1, importance=0.8)
    assert isinstance(mid, str) and len(mid) > 10  # UUID

    memories = mem_mod.get_recent_memories("npc-1", limit=10)
    assert len(memories) == 1
    assert memories[0] == "Saw a dragon."


def test_get_recent_respects_limit(mem_db):
    mem_mod, _ = mem_db
    for i in range(15):
        mem_mod.add_memory("npc-2", f"Memory {i}", day=i)
    memories = mem_mod.get_recent_memories("npc-2", limit=5)
    assert len(memories) == 5


def test_get_recent_empty(mem_db):
    mem_mod, _ = mem_db
    assert mem_mod.get_recent_memories("npc-unknown") == []


def test_get_recent_excludes_summarized(mem_db):
    mem_mod, _ = mem_db
    m1 = mem_mod.add_memory("npc-3", "Old memory", day=1)
    mem_mod.add_memory("npc-3", "New memory", day=2)
    mem_mod.mark_summarized([m1])
    memories = mem_mod.get_recent_memories("npc-3")
    assert len(memories) == 1
    assert memories[0] == "New memory"


# ── search_memories ──────────────────────────────────────────────────────

def test_search_memories(mem_db):
    mem_mod, _ = mem_db
    mem_mod.add_memory("npc-s", "Dragon attacked village.")
    mem_mod.add_memory("npc-s", "Bought bread at market.")
    results = mem_mod.search_memories("npc-s", "dragon", top_k=1)
    assert len(results) == 1


def test_search_memories_no_data(mem_db):
    mem_mod, _ = mem_db
    results = mem_mod.search_memories("npc-empty", "anything")
    assert results == []


# ── get_memory_count ─────────────────────────────────────────────────────

def test_memory_count(mem_db):
    mem_mod, _ = mem_db
    assert mem_mod.get_memory_count("npc-c") == 0
    mem_mod.add_memory("npc-c", "First")
    mem_mod.add_memory("npc-c", "Second")
    assert mem_mod.get_memory_count("npc-c") == 2


# ── mark_summarized ──────────────────────────────────────────────────────

def test_mark_summarized(mem_db):
    mem_mod, _ = mem_db
    m1 = mem_mod.add_memory("npc-m", "Mem 1")
    m2 = mem_mod.add_memory("npc-m", "Mem 2")
    mem_mod.mark_summarized([m1])
    assert mem_mod.get_memory_count("npc-m") == 1  # only m2 left unsummarized


def test_mark_summarized_empty(mem_db):
    mem_mod, _ = mem_db
    mem_mod.mark_summarized([])  # should not raise


# ── get_old_memories ─────────────────────────────────────────────────────

def test_get_old_memories(mem_db):
    mem_mod, _ = mem_db
    mem_mod.add_memory("npc-o", "Old one", day=1)
    mem_mod.add_memory("npc-o", "New one", day=10)
    old = mem_mod.get_old_memories("npc-o", limit=1)
    assert len(old) == 1
    assert old[0]["content"] == "Old one"
    assert "id" in old[0]
    assert old[0]["day"] == 1


# ── purge_old_summarized ─────────────────────────────────────────────────

def test_purge_old_summarized(mem_db):
    mem_mod, _ = mem_db
    ids = []
    for i in range(10):
        mid = mem_mod.add_memory("npc-p", f"Mem {i}", day=i)
        ids.append(mid)
    mem_mod.mark_summarized(ids)
    deleted = mem_mod.purge_old_summarized("npc-p", keep=3)
    assert deleted == 7


def test_purge_nothing_to_delete(mem_db):
    mem_mod, _ = mem_db
    mid = mem_mod.add_memory("npc-pk", "Only one", day=1)
    mem_mod.mark_summarized([mid])
    deleted = mem_mod.purge_old_summarized("npc-pk", keep=5)
    assert deleted == 0


# ── decay_importance ─────────────────────────────────────────────────────

def test_decay_importance_reduces(mem_db):
    mem_mod, db_path = mem_db
    mem_mod.add_memory("npc-d", "Regular memory", day=1, importance=0.5)
    affected = mem_mod.decay_importance("npc-d", current_day=10, decay_rate=0.9)
    assert affected >= 1
    # Verify importance dropped
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT importance FROM memories WHERE npc_id = 'npc-d'").fetchone()
    conn.close()
    if row:
        assert row["importance"] < 0.5


def test_decay_skips_traumatic(mem_db):
    mem_mod, db_path = mem_db
    mem_mod.add_memory("npc-t", "Traumatic event", day=1, importance=0.95)
    affected = mem_mod.decay_importance("npc-t", current_day=20)
    # Traumatic (>= 0.9) should be immune
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT importance FROM memories WHERE npc_id = 'npc-t'").fetchone()
    conn.close()
    assert row["importance"] == 0.95  # unchanged


def test_decay_deletes_forgotten(mem_db):
    mem_mod, db_path = mem_db
    mem_mod.add_memory("npc-f", "Trivial thing", day=1, importance=0.15)
    affected = mem_mod.decay_importance("npc-f", current_day=100, decay_rate=0.5)
    # With very low importance and high age, should be deleted
    conn = sqlite3.connect(str(db_path))
    count = conn.execute("SELECT COUNT(*) FROM memories WHERE npc_id = 'npc-f'").fetchone()[0]
    conn.close()
    assert count == 0


# ── clear_all_memories ───────────────────────────────────────────────────

def test_clear_all(mem_db):
    mem_mod, db_path = mem_db
    mem_mod.add_memory("npc-x", "Data 1")
    mem_mod.add_memory("npc-y", "Data 2")
    mem_mod.set_location_memory("loc-1", "summary", day=1)
    mem_mod.clear_all_memories()

    conn = sqlite3.connect(str(db_path))
    assert conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM location_memories").fetchone()[0] == 0
    conn.close()


# ── Location Memory ──────────────────────────────────────────────────────

def test_location_memory_set_get(mem_db):
    mem_mod, _ = mem_db
    assert mem_mod.get_location_memory("loc-1") is None
    mem_mod.set_location_memory("loc-1", "Busy market day.", day=5)
    assert mem_mod.get_location_memory("loc-1") == "Busy market day."


def test_location_memory_overwrite(mem_db):
    mem_mod, _ = mem_db
    mem_mod.set_location_memory("loc-2", "Old summary", day=1)
    mem_mod.set_location_memory("loc-2", "New summary", day=2)
    assert mem_mod.get_location_memory("loc-2") == "New summary"
