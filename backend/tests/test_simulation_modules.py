"""Tests for simulation modules: scheduler, reputation, quests, analytics, events, rumors, interaction_resolver, background_ticker, scenario_manager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestScheduler:
    @pytest.mark.asyncio
    async def test_get_active_npcs(self):
        from app.simulation.scheduler import get_active_npcs
        gq = MagicMock()
        gq.get_player_location = AsyncMock(return_value={"id": "loc-1"})
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": "npc-1", "name": "Near", "goals": ["protect"]},
        ])
        all_npcs = [
            {"id": "npc-1", "name": "Near", "goals": ["protect"]},
            {"id": "npc-2", "name": "Far", "goals": []},
            {"id": "npc-3", "name": "Goal", "goals": ["find treasure"]},
        ]
        result = await get_active_npcs(gq, all_npcs, "player-1")
        assert len(result) > 0
        # NPC near player should be prioritized
        ids = [n["id"] for n in result]
        assert "npc-1" in ids


class TestBackgroundTicker:
    @pytest.mark.asyncio
    async def test_tick_runs_without_llm(self):
        from app.simulation.background_ticker import BackgroundTicker
        ticker = BackgroundTicker()
        gq = MagicMock()
        gq.world_id = "test"
        gq.increment_world_day = AsyncMock(return_value=5)
        gq.get_all_npcs = AsyncMock(return_value=[
            {"id": "npc-1", "name": "Guard", "occupation": "guard",
             "personality": "Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10",
             "mood": "neutral", "archetype": "guardian",
             "trust_baseline": 0.0, "mood_baseline": 0.0,
             "aggression_baseline": 0.0, "confidence_baseline": 0.0},
        ])
        gq.get_all_locations = AsyncMock(return_value=[{"id": "loc-1", "name": "Square"}])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_npc = AsyncMock()
        gq.update_location = AsyncMock()
        gq.update_world_state = AsyncMock()
        gq.get_npc_location = AsyncMock(return_value={"id": "loc-1"})

        with patch("app.models.memory.init_memory_db"), \
             patch("app.models.memory.add_memory"), \
             patch("app.models.memory.decay_importance", return_value=0):
            result = await ticker.tick(gq, 5)
            assert result["mode"] == "background"
            assert result["day"] == 5


class TestScenarioManager:
    def test_module_importable(self):
        from app.simulation.scenario_manager import run_scenario_lifecycle
        assert callable(run_scenario_lifecycle)


class TestInteractionResolver:
    @pytest.mark.asyncio
    async def test_resolve_no_npcs(self):
        from app.simulation.interaction_resolver import resolve_interactions
        gq = MagicMock()
        npc_agent = MagicMock()
        result = await resolve_interactions(gq, npc_agent, [], 1, None)
        assert result == []


class TestEvents:
    @pytest.mark.asyncio
    async def test_process_events_empty(self):
        from app.simulation.events import process_events
        gq = MagicMock()
        gq.create_world_event = AsyncMock()
        gq.link_event_to_location = AsyncMock()
        gq.link_event_to_npc = AsyncMock()
        result = await process_events(gq, [], 1)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_process_events_with_event(self):
        from app.simulation.events import process_events
        gq = MagicMock()
        gq.create_world_event = AsyncMock()
        gq.link_event_to_location = AsyncMock()
        gq.link_event_to_npc = AsyncMock()
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": "npc-1", "name": "Guard"},
        ])
        events = [{"description": "Storm", "type": "natural",
                   "location_id": "loc-1", "affected_npc_ids": ["npc-1"]}]
        with patch("app.simulation.events.add_memory"):
            result = await process_events(gq, events, 1)
        gq.create_world_event.assert_called()
