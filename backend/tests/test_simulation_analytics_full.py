"""Tests for app.simulation.analytics — get_world_report and get_event_timeline."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.simulation.analytics import get_event_timeline, get_world_report


@pytest.fixture
def analytics_gq():
    gq = MagicMock()
    gq.get_events_in_range = AsyncMock(return_value=[
        {"day": 3, "description": "Storm hit", "type": "weather"},
        {"day": 4, "description": "Market opened", "type": "trade"},
    ])
    gq.get_all_relationships = AsyncMock(return_value=[
        {"from_name": "Ava", "to_name": "Bob", "sentiment": 0.8, "reason": "friends"},
        {"from_name": "Carl", "to_name": "Dan", "sentiment": -0.7, "reason": "rivalry"},
    ])
    gq.get_active_scenarios = AsyncMock(return_value=[
        {"title": "Goblin Raid", "tension_level": "high"},
    ])
    gq.get_completed_scenarios = AsyncMock(return_value=[
        {"title": "Lost Artifact"},
    ])
    gq.get_dead_npcs = AsyncMock(return_value=[
        {"name": "Ghost", "occupation": "thief"},
    ])
    gq.get_npc_stats_summary = AsyncMock(return_value={
        "total": 10, "alive": 9, "dead": 1, "avg_gold": 12.0,
    })
    gq.get_world_day = AsyncMock(return_value=10)
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
        {"id": "npc-2", "name": "Bob"},
    ])
    return gq


@pytest.mark.asyncio
async def test_get_world_report_structure(analytics_gq):
    """get_world_report should return dict with expected top-level keys."""
    with patch("app.simulation.analytics.get_recent_memories", return_value=[]):
        report = await get_world_report(analytics_gq, from_day=1, to_day=10)

    assert report["world_day"] == 10
    assert report["period"] == {"from_day": 1, "to_day": 10}
    assert len(report["events"]) == 2
    assert len(report["deaths"]) == 1
    assert report["npc_stats"]["total"] == 10


@pytest.mark.asyncio
async def test_get_world_report_alliances_and_rivalries(analytics_gq):
    """Report should categorize relationships into alliances and rivalries."""
    with patch("app.simulation.analytics.get_recent_memories", return_value=[]):
        report = await get_world_report(analytics_gq, from_day=1, to_day=10)

    rels = report["relationships"]
    assert rels["total"] == 2
    assert len(rels["alliances"]) == 1
    assert rels["alliances"][0]["from"] == "Ava"
    assert len(rels["rivalries"]) == 1
    assert rels["rivalries"][0]["from"] == "Carl"


@pytest.mark.asyncio
async def test_get_world_report_scenarios(analytics_gq):
    """Report should include active and completed scenarios."""
    with patch("app.simulation.analytics.get_recent_memories", return_value=[]):
        report = await get_world_report(analytics_gq, from_day=1, to_day=10)

    assert len(report["scenarios"]["active"]) == 1
    assert report["scenarios"]["active"][0]["title"] == "Goblin Raid"
    assert len(report["scenarios"]["completed"]) == 1


@pytest.mark.asyncio
async def test_get_world_report_notable_memories(analytics_gq):
    """Report should include notable NPC memories."""
    with patch("app.simulation.analytics.get_recent_memories", return_value=[
        "Day 5: Fought a wolf",
    ]):
        report = await get_world_report(analytics_gq, from_day=1, to_day=10)

    assert len(report["notable_memories"]) > 0


@pytest.mark.asyncio
async def test_get_event_timeline_returns_sorted_list(analytics_gq):
    """get_event_timeline should return chronologically sorted entries."""
    result = await get_event_timeline(analytics_gq, limit=50)

    assert isinstance(result, list)
    # Should have events + deaths
    assert len(result) >= 2
    # Deaths are appended with day=None which sorts as 0
    days = [e["day"] or 0 for e in result]
    assert days == sorted(days)


@pytest.mark.asyncio
async def test_get_event_timeline_includes_deaths(analytics_gq):
    """Timeline should include death entries."""
    result = await get_event_timeline(analytics_gq, limit=50)

    death_entries = [e for e in result if e["type"] == "death"]
    assert len(death_entries) == 1
    assert "Ghost" in death_entries[0]["description"]


@pytest.mark.asyncio
async def test_get_event_timeline_respects_limit(analytics_gq):
    """Timeline should limit event entries to the limit parameter."""
    analytics_gq.get_events_in_range = AsyncMock(return_value=[
        {"day": i, "description": f"Event {i}", "type": "event"}
        for i in range(100)
    ])

    result = await get_event_timeline(analytics_gq, limit=5)

    # events capped at 5 + deaths
    event_entries = [e for e in result if e["type"] != "death"]
    assert len(event_entries) <= 5


@pytest.mark.asyncio
async def test_get_event_timeline_empty_world():
    """Timeline for empty world should still work."""
    gq = MagicMock()
    gq.get_world_day = AsyncMock(return_value=1)
    gq.get_events_in_range = AsyncMock(return_value=[])
    gq.get_dead_npcs = AsyncMock(return_value=[])

    result = await get_event_timeline(gq, limit=50)
    assert result == []
