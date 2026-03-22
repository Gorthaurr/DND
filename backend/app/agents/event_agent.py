"""World event generation agent."""

import json
import random
import uuid
from pathlib import Path

from app.agents.base import BaseAgent
from app.config import settings
from app.utils.logger import get_logger

log = get_logger("event_agent")


class EventAgent:
    """Generates world events using LLM or event pool."""

    def __init__(self):
        self._agent = BaseAgent("event_generate.j2")
        self._event_pool: list[dict] = []

    def load_event_pool(self, world_dir: Path) -> None:
        """Load predefined events from the world preset."""
        events_file = world_dir / "events.json"
        if events_file.exists():
            with open(events_file, encoding="utf-8") as f:
                data = json.load(f)
                self._event_pool = data.get("events", [])
            log.info("event_pool_loaded", count=len(self._event_pool))

    async def generate(
        self,
        world_day: int,
        locations: list[dict],
        recent_events: list[str],
        tensions: list[str],
        use_llm: bool = True,
    ) -> list[dict]:
        """Generate world events for the current tick."""
        # 50% chance to use predefined events, 50% LLM-generated
        if not use_llm or (self._event_pool and random.random() < 0.5):
            return self._pick_from_pool(world_day)

        try:
            result = await self._agent.generate_json(
                world_day=world_day,
                locations=locations,
                recent_events=recent_events,
                tensions=tensions,
            )
            events = result.get("events", [])
            return [self._normalize_event(e, world_day) for e in events]
        except Exception as e:
            log.warning("llm_event_gen_failed", error=str(e))
            return self._pick_from_pool(world_day)

    def _pick_from_pool(self, world_day: int) -> list[dict]:
        """Pick 1-2 events from the predefined pool."""
        if not self._event_pool:
            return []
        count = random.randint(0, 2)
        picked = random.sample(self._event_pool, min(count, len(self._event_pool)))
        return [self._normalize_event(e, world_day) for e in picked]

    def _normalize_event(self, event: dict, world_day: int) -> dict:
        return {
            "id": f"evt-{uuid.uuid4().hex[:8]}",
            "day": world_day,
            "description": event.get("description", "Something happened."),
            "type": event.get("type", "natural"),
            "location_id": event.get("location_id", ""),
            "severity": event.get("severity", "low"),
            "affected_npc_ids": event.get("affected_npc_ids", []),
        }


event_agent = EventAgent()
