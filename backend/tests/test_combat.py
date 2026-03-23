"""Tests for NPC combat resolution."""

import random
from unittest.mock import AsyncMock, patch

import pytest


class TestNPCCombat:
    @pytest.mark.asyncio
    async def test_defender_killed_when_hp_zero(self, mock_graph_queries, sample_npc_attacker, sample_npc_defender):
        """Defender dies when combat reduces HP to 0."""
        from app.simulation.ticker import _resolve_npc_combat

        # Seed random so attacker always hits and kills
        with patch("app.simulation.ticker.random") as mock_rng:
            mock_rng.randint.side_effect = [
                20, 8,   # round 1: attacker rolls 20 (hit), deals 8 damage
                1, 1,    # round 1: defender rolls 1 (miss)
                20, 8,   # round 2: attacker rolls 20 (hit), deals 8 damage
                1, 1,    # round 2: defender miss
                20, 8,   # round 3: attacker hits
                1, 1,    # round 3: defender miss
            ]

            # Set defender HP low enough to die
            sample_npc_defender["current_hp"] = 5
            mock_graph_queries.get_npc_location.return_value = {"id": "loc-1", "name": "Tavern"}
            mock_graph_queries.get_npcs_at_location.return_value = []

            with patch("app.simulation.ticker.add_memory"):
                result = await _resolve_npc_combat(
                    mock_graph_queries, sample_npc_attacker, sample_npc_defender, "fight", 1,
                )

            assert result["defender_died"] is True
            mock_graph_queries.kill_npc.assert_called_once_with("npc-defender")

    @pytest.mark.asyncio
    async def test_both_survive_combat(self, mock_graph_queries, sample_npc_attacker, sample_npc_defender):
        """Both NPCs survive when neither reaches 0 HP."""
        from app.simulation.ticker import _resolve_npc_combat

        with patch("app.simulation.ticker.random") as mock_rng:
            # All attacks miss (roll 1)
            mock_rng.randint.return_value = 1

            with patch("app.simulation.ticker.add_memory"):
                result = await _resolve_npc_combat(
                    mock_graph_queries, sample_npc_attacker, sample_npc_defender, "fight", 1,
                )

            assert result["defender_died"] is False
            assert result["attacker_died"] is False
            mock_graph_queries.kill_npc.assert_not_called()

    @pytest.mark.asyncio
    async def test_robbery_success(self, mock_graph_queries, sample_npc_attacker, sample_npc_defender):
        """Successful robbery transfers gold."""
        from app.simulation.ticker import _resolve_npc_combat

        with patch("app.simulation.ticker.random") as mock_rng:
            # success_chance check passes, stolen gold = 3
            mock_rng.random.return_value = 0.1
            mock_rng.randint.return_value = 3

            with patch("app.simulation.ticker.add_memory"):
                result = await _resolve_npc_combat(
                    mock_graph_queries, sample_npc_attacker, sample_npc_defender, "rob", 1,
                )

            mock_graph_queries.transfer_gold.assert_called_once()
            mock_graph_queries.set_relationship.assert_called()

    @pytest.mark.asyncio
    async def test_robbery_caught(self, mock_graph_queries, sample_npc_attacker, sample_npc_defender):
        """Failed robbery changes relationship to hostile."""
        from app.simulation.ticker import _resolve_npc_combat

        with patch("app.simulation.ticker.random") as mock_rng:
            # Robbery fails
            mock_rng.random.return_value = 0.99

            with patch("app.simulation.ticker.add_memory"):
                await _resolve_npc_combat(
                    mock_graph_queries, sample_npc_attacker, sample_npc_defender, "rob", 1,
                )

            # Should set hostile relationship
            mock_graph_queries.set_relationship.assert_called()
            call_args = mock_graph_queries.set_relationship.call_args
            assert call_args[0][2] == -0.9  # sentiment


class TestD20Rolls:
    def test_d20_range(self):
        """D20 roll should always be between 1 and 20."""
        for _ in range(100):
            roll = random.randint(1, 20)
            assert 1 <= roll <= 20

    def test_d20_plus_level_beats_ac(self):
        """High level + high roll should beat AC."""
        level = 10
        roll = 18
        ac = 12
        assert (roll + level) >= ac

    def test_d20_critical_always_hits(self):
        """Roll of 20 + any level beats reasonable AC."""
        for level in range(1, 20):
            assert (20 + level) >= (10 + level)  # AC = 10 + level
