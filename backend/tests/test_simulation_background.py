"""Tests for app.simulation.background_ticker — BackgroundTicker."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.simulation.background_ticker import BackgroundTicker


@pytest.fixture
def bg_ticker():
    return BackgroundTicker()


@pytest.fixture
def gq_mock():
    gq = MagicMock()
    gq.world_id = "test-world"
    gq.increment_world_day = AsyncMock(return_value=10)
    gq.get_all_npcs = AsyncMock(return_value=[])
    gq.get_npc_location = AsyncMock(return_value=None)
    gq.update_npc = AsyncMock()
    return gq


@pytest.mark.asyncio
async def test_tick_returns_summary_dict(bg_ticker, gq_mock):
    """tick() should return a dict with day, season, weather, mode keys."""
    with (
        patch("app.models.memory.init_memory_db"),
        patch("app.models.memory.add_memory"),
        patch("app.simulation.environment.environment_engine") as mock_env,
        patch("app.simulation.economy.economy_engine") as mock_econ,
        patch("app.simulation.schedule.schedule_engine") as mock_sched,
        patch("app.simulation.evolution.evolution_engine") as mock_evo,
        patch("app.agents.memory_architect.memory_architect") as mock_mem,
    ):
        mock_env.tick = AsyncMock(return_value=([], "summer", "rainy"))
        mock_econ.tick = AsyncMock(return_value=[])
        mock_sched.get_activity = MagicMock(return_value={
            "action": "work",
            "activity_desc": "working as blacksmith",
            "location_hint": None,
        })
        mock_evo.classify_action_outcome = MagicMock(return_value=[])
        mock_evo.apply_shifts = AsyncMock()
        mock_mem.decay_memories = MagicMock()

        result = await bg_ticker.tick(gq_mock)

    assert isinstance(result, dict)
    assert result["day"] == 10
    assert result["season"] == "summer"
    assert result["weather"] == "rainy"
    assert result["mode"] == "background"


@pytest.mark.asyncio
async def test_tick_with_explicit_world_day(bg_ticker, gq_mock):
    """tick() should use the provided world_day instead of incrementing."""
    with (
        patch("app.models.memory.init_memory_db"),
        patch("app.models.memory.add_memory"),
        patch("app.simulation.environment.environment_engine") as mock_env,
        patch("app.simulation.economy.economy_engine") as mock_econ,
        patch("app.simulation.schedule.schedule_engine") as mock_sched,
        patch("app.simulation.evolution.evolution_engine") as mock_evo,
        patch("app.agents.memory_architect.memory_architect") as mock_mem,
    ):
        mock_env.tick = AsyncMock(return_value=([], "autumn", "foggy"))
        mock_econ.tick = AsyncMock(return_value=[])
        mock_sched.get_activity = MagicMock(return_value={
            "action": "rest", "activity_desc": "resting", "location_hint": None,
        })
        mock_evo.classify_action_outcome = MagicMock(return_value=[])
        mock_evo.apply_shifts = AsyncMock()
        mock_mem.decay_memories = MagicMock()

        result = await bg_ticker.tick(gq_mock, world_day=42)

    assert result["day"] == 42
    # Should NOT have called increment_world_day
    gq_mock.increment_world_day.assert_not_awaited()


@pytest.mark.asyncio
async def test_tick_processes_npcs(bg_ticker, gq_mock):
    """tick() should run schedule for active NPCs and record actions."""
    npc1 = {"id": "npc-1", "name": "Ava", "occupation": "farmer", "mood": "neutral", "personality": ""}
    npc2 = {"id": "npc-2", "name": "Bob", "occupation": "guard", "mood": "neutral", "personality": ""}
    gq_mock.get_all_npcs = AsyncMock(return_value=[npc1, npc2])

    with (
        patch("app.models.memory.init_memory_db"),
        patch("app.models.memory.add_memory") as mock_add_mem,
        patch("app.simulation.environment.environment_engine") as mock_env,
        patch("app.simulation.economy.economy_engine") as mock_econ,
        patch("app.simulation.schedule.schedule_engine") as mock_sched,
        patch("app.simulation.evolution.evolution_engine") as mock_evo,
        patch("app.agents.memory_architect.memory_architect") as mock_mem,
    ):
        mock_env.tick = AsyncMock(return_value=([], "spring", "clear"))
        mock_econ.tick = AsyncMock(return_value=[])
        mock_sched.get_activity = MagicMock(return_value={
            "action": "work", "activity_desc": "working", "location_hint": None,
        })
        mock_evo.classify_action_outcome = MagicMock(return_value=[])
        mock_evo.apply_shifts = AsyncMock()
        mock_mem.decay_memories = MagicMock()

        # Use afternoon phase so all NPCs are active (world_day=7 → 7%5=2 → afternoon)
        result = await bg_ticker.tick(gq_mock, world_day=7)

    assert result["npc_actions"] == 2
    assert gq_mock.update_npc.await_count == 2


@pytest.mark.asyncio
async def test_simple_interactions(bg_ticker, gq_mock):
    """_simple_interactions should pair NPCs at the same location."""
    npc_a = {"id": "a", "name": "Ava"}
    npc_b = {"id": "b", "name": "Bob"}
    gq_mock.get_npc_location = AsyncMock(
        side_effect=lambda nid: {"id": "loc-1", "name": "Tavern"} if nid in ("a", "b") else None,
    )

    with patch("app.models.memory.add_memory"):
        interactions = await bg_ticker._simple_interactions(gq_mock, [npc_a, npc_b], 5)

    assert len(interactions) >= 1
    assert interactions[0]["type"] == "proximity"
