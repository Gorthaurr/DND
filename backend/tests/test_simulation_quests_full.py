"""Tests for app.simulation.quests — detect_conflicts and generate_quest_from_world."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.simulation.quests import detect_conflicts, generate_quest_from_world


@pytest.mark.asyncio
async def test_detect_conflicts_finds_negative_relationships():
    """detect_conflicts should find NPCs with sentiment < -0.3."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
        {"id": "npc-2", "name": "Bob"},
    ])
    gq.get_relationships = AsyncMock(side_effect=[
        # Ava's relationships
        [{"name": "Bob", "id": "npc-2", "sentiment": -0.5, "reason": "stole my bread"}],
        # Bob's relationships
        [],
    ])

    conflicts = await detect_conflicts(gq)

    assert len(conflicts) == 1
    assert "Ava" in conflicts[0]
    assert "Bob" in conflicts[0]


@pytest.mark.asyncio
async def test_detect_conflicts_ignores_positive():
    """Positive relationships should not produce conflicts."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
    ])
    gq.get_relationships = AsyncMock(return_value=[
        {"name": "Bob", "id": "npc-2", "sentiment": 0.8, "reason": "best friends"},
    ])

    conflicts = await detect_conflicts(gq)
    assert conflicts == []


@pytest.mark.asyncio
async def test_detect_conflicts_empty_npcs():
    """No NPCs means no conflicts."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[])

    conflicts = await detect_conflicts(gq)
    assert conflicts == []


@pytest.mark.asyncio
async def test_generate_quest_from_world_returns_quest():
    """generate_quest_from_world should return a quest dict when conflicts exist."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
    ])
    gq.get_relationships = AsyncMock(return_value=[
        {"name": "Bob", "id": "npc-2", "sentiment": -0.6, "reason": "rivalry"},
    ])
    gq.get_recent_events = AsyncMock(return_value=[
        {"description": "A storm hit the village"},
    ])
    gq.get_player_location = AsyncMock(return_value={"name": "Tavern"})

    mock_quest = {"quest_name": "Resolve the Feud", "description": "Help Ava and Bob"}

    with patch("app.simulation.quests.dm_agent") as mock_dm:
        mock_dm.generate_quest = AsyncMock(return_value=mock_quest)
        result = await generate_quest_from_world(gq, "player-1")

    assert result is not None
    assert result["quest_name"] == "Resolve the Feud"


@pytest.mark.asyncio
async def test_generate_quest_no_conflicts_returns_none():
    """No conflicts means no quest generated."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[
        {"id": "npc-1", "name": "Ava"},
    ])
    gq.get_relationships = AsyncMock(return_value=[])

    result = await generate_quest_from_world(gq, "player-1")
    assert result is None


@pytest.mark.asyncio
async def test_generate_quest_dm_returns_none():
    """If dm_agent returns None, generate_quest_from_world should return None."""
    gq = MagicMock()
    gq.get_all_npcs = AsyncMock(return_value=[{"id": "npc-1", "name": "Ava"}])
    gq.get_relationships = AsyncMock(return_value=[
        {"name": "Bob", "id": "npc-2", "sentiment": -0.5, "reason": "distrust"},
    ])
    gq.get_recent_events = AsyncMock(return_value=[])
    gq.get_player_location = AsyncMock(return_value=None)

    with patch("app.simulation.quests.dm_agent") as mock_dm:
        mock_dm.generate_quest = AsyncMock(return_value=None)
        result = await generate_quest_from_world(gq, "player-1")

    assert result is None
