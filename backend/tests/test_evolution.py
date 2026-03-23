"""Tests for NPC long-term personality evolution."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.simulation.evolution import EvolutionEngine, _clamp


class TestEvolutionShifts:
    def setup_method(self):
        self.engine = EvolutionEngine()

    def test_was_robbed_shifts(self):
        shifts = self.engine.compute_shifts("was_robbed")
        assert shifts["trust"] < 0  # trust drops
        assert shifts["mood"] < 0   # mood drops
        assert shifts["aggression"] > 0  # gets angrier

    def test_killed_enemy_shifts(self):
        shifts = self.engine.compute_shifts("killed_enemy")
        assert shifts["confidence"] > 0

    def test_was_helped_positive(self):
        shifts = self.engine.compute_shifts("was_helped")
        assert shifts["trust"] > 0
        assert shifts["mood"] > 0

    def test_unknown_event_empty(self):
        assert self.engine.compute_shifts("unknown_event") == {}


class TestClassifyActionOutcome:
    def setup_method(self):
        self.engine = EvolutionEngine()

    def test_fight_with_kill(self):
        events = self.engine.classify_action_outcome(
            "fight", "Goblin", {"attacker_won": True, "defender_died": True})
        assert "killed_enemy" in events

    def test_fight_survived(self):
        events = self.engine.classify_action_outcome(
            "fight", "Goblin", {"attacker_won": False, "defender_died": False})
        assert "survived_fight" in events

    def test_trade_classified(self):
        events = self.engine.classify_action_outcome("trade", "Merchant")
        assert "made_trade" in events

    def test_rob_classified(self):
        events = self.engine.classify_action_outcome("rob", "Victim")
        assert "robbed_someone" in events

    def test_help_classified(self):
        events = self.engine.classify_action_outcome("help", "Friend")
        assert "helped_someone" in events

    def test_work_classified(self):
        events = self.engine.classify_action_outcome("work", None)
        assert "earned_gold" in events

    def test_rest_classified(self):
        events = self.engine.classify_action_outcome("rest", None)
        assert "rested" in events

    def test_pray_classified(self):
        events = self.engine.classify_action_outcome("pray", None)
        assert "prayed" in events

    def test_threaten_classified(self):
        events = self.engine.classify_action_outcome("threaten", "Someone")
        assert "threatened_someone" in events

    def test_gossip_classified(self):
        events = self.engine.classify_action_outcome("gossip", "Village")
        assert "had_conversation" in events

    def test_craft_classified(self):
        events = self.engine.classify_action_outcome("craft", None)
        assert "earned_gold" in events

    def test_fight_attacker_won_survived(self):
        """Attacker won but defender didn't die → survived_fight."""
        events = self.engine.classify_action_outcome(
            "fight", "Target", {"attacker_won": True, "defender_died": False})
        assert "survived_fight" in events

    def test_fight_attacker_died(self):
        """Attacker died → no events (dead NPC doesn't evolve)."""
        events = self.engine.classify_action_outcome(
            "fight", "Target", {"attacker_died": True})
        assert events == []

    def test_fight_no_combat_result(self):
        """Fight without combat_result → survived_fight."""
        events = self.engine.classify_action_outcome("fight", "Target", None)
        assert "survived_fight" in events

    def test_unknown_action_no_events(self):
        events = self.engine.classify_action_outcome("investigate", None)
        assert events == []


class TestClamp:
    def test_clamp_within_range(self):
        assert _clamp(0.5) == 0.5

    def test_clamp_lower_bound(self):
        assert _clamp(-1.5) == -1.0

    def test_clamp_upper_bound(self):
        assert _clamp(1.5) == 1.0


class TestApplyShifts:
    @pytest.mark.asyncio
    async def test_apply_shifts_updates_graph(self):
        engine = EvolutionEngine()
        gq = MagicMock()
        gq.update_npc = AsyncMock()
        npc = {"id": "npc-1", "name": "Test", "trust_baseline": 0.0,
               "mood_baseline": 0.0, "aggression_baseline": 0.0, "confidence_baseline": 0.0}
        await engine.apply_shifts(gq, "npc-1", npc, ["was_robbed"])
        gq.update_npc.assert_called_once()
        call_args = gq.update_npc.call_args
        updates = call_args[0][1]
        assert "trust_baseline" in updates
        assert updates["trust_baseline"] < 0

    @pytest.mark.asyncio
    async def test_no_shifts_no_update(self):
        engine = EvolutionEngine()
        gq = MagicMock()
        gq.update_npc = AsyncMock()
        npc = {"id": "npc-1", "name": "Test"}
        await engine.apply_shifts(gq, "npc-1", npc, [])
        gq.update_npc.assert_not_called()

    @pytest.mark.asyncio
    async def test_unknown_event_no_deltas_no_update(self):
        """Event type with no shifts → no graph update (line 135)."""
        engine = EvolutionEngine()
        gq = MagicMock()
        gq.update_npc = AsyncMock()
        npc = {"id": "npc-1", "name": "Test"}
        # "unknown" returns {} shifts → deltas empty → return {}
        result = await engine.apply_shifts(gq, "npc-1", npc, ["unknown_event_type"])
        assert result == {}
        gq.update_npc.assert_not_called()
