"""Tests for environment engine (seasons, weather, disasters)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.simulation.environment import EnvironmentEngine, SEASONS, WEATHER_WEIGHTS, CONDITION_RECOVERY


class TestEnvironmentEngine:
    def setup_method(self):
        self.engine = EnvironmentEngine()

    def test_season_cycle_spring(self):
        assert self.engine.get_season(0) == "spring"
        assert self.engine.get_season(15) == "spring"
        assert self.engine.get_season(29) == "spring"

    def test_season_cycle_summer(self):
        assert self.engine.get_season(30) == "summer"
        assert self.engine.get_season(59) == "summer"

    def test_season_cycle_autumn(self):
        assert self.engine.get_season(60) == "autumn"

    def test_season_cycle_winter(self):
        assert self.engine.get_season(90) == "winter"

    def test_season_cycle_wraps(self):
        # Day 120 = back to spring
        assert self.engine.get_season(120) == "spring"

    def test_weather_returns_valid_string(self):
        for season in SEASONS:
            weather = self.engine.get_weather(season)
            assert weather in WEATHER_WEIGHTS[season]

    def test_weather_consistency(self):
        """Weather should only return options valid for the season."""
        for _ in range(100):
            weather = self.engine.get_weather("winter")
            assert weather in WEATHER_WEIGHTS["winter"]

    def test_summer_can_have_drought(self):
        """Summer should occasionally produce drought."""
        weathers = set()
        for _ in range(200):
            weathers.add(self.engine.get_weather("summer"))
        assert "drought" in weathers

    def test_winter_can_have_snow(self):
        weathers = set()
        for _ in range(100):
            weathers.add(self.engine.get_weather("winter"))
        assert "snow" in weathers

    def test_all_seasons_have_weather_weights(self):
        for season in SEASONS:
            assert season in WEATHER_WEIGHTS
            weights = WEATHER_WEIGHTS[season]
            assert abs(sum(weights.values()) - 1.0) < 0.01


class TestEnvironmentTick:
    @pytest.mark.asyncio
    async def test_tick_returns_tuple(self):
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[])
        result = await engine.tick(gq, 1)
        events, season, weather = result
        assert isinstance(events, list)
        assert season in SEASONS
        assert isinstance(weather, str)

    @pytest.mark.asyncio
    async def test_season_change_event(self):
        """Day 31 = first day of summer → season change event."""
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[])
        events, season, _ = await engine.tick(gq, 31)  # day 31 % 30 == 1
        season_events = [e for e in events if "season" in e["description"].lower()]
        assert len(season_events) == 1

    @pytest.mark.asyncio
    async def test_no_season_change_mid_season(self):
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[])
        events, _, _ = await engine.tick(gq, 15)
        season_events = [e for e in events if "season has changed" in e["description"].lower()]
        assert len(season_events) == 0

    @pytest.mark.asyncio
    async def test_condition_recovery(self):
        """Flooded location recovers after 3 days."""
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[{
            "id": "loc-1", "name": "Bridge", "type": "bridge",
            "condition": "flooded", "condition_since_day": 10,
            "accessibility": 0.2,
        }])
        gq.update_location = AsyncMock()
        events, _, _ = await engine.tick(gq, 14)  # 14-10=4 > 3 recovery days
        recovery_events = [e for e in events if "recovered" in e["description"].lower()]
        assert len(recovery_events) == 1
        # Check update_location called with normal condition
        update_call = gq.update_location.call_args[0]
        assert update_call[1].get("condition") == "normal"

    @pytest.mark.asyncio
    async def test_normal_location_no_recovery(self):
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[{
            "id": "loc-1", "name": "Square", "type": "square",
            "condition": "normal", "accessibility": 1.0,
        }])
        gq.update_location = AsyncMock()
        await engine.tick(gq, 5)
        # No recovery needed for normal locations

    @pytest.mark.asyncio
    async def test_world_state_updated(self):
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[])
        await engine.tick(gq, 5)
        gq.update_world_state.assert_called_once()
        call_args = gq.update_world_state.call_args[0][0]
        assert "season" in call_args
        assert "weather" in call_args

    @pytest.mark.asyncio
    async def test_storm_weather_event(self):
        """Storm weather should generate a weather event."""
        engine = EnvironmentEngine()
        gq = MagicMock()
        gq.update_world_state = AsyncMock()
        gq.get_all_locations = AsyncMock(return_value=[{
            "id": "loc-1", "name": "Village", "type": "village",
            "condition": "normal", "accessibility": 1.0,
        }])
        gq.update_location = AsyncMock()

        # Mock weather to storm
        original_get_weather = engine.get_weather
        engine.get_weather = lambda s: "storm"
        events, _, weather = await engine.tick(gq, 5)
        engine.get_weather = original_get_weather
        assert weather == "storm"
        storm_events = [e for e in events if "storm" in e["description"].lower()]
        assert len(storm_events) >= 1
