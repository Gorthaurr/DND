"""SQLite disk cache to avoid re-generating already-processed prompts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class PromptCache:
    """Persistent prompt -> response cache backed by SQLite."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                prompt_hash  TEXT PRIMARY KEY,
                response_json TEXT NOT NULL,
                agent_type   TEXT NOT NULL,
                created_at   TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, prompt_hash: str) -> dict | None:
        """Get cached response by SHA-256 hash of rendered prompt."""
        row = self._conn.execute(
            "SELECT response_json FROM cache WHERE prompt_hash = ?",
            (prompt_hash,),
        ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def put(self, prompt_hash: str, agent_type: str, response: dict) -> None:
        """Store response in cache (upsert)."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO cache (prompt_hash, response_json, agent_type, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                prompt_hash,
                json.dumps(response, ensure_ascii=False),
                agent_type,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self._conn.commit()

    def has(self, prompt_hash: str) -> bool:
        """Check if prompt hash exists in cache."""
        row = self._conn.execute(
            "SELECT 1 FROM cache WHERE prompt_hash = ?",
            (prompt_hash,),
        ).fetchone()
        return row is not None

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def hash_prompt(rendered_prompt: str) -> str:
        """SHA-256 hash of prompt string."""
        return hashlib.sha256(rendered_prompt.encode("utf-8")).hexdigest()
