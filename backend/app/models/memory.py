"""NPC memory storage using SQLite + embeddings for semantic search."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.utils.embeddings import encode, find_most_relevant
from app.utils.logger import get_logger

log = get_logger("memory")

_db_path: Path | None = None


def _get_db_path() -> Path:
    global _db_path
    if _db_path is None:
        _db_path = settings.data_dir / "memories.db"
        _db_path.parent.mkdir(parents=True, exist_ok=True)
    return _db_path


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_memory_db() -> None:
    """Create memory tables if they don't exist."""
    conn = _get_connection()
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS location_memories (
            location_id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            day INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    log.info("memory_db_initialized")


def add_memory(npc_id: str, content: str, day: int = 0, importance: float = 0.5) -> str:
    """Store a new memory for an NPC with embedding."""
    memory_id = str(uuid.uuid4())
    embedding = encode(content)

    conn = _get_connection()
    conn.execute(
        """
        INSERT INTO memories (id, npc_id, content, embedding, importance, day, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (memory_id, npc_id, content, json.dumps(embedding), importance, day, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return memory_id


def get_recent_memories(npc_id: str, limit: int = 10) -> list[str]:
    """Get most recent memories for an NPC."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT content FROM memories WHERE npc_id = ? AND summarized = 0 ORDER BY day DESC, created_at DESC LIMIT ?",
        (npc_id, limit),
    )
    memories = [row["content"] for row in cursor.fetchall()]
    conn.close()
    return memories


def search_memories(npc_id: str, query: str, top_k: int = 5) -> list[str]:
    """Search NPC memories by semantic similarity."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT content, embedding FROM memories WHERE npc_id = ? AND summarized = 0",
        (npc_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    contents = [row["content"] for row in rows]
    embeddings = [json.loads(row["embedding"]) for row in rows]
    query_emb = encode(query)

    indices = find_most_relevant(query_emb, embeddings, top_k)
    return [contents[i] for i in indices]


def get_memory_count(npc_id: str) -> int:
    """Count unsummarized memories for an NPC."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT COUNT(*) as cnt FROM memories WHERE npc_id = ? AND summarized = 0",
        (npc_id,),
    )
    count = cursor.fetchone()["cnt"]
    conn.close()
    return count


def get_old_memories(npc_id: str, limit: int = 20) -> list[dict]:
    """Get oldest unsummarized memories for summarization."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT id, content, day FROM memories WHERE npc_id = ? AND summarized = 0 ORDER BY day ASC, created_at ASC LIMIT ?",
        (npc_id, limit),
    )
    memories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return memories


def mark_summarized(memory_ids: list[str]) -> None:
    """Mark memories as summarized (they won't appear in recent/search)."""
    if not memory_ids:
        return
    conn = _get_connection()
    placeholders = ",".join("?" * len(memory_ids))
    conn.execute(f"UPDATE memories SET summarized = 1 WHERE id IN ({placeholders})", memory_ids)
    conn.commit()
    conn.close()


def purge_old_summarized(npc_id: str, keep: int = 50) -> int:
    """Delete excess summarized memories to prevent DB bloat. Returns count deleted."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT COUNT(*) as cnt FROM memories WHERE npc_id = ? AND summarized = 1",
        (npc_id,),
    )
    total = cursor.fetchone()["cnt"]
    if total <= keep:
        conn.close()
        return 0

    to_delete = total - keep
    cursor = conn.execute(
        "SELECT id FROM memories WHERE npc_id = ? AND summarized = 1 ORDER BY day ASC, created_at ASC LIMIT ?",
        (npc_id, to_delete),
    )
    ids = [row["id"] for row in cursor.fetchall()]
    if ids:
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", ids)
        conn.commit()
    conn.close()
    log.info("purged_old_summarized", npc_id=npc_id, deleted=len(ids))
    return len(ids)


def clear_all_memories() -> None:
    """Delete all memories. Used for world reset."""
    conn = _get_connection()
    conn.execute("DELETE FROM memories")
    conn.execute("DELETE FROM location_memories")
    conn.commit()
    conn.close()
    log.warning("all_memories_cleared")


# ── Location Memory ──────────────────────────────────────────

def get_location_memory(location_id: str) -> str | None:
    """Get collective memory summary for a location."""
    conn = _get_connection()
    cursor = conn.execute(
        "SELECT summary FROM location_memories WHERE location_id = ?",
        (location_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row["summary"] if row else None


def set_location_memory(location_id: str, summary: str, day: int) -> None:
    """Set or update collective memory for a location."""
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO location_memories (location_id, summary, day) VALUES (?, ?, ?)",
        (location_id, summary, day),
    )
    conn.commit()
    conn.close()


# ── Memory Decay ─────────────────────────────────────────────

def decay_importance(npc_id: str, current_day: int, decay_rate: float = 0.95) -> int:
    """Reduce importance of old memories over time.

    Trauma (importance >= 0.9 originally) is immune to decay.
    Memories with importance < 0.1 after decay are deleted (forgotten).
    Returns count of memories affected.
    """
    conn = _get_connection()
    # Decay non-traumatic, non-summarized memories older than 3 days
    cursor = conn.execute(
        """
        SELECT id, importance, day FROM memories
        WHERE npc_id = ? AND summarized = 0 AND importance < 0.9
        AND day < ?
        """,
        (npc_id, current_day - 3),
    )
    rows = cursor.fetchall()
    affected = 0
    to_delete = []
    for row in rows:
        age_days = current_day - row["day"]
        new_importance = row["importance"] * (decay_rate ** age_days)
        if new_importance < 0.1:
            to_delete.append(row["id"])
        else:
            conn.execute(
                "UPDATE memories SET importance = ? WHERE id = ?",
                (round(new_importance, 3), row["id"]),
            )
            affected += 1

    if to_delete:
        placeholders = ",".join("?" * len(to_delete))
        conn.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", to_delete)
        affected += len(to_delete)

    conn.commit()
    conn.close()
    return affected
