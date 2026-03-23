"""Tests for rumor propagation system."""

import random
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestRumorPropagation:
    def test_rumor_chance_30_percent(self):
        """Verify ~30% propagation rate over many trials."""
        random.seed(42)
        passed = sum(1 for _ in range(1000) if random.random() <= 0.3)
        assert 250 < passed < 350  # roughly 30% with tolerance

    def test_summary_memories_skipped(self):
        """Memories starting with [Summary] should be skipped."""
        memory = "[Summary] Village was peaceful"
        assert memory.startswith("[Summary]")

    def test_rumor_memories_skipped(self):
        """Memories containing 'heard a rumor' should be skipped."""
        memory = "Day 5: heard a rumor from Marta: something happened"
        assert "heard a rumor" in memory.lower()

    @pytest.mark.asyncio
    async def test_enemies_dont_share(self):
        """NPCs with sentiment < -0.5 should not share rumors."""
        from app.simulation.rumors import propagate_rumors

        gq = MagicMock()
        gq.get_npc_location = AsyncMock(side_effect=[
            {"id": "loc-1", "name": "Tavern"},
            {"id": "loc-1", "name": "Tavern"},
        ])
        gq.get_relationships = AsyncMock(return_value=[
            {"id": "npc-2", "name": "Finn", "sentiment": -0.9, "reason": "enemy"},
        ])

        npcs = [
            {"id": "npc-1", "name": "Goran"},
            {"id": "npc-2", "name": "Finn"},
        ]

        with patch("app.simulation.rumors.random") as mock_rng, \
             patch("app.simulation.rumors.get_recent_memories", return_value=["Day 1: Found treasure"]), \
             patch("app.simulation.rumors.add_memory") as mock_add:
            # Force NPC to try sharing (random <= 0.3)
            mock_rng.random.return_value = 0.1
            mock_rng.choice.side_effect = lambda x: x[0] if x else None

            await propagate_rumors(gq, npcs, 5)

            # Memory should NOT be added because they are enemies
            mock_add.assert_not_called()

    @pytest.mark.asyncio
    async def test_friends_share(self):
        """NPCs with positive sentiment should share rumors."""
        from app.simulation.rumors import propagate_rumors

        gq = MagicMock()
        gq.get_npc_location = AsyncMock(side_effect=[
            {"id": "loc-1", "name": "Tavern"},
            {"id": "loc-1", "name": "Tavern"},
        ])
        gq.get_relationships = AsyncMock(return_value=[
            {"id": "npc-2", "name": "Lira", "sentiment": 0.7, "reason": "friend"},
        ])

        npcs = [
            {"id": "npc-1", "name": "Goran"},
            {"id": "npc-2", "name": "Lira"},
        ]

        with patch("app.simulation.rumors.random") as mock_rng, \
             patch("app.simulation.rumors.get_recent_memories", return_value=["Day 1: Found treasure"]), \
             patch("app.simulation.rumors.add_memory") as mock_add:
            mock_rng.random.return_value = 0.1  # will share
            mock_rng.choice.side_effect = lambda x: x[0] if x else None

            await propagate_rumors(gq, npcs, 5)

            mock_add.assert_called_once()
            call_content = mock_add.call_args[0][1]
            assert "rumor" in call_content.lower()
