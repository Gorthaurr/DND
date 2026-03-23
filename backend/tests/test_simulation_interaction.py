"""Tests for app.simulation.interaction_resolver — resolve_interactions."""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# The interaction_resolver lazily imports from app.simulation.ticker which needs celery.
# Pre-mock celery if it isn't installed.
if "celery" not in sys.modules:
    sys.modules["celery"] = MagicMock()

from app.simulation.interaction_resolver import resolve_interactions


@pytest.fixture
def mock_npc_agent():
    agent = MagicMock()
    agent.interact = AsyncMock(return_value={
        "summary": "They had a pleasant chat.",
        "interaction_type": "conversation",
        "action": "none",
        "a_sentiment_change": 0.1,
        "b_sentiment_change": 0.05,
        "a_mood_change": "same",
        "b_mood_change": "same",
    })
    return agent


@pytest.fixture
def two_npcs_same_location(mock_graph_queries):
    gq = mock_graph_queries
    npc_a = {"id": "npc-a", "name": "Ava", "mood": "neutral", "alive": True, "gold": 10}
    npc_b = {"id": "npc-b", "name": "Bob", "mood": "neutral", "alive": True, "gold": 5}

    gq.get_npc_location = AsyncMock(
        side_effect=lambda nid: {"id": "loc-1", "name": "Tavern"} if nid in ("npc-a", "npc-b") else None,
    )
    gq.get_relationships = AsyncMock(return_value=[])
    return gq, [npc_a, npc_b]


@pytest.mark.asyncio
async def test_resolve_interactions_returns_list(mock_npc_agent, two_npcs_same_location):
    """resolve_interactions should return a list of interaction dicts."""
    gq, npcs = two_npcs_same_location

    with patch("app.simulation.interaction_resolver.add_memory"):
        results = await resolve_interactions(gq, mock_npc_agent, npcs, world_day=3)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["npc_a"] in ("Ava", "Bob")
    assert results[0]["npc_b"] in ("Ava", "Bob")
    assert results[0]["summary"] == "They had a pleasant chat."


@pytest.mark.asyncio
async def test_resolve_interactions_no_npcs(mock_npc_agent, mock_graph_queries):
    """No NPCs means no interactions."""
    with patch("app.simulation.interaction_resolver.add_memory"):
        results = await resolve_interactions(mock_graph_queries, mock_npc_agent, [], world_day=1)

    assert results == []
    mock_npc_agent.interact.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_interactions_single_npc(mock_npc_agent, mock_graph_queries):
    """A single NPC cannot interact with anyone."""
    npc = {"id": "npc-a", "name": "Solo", "mood": "neutral", "alive": True}
    mock_graph_queries.get_npc_location = AsyncMock(return_value={"id": "loc-1", "name": "Square"})

    with patch("app.simulation.interaction_resolver.add_memory"):
        results = await resolve_interactions(mock_graph_queries, mock_npc_agent, [npc], world_day=1)

    assert results == []


@pytest.mark.asyncio
async def test_resolve_interactions_applies_sentiment(mock_npc_agent, two_npcs_same_location):
    """Sentiment changes should be applied via set_relationship."""
    gq, npcs = two_npcs_same_location

    with patch("app.simulation.interaction_resolver.add_memory"):
        await resolve_interactions(gq, mock_npc_agent, npcs, world_day=5)

    # set_relationship called for a->b and b->a sentiment changes
    assert gq.set_relationship.await_count >= 1


@pytest.mark.asyncio
async def test_resolve_interactions_handles_error(mock_npc_agent, two_npcs_same_location):
    """If interact() raises, the pair is skipped without crashing."""
    gq, npcs = two_npcs_same_location
    mock_npc_agent.interact = AsyncMock(side_effect=RuntimeError("LLM down"))

    with patch("app.simulation.interaction_resolver.add_memory"):
        results = await resolve_interactions(gq, mock_npc_agent, npcs, world_day=2)

    # Error is caught, returns empty
    assert results == []
