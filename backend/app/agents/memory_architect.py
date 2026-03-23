"""Memory Architect — smart consolidation, decay, and collective location memory.

Prevents memory bloat in long simulations while preserving important events.
Traumatic memories persist; mundane ones fade and get consolidated via LLM.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("memory_architect")


class MemoryArchitect:
    """Manages NPC memory lifecycle: consolidation, decay, and location memory."""

    def __init__(self):
        self._consolidate_agent = BaseAgent("memory_consolidate.j2")

    async def consolidate_npc(self, npc_id: str, npc_name: str) -> int:
        """Compress old low-importance memories into summaries via LLM.

        Returns number of memories consolidated.
        """
        from app.models.memory import get_old_memories, mark_summarized, add_memory

        old = get_old_memories(npc_id, limit=20)
        if len(old) < 10:
            return 0

        # Split: keep traumatic memories (importance >= 0.8), consolidate the rest
        to_consolidate = [m for m in old if m["importance"] < 0.8]
        if len(to_consolidate) < 5:
            return 0

        result = await self._consolidate_agent.generate_json(
            npc_name=npc_name,
            memories=to_consolidate,
        )

        summary = result.get("summary")
        if not summary:
            return 0

        # Mark originals as summarized
        ids = [m["id"] for m in to_consolidate]
        mark_summarized(ids)

        # Add consolidated summary as new memory
        add_memory(
            npc_id,
            f"[Consolidated] {summary}",
            day=to_consolidate[-1].get("day", 0),
            importance=0.6,
        )

        log.info("memories_consolidated", npc=npc_name, count=len(ids))
        return len(ids)

    def decay_memories(self, npc_id: str, current_day: int) -> int:
        """Reduce importance of old memories. Trauma (>=0.9) is immune.

        Returns number of memories affected.
        """
        from app.models.memory import decay_importance
        return decay_importance(npc_id, current_day)

    async def build_location_memory(
        self, gq, location_id: str, location_name: str, world_day: int,
    ) -> str | None:
        """Build collective memory for a location from recent events and NPC actions.

        Returns summary string or None.
        """
        from app.models.memory import set_location_memory

        # Gather recent events at this location
        events = await gq.get_events_at_location(location_id, since_day=max(1, world_day - 10))
        npcs = await gq.get_npcs_at_location(location_id)

        if not events and not npcs:
            return None

        event_descs = [e.get("description", "") for e in events[:15]]
        npc_activities = [f"{n['name']}: {n.get('current_activity', 'idle')}" for n in npcs[:10]]

        # Simple rule-based summary (no LLM needed for collective memory)
        parts = []
        if event_descs:
            parts.append(f"Recent events: {'; '.join(event_descs[:5])}")
        if npc_activities:
            parts.append(f"People here: {', '.join(npc_activities[:5])}")

        summary = " | ".join(parts) if parts else None
        if summary:
            set_location_memory(location_id, summary, world_day)

        return summary


memory_architect = MemoryArchitect()
