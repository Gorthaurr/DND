"""Tests for economy engine."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.simulation.economy import EconomyEngine, BASE_PRICES, SHORTAGE_THRESHOLD, SURPLUS_THRESHOLD


class TestEconomyEngine:
    def setup_method(self):
        self.engine = EconomyEngine()

    def test_get_shortages_with_low_resources(self):
        loc = {"resources": '{"food": 1, "iron": 10, "wood": 2}'}
        shortages = self.engine.get_shortages(loc)
        assert "food" in shortages
        assert "wood" in shortages
        assert "iron" not in shortages

    def test_get_shortages_no_shortage(self):
        loc = {"resources": '{"food": 20, "iron": 15}'}
        assert self.engine.get_shortages(loc) == []

    def test_get_shortages_empty_resources(self):
        loc = {"resources": "{}"}
        assert self.engine.get_shortages(loc) == []

    def test_get_shortages_no_resources_key(self):
        loc = {}
        assert self.engine.get_shortages(loc) == []

    def test_get_shortages_invalid_json(self):
        loc = {"resources": "not-json"}
        assert self.engine.get_shortages(loc) == []

    def test_prosperity_zero_npcs(self):
        assert self.engine._calc_prosperity({"food": 10}, 0) == 0.3

    def test_prosperity_high_food(self):
        p = self.engine._calc_prosperity({"food": 100}, 5)
        assert p > 0.5

    def test_prosperity_no_food(self):
        p = self.engine._calc_prosperity({"food": 0}, 10)
        assert p <= 0.3

    def test_prosperity_capped(self):
        p = self.engine._calc_prosperity({"food": 1000}, 1)
        assert p <= 0.9

    def test_base_prices_exist(self):
        assert "food" in BASE_PRICES
        assert "iron" in BASE_PRICES
        assert all(isinstance(v, int) for v in BASE_PRICES.values())


class TestEconomyTick:
    @pytest.mark.asyncio
    async def test_tick_with_shortage(self):
        """Full tick producing shortage event."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Village", "resources": '{"food": 1, "iron": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": "npc-1", "occupation": "guard"},
        ])
        gq.update_location = AsyncMock()

        events = await engine.tick(gq, 10, [])
        # Food=1 is below SHORTAGE_THRESHOLD → should generate shortage event
        shortage_events = [e for e in events if "shortage" in e["description"].lower()]
        assert len(shortage_events) >= 1
        gq.update_location.assert_called_once()

    @pytest.mark.asyncio
    async def test_tick_with_surplus(self):
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Farm", "resources": f'{{"food": {SURPLUS_THRESHOLD + 5}}}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_location = AsyncMock()

        events = await engine.tick(gq, 10, [])
        surplus_events = [e for e in events if "surplus" in e["description"].lower()]
        assert len(surplus_events) >= 1

    @pytest.mark.asyncio
    async def test_tick_production(self):
        """Farmer produces food."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Farm", "resources": '{"food": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": "npc-1", "occupation": "farmer"},
        ])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 10, [])
        # Check update_location was called with increased food
        call_args = gq.update_location.call_args[0]
        import json
        resources = json.loads(call_args[1]["resources"])
        assert resources["food"] > 10  # farmer produced food

    @pytest.mark.asyncio
    async def test_tick_empty_resources_initialized(self):
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "New Place"},  # no resources key
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 1, [])
        # Should initialize defaults
        import json
        call_args = gq.update_location.call_args[0]
        resources = json.loads(call_args[1]["resources"])
        assert "food" in resources

    @pytest.mark.asyncio
    async def test_tick_invalid_json_resources(self):
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Broken", "resources": "not-json"},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_location = AsyncMock()
        # Should not crash
        await engine.tick(gq, 1, [])
        gq.update_location.assert_called_once()

    @pytest.mark.asyncio
    async def test_tick_consumption(self):
        """NPCs consume food."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Town", "resources": '{"food": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": f"npc-{i}", "occupation": "guard"} for i in range(10)
        ])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 1, [])
        import json
        resources = json.loads(gq.update_location.call_args[0][1]["resources"])
        assert resources["food"] < 10  # consumed

    @pytest.mark.asyncio
    async def test_tick_zero_demand_price(self):
        """Zero NPCs → demand=0 → price_multiplier=1.0."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Empty", "resources": '{"food": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 1, [])
        import json
        prices = json.loads(gq.update_location.call_args[0][1]["prices"])
        assert prices["food"] == BASE_PRICES["food"]  # multiplier=1.0

    @pytest.mark.asyncio
    async def test_tick_new_resource_from_production(self):
        """NPC produces resource not in location → creates it."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Mine", "resources": '{"food": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"id": "npc-1", "occupation": "miner"},  # produces iron, stone
        ])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 1, [])
        import json
        resources = json.loads(gq.update_location.call_args[0][1]["resources"])
        assert "iron" in resources  # miner created new iron resource

    @pytest.mark.asyncio
    async def test_tick_no_events_no_log(self):
        """No events → no log call (line 135-136)."""
        engine = EconomyEngine()
        gq = MagicMock()
        gq.get_all_locations = AsyncMock(return_value=[
            {"id": "loc-1", "name": "Normal", "resources": '{"food": 15, "iron": 10, "wood": 10}'},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])
        gq.update_location = AsyncMock()
        events = await engine.tick(gq, 1, [])
        # Most runs won't have events (5% random chance only)
        # This covers the `if events:` branch being False
