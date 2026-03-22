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


def clear_all_memories() -> None:
    """Delete all memories. Used for world reset."""
    conn = _get_connection()
    conn.execute("DELETE FROM memories")
    conn.commit()
    conn.close()
    log.warning("all_memories_cleared")
