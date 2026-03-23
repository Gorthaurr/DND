"""Tests for app.simulation.events — process_events and summarize_old_memories."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.simulation.events import process_events


@pytest.mark.asyncio
async def test_process_events_creates_events(mock_graph_queries):
    """process_events should create world events in graph and return list."""
    gq = mock_graph_queries
    events = [
        {"description": "A storm approaches the village", "type": "weather"},
        {"description": "A merchant caravan arrives", "type": "trade", "location_id": "loc-market"},
    ]
    gq.get_npcs_at_location = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
    ])

    with patch("app.simulation.events.add_memory"):
        results = await process_events(gq, events, world_day=3)

    assert len(results) == 2
    assert gq.create_world_event.await_count == 2
    # First event has no location_id, so link_event_to_location should be called once
    assert gq.link_event_to_location.await_count == 1


@pytest.mark.asyncio
async def test_process_events_returns_event_data(mock_graph_queries):
    """Returned events should have id, day, description, type."""
    gq = mock_graph_queries
    events = [{"description": "Wolves spotted", "type": "danger"}]

    with patch("app.simulation.events.add_memory"):
        results = await process_events(gq, events, world_day=7)

    assert len(results) == 1
    r = results[0]
    assert r["day"] == 7
    assert r["description"] == "Wolves spotted"
    assert r["type"] == "danger"
    assert "id" in r


@pytest.mark.asyncio
async def test_process_events_empty_list(mock_graph_queries):
    """process_events with empty list should return empty list."""
    results = await process_events(mock_graph_queries, [], world_day=1)
    assert results == []
    mock_graph_queries.create_world_event.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_events_notifies_npcs_at_location(mock_graph_queries):
    """NPCs at event location should get memories and event links."""
    gq = mock_graph_queries
    gq.get_npcs_at_location = AsyncMock(return_value=[
        {"id": "npc-a", "name": "Ava"},
        {"id": "npc-b", "name": "Bob"},
    ])
    events = [{"description": "Fire in the market", "location_id": "loc-market"}]

    with patch("app.simulation.events.add_memory") as mock_add:
        results = await process_events(gq, events, world_day=5)

    # 2 NPCs should get memories
    assert mock_add.call_count == 2
    # 2 NPCs should be linked to the event
    assert gq.link_event_to_npc.await_count == 2


@pytest.mark.asyncio
async def test_process_events_affected_npc_ids(mock_graph_queries):
    """Events with affected_npc_ids should notify those NPCs."""
    gq = mock_graph_queries
    events = [{
        "description": "A curse falls on the blacksmith",
        "affected_npc_ids": ["npc-smith"],
    }]

    with patch("app.simulation.events.add_memory") as mock_add:
        results = await process_events(gq, events, world_day=4)

    mock_add.assert_called_once()
    assert "npc-smith" in mock_add.call_args[0][0]
