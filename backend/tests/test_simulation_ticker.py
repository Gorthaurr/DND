"""Tests for app.simulation.ticker — run_world_tick.

run_world_tick uses lazy imports (from X import Y inside the function body),
so we must patch at the source modules rather than on the ticker module.
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure celery is mockable if not installed
if "celery" not in sys.modules:
    sys.modules["celery"] = MagicMock()


@pytest.fixture(autouse=True)
def _reload_ticker():
    """Force re-import of ticker to pick up fresh patches."""
    mod = "app.simulation.ticker"
    if mod in sys.modules:
        del sys.modules[mod]
    yield
    if mod in sys.modules:
        del sys.modules[mod]


@pytest.mark.asyncio
async def test_run_world_tick_returns_day(mock_graph_queries):
    """run_world_tick should return a dict containing 'day'."""
    gq = mock_graph_queries
    gq.increment_world_day = AsyncMock(return_value=5)
    gq.get_all_npcs = AsyncMock(return_value=[])
    gq.get_all_locations = AsyncMock(return_value=[])
    gq.get_recent_events = AsyncMock(return_value=[])
    gq.get_all_factions = AsyncMock(return_value=[])
    gq.world_id = "default"

    mock_driver = MagicMock()

    with (
        # Patch source modules that ticker lazily imports from
        patch("app.graph.connection.get_driver", return_value=mock_driver),
        patch("app.graph.queries.GraphQueries", return_value=gq),
        patch("app.models.memory.init_memory_db"),
        patch("app.models.memory.get_memory_count", return_value=0),
        patch("app.models.memory.get_recent_memories", return_value=[]),
        patch("app.models.memory.add_memory"),
        patch("app.models.memory.purge_old_summarized"),
        patch("app.simulation.events.process_events", new_callable=AsyncMock, return_value=[]),
        patch("app.simulation.rumors.propagate_rumors", new_callable=AsyncMock),
        patch("app.simulation.scheduler.get_active_npcs", new_callable=AsyncMock, return_value=[]),
        patch("app.simulation.environment.environment_engine") as mock_env,
        patch("app.simulation.economy.economy_engine") as mock_econ,
        patch("app.simulation.scenario_manager.run_scenario_lifecycle", new_callable=AsyncMock, return_value=(
            {}, [], [],
        )),
        patch("app.agents.faction_agent.faction_agent") as mock_faction,
        patch("app.agents.event_agent.event_agent") as mock_event_agent,
        patch("app.agents.npc_agent.npc_agent") as mock_npc,
        patch("app.simulation.schedule.schedule_engine") as mock_sched,
        patch("app.agents.memory_architect.memory_architect") as mock_mem_arch,
        patch("app.simulation.events.summarize_old_memories", new_callable=AsyncMock),
    ):
        mock_env.tick = AsyncMock(return_value=([], "spring", "clear"))
        mock_econ.tick = AsyncMock(return_value=[])
        mock_econ.get_shortages = MagicMock(return_value=[])
        mock_event_agent.load_event_pool = MagicMock()
        mock_event_agent.generate = AsyncMock(return_value=[])
        mock_mem_arch.consolidate_npc = AsyncMock()
        mock_mem_arch.decay_memories = MagicMock()
        mock_mem_arch.build_location_memory = AsyncMock()

        from app.simulation.ticker import run_world_tick

        result = await run_world_tick()

    assert isinstance(result, dict)
    assert result["day"] == 5
    assert "events" in result
    assert "npc_actions" in result


@pytest.mark.asyncio
async def test_run_world_tick_includes_season_and_weather(mock_graph_queries):
    """Tick result should include season and weather from environment engine."""
    gq = mock_graph_queries
    gq.increment_world_day = AsyncMock(return_value=2)
    gq.get_all_npcs = AsyncMock(return_value=[])
    gq.get_all_locations = AsyncMock(return_value=[])
    gq.get_recent_events = AsyncMock(return_value=[])
    gq.get_all_factions = AsyncMock(return_value=[])
    gq.world_id = "default"

    with (
        patch("app.graph.connection.get_driver", return_value=MagicMock()),
        patch("app.graph.queries.GraphQueries", return_value=gq),
        patch("app.models.memory.init_memory_db"),
        patch("app.models.memory.get_memory_count", return_value=0),
        patch("app.models.memory.get_recent_memories", return_value=[]),
        patch("app.models.memory.add_memory"),
        patch("app.models.memory.purge_old_summarized"),
        patch("app.simulation.events.process_events", new_callable=AsyncMock, return_value=[]),
        patch("app.simulation.rumors.propagate_rumors", new_callable=AsyncMock),
        patch("app.simulation.scheduler.get_active_npcs", new_callable=AsyncMock, return_value=[]),
        patch("app.simulation.environment.environment_engine") as mock_env,
        patch("app.simulation.economy.economy_engine") as mock_econ,
        patch("app.simulation.scenario_manager.run_scenario_lifecycle", new_callable=AsyncMock, return_value=({}, [], [])),
        patch("app.agents.faction_agent.faction_agent"),
        patch("app.agents.event_agent.event_agent") as mock_event_agent,
        patch("app.agents.npc_agent.npc_agent"),
        patch("app.simulation.schedule.schedule_engine"),
        patch("app.agents.memory_architect.memory_architect") as mock_mem_arch,
        patch("app.simulation.events.summarize_old_memories", new_callable=AsyncMock),
    ):
        mock_env.tick = AsyncMock(return_value=([], "winter", "snow"))
        mock_econ.tick = AsyncMock(return_value=[])
        mock_econ.get_shortages = MagicMock(return_value=[])
        mock_event_agent.load_event_pool = MagicMock()
        mock_event_agent.generate = AsyncMock(return_value=[])
        mock_mem_arch.consolidate_npc = AsyncMock()
        mock_mem_arch.decay_memories = MagicMock()
        mock_mem_arch.build_location_memory = AsyncMock()

        from app.simulation.ticker import run_world_tick

        result = await run_world_tick()

    assert result["season"] == "winter"
    assert result["weather"] == "snow"
