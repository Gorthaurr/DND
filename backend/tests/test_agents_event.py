"""Tests for Event Agent."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


class TestEventAgentLoadPool:
    """Tests for EventAgent.load_event_pool()."""

    def test_load_event_pool_from_file(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "events.json"
            p.write_text(json.dumps({
                "events": [
                    {"type": "fire", "description": "Fire breaks out!"},
                    {"type": "weather", "description": "Heavy rain."},
                ]
            }))
            agent.load_event_pool(Path(td))
            assert len(agent._event_pool) == 2
            assert agent._event_pool[0]["type"] == "fire"

    def test_load_event_pool_missing_file(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        with tempfile.TemporaryDirectory() as td:
            agent.load_event_pool(Path(td))
            assert agent._event_pool == []

    def test_load_event_pool_empty_events(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "events.json"
            p.write_text(json.dumps({"events": []}))
            agent.load_event_pool(Path(td))
            assert agent._event_pool == []


class TestEventAgentGenerate:
    """Tests for EventAgent.generate()."""

    @pytest.mark.asyncio
    async def test_generate_with_llm(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._agent = AsyncMock()
        agent._agent.generate_json = AsyncMock(return_value={
            "events": [
                {"type": "weather", "description": "A storm brews", "severity": "medium", "location_id": "loc1"},
            ]
        })
        # Force LLM path by clearing pool
        agent._event_pool = []

        result = await agent.generate(
            world_day=5,
            locations=[{"id": "loc1", "name": "Village"}],
            recent_events=[],
            tensions=[],
            use_llm=True,
        )
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["type"] == "weather"
        assert result[0]["day"] == 5
        assert "id" in result[0]

    @pytest.mark.asyncio
    async def test_generate_fallback_no_llm(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._event_pool = [
            {"type": "fire", "description": "Fire!", "severity": "high"},
            {"type": "flood", "description": "Flood!", "severity": "low"},
        ]

        result = await agent.generate(
            world_day=1,
            locations=[{"id": "l1", "name": "V"}],
            recent_events=[],
            tensions=[],
            use_llm=False,
        )
        assert isinstance(result, list)
        # With use_llm=False, it picks from pool (0-2 events)
        for event in result:
            assert "description" in event
            assert "id" in event

    @pytest.mark.asyncio
    async def test_generate_empty_pool_no_llm(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._event_pool = []

        result = await agent.generate(
            world_day=1,
            locations=[],
            recent_events=[],
            tensions=[],
            use_llm=False,
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_generate_llm_failure_falls_back_to_pool(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._agent = AsyncMock()
        agent._agent.generate_json = AsyncMock(side_effect=RuntimeError("LLM down"))
        agent._event_pool = [
            {"type": "earthquake", "description": "Ground shakes!", "severity": "high"},
        ]

        result = await agent.generate(
            world_day=3,
            locations=[{"id": "l1", "name": "Town"}],
            recent_events=[],
            tensions=[],
            use_llm=True,
        )
        assert isinstance(result, list)


class TestEventAgentNormalize:
    """Tests for EventAgent._normalize_event()."""

    def test_normalize_event_fills_defaults(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        event = agent._normalize_event({}, world_day=7)
        assert event["day"] == 7
        assert event["description"] == "Something happened."
        assert event["type"] == "natural"
        assert event["severity"] == "low"
        assert event["affected_npc_ids"] == []
        assert event["id"].startswith("evt-")

    def test_normalize_event_preserves_values(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        raw = {
            "description": "Dragon attack!",
            "type": "combat",
            "location_id": "loc-castle",
            "severity": "critical",
            "affected_npc_ids": ["npc-1", "npc-2"],
        }
        event = agent._normalize_event(raw, world_day=10)
        assert event["description"] == "Dragon attack!"
        assert event["type"] == "combat"
        assert event["severity"] == "critical"
        assert event["location_id"] == "loc-castle"
        assert len(event["affected_npc_ids"]) == 2


class TestEventAgentPickFromPool:
    """Tests for EventAgent._pick_from_pool()."""

    def test_pick_from_empty_pool(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._event_pool = []
        result = agent._pick_from_pool(world_day=1)
        assert result == []

    def test_pick_from_pool_returns_list(self):
        from app.agents.event_agent import EventAgent

        agent = EventAgent()
        agent._event_pool = [
            {"type": "rain", "description": "It rains."},
            {"type": "sun", "description": "The sun shines."},
            {"type": "snow", "description": "It snows."},
        ]
        result = agent._pick_from_pool(world_day=5)
        assert isinstance(result, list)
        assert len(result) <= 2
        for event in result:
            assert "id" in event
            assert event["day"] == 5
