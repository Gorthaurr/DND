"""Tests for reputation system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.simulation.reputation import reputation_label


class TestReputationLabel:
    def test_hero(self):
        assert "hero" in reputation_label(80).lower()

    def test_nemesis_or_hated(self):
        label = reputation_label(-80).lower()
        assert "nemesis" in label or "hated" in label

    def test_neutral(self):
        assert "neutral" in reputation_label(0).lower()

    def test_friendly(self):
        label = reputation_label(30)
        assert isinstance(label, str)
        assert len(label) > 0

    def test_negative(self):
        label = reputation_label(-30)
        assert isinstance(label, str)

    def test_boundary_values(self):
        # All values should return a non-empty string
        for val in range(-100, 101, 10):
            label = reputation_label(val)
            assert isinstance(label, str)
            assert len(label) > 0


class TestReputationAsync:
    @pytest.mark.asyncio
    async def test_update_reputation(self):
        from app.simulation.reputation import update_reputation
        gq = MagicMock()
        gq.get_player_reputation = AsyncMock(return_value=0)
        gq.set_player_reputation = AsyncMock()
        result = await update_reputation(gq, "player-1", "npc-1", 10, "helped")
        assert result == 10
        gq.set_player_reputation.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_reputation_clamp(self):
        from app.simulation.reputation import update_reputation
        gq = MagicMock()
        gq.get_player_reputation = AsyncMock(return_value=95)
        gq.set_player_reputation = AsyncMock()
        result = await update_reputation(gq, "player-1", "npc-1", 20, "saved")
        assert result == 100  # clamped

    @pytest.mark.asyncio
    async def test_get_reputation_summary(self):
        from app.simulation.reputation import get_reputation_summary
        gq = MagicMock()
        gq.get_all_npcs = AsyncMock(return_value=[
            {"id": "npc-1", "name": "Guard"},
        ])
        gq.get_player_reputation = AsyncMock(return_value=50)
        result = await get_reputation_summary(gq, "player-1")
        assert isinstance(result, dict)
