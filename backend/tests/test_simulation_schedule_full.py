"""Tests for app.simulation.schedule — ScheduleEngine (pure logic)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.simulation.schedule import ScheduleEngine, _parse_big_five


class TestParseBigFive:
    def test_parse_standard_format(self):
        s = "O: 7/10, C: 3/10, E: 2/10, A: 8/10, N: 5/10"
        scores = _parse_big_five(s)
        assert scores == {"O": 7, "C": 3, "E": 2, "A": 8, "N": 5}

    def test_parse_long_names(self):
        s = "Openness 8/10, Conscientiousness 6/10, Extraversion 4/10, Agreeableness 9/10, Neuroticism 2/10"
        scores = _parse_big_five(s)
        assert scores["O"] == 8
        assert scores["C"] == 6
        assert scores["E"] == 4
        assert scores["A"] == 9
        assert scores["N"] == 2

    def test_parse_empty_string(self):
        assert _parse_big_five("") == {}

    def test_parse_partial(self):
        scores = _parse_big_five("O: 5/10, N: 9/10")
        assert scores == {"O": 5, "N": 9}


class TestScheduleEngine:
    def setup_method(self):
        self.engine = ScheduleEngine()

    def _make_npc(self, **overrides):
        base = {
            "id": "npc-test",
            "name": "Test",
            "occupation": "blacksmith",
            "personality": "O: 5/10, C: 5/10, E: 5/10, A: 5/10, N: 5/10",
            "mood": "neutral",
            "archetype": None,
            "trust_baseline": 0.0,
            "mood_baseline": 0.0,
            "aggression_baseline": 0.0,
            "confidence_baseline": 0.0,
        }
        base.update(overrides)
        return base

    def test_get_activity_returns_dict(self):
        npc = self._make_npc()
        result = self.engine.get_activity(npc, "morning", 1)
        assert "action" in result
        assert "activity_desc" in result
        assert "location_hint" in result

    def test_morning_high_conscientiousness_works(self):
        """High C in morning should always return 'work'."""
        npc = self._make_npc(personality="O: 1/10, C: 9/10, E: 5/10, A: 5/10, N: 1/10")
        # Run multiple times since some paths have randomness
        with patch("app.simulation.schedule.random") as mock_rng:
            mock_rng.random.return_value = 0.99  # avoid random overrides
            mock_rng.choice.return_value = "work"
            result = self.engine.get_activity(npc, "morning", 1)
        assert result["action"] == "work"

    def test_introvert_evening_avoids_socialize(self):
        """Low E NPC should have socialize replaced with rest in evening."""
        npc = self._make_npc(
            personality="O: 1/10, C: 5/10, E: 1/10, A: 5/10, N: 1/10",
            archetype="merchant",
        )
        with (
            patch("app.simulation.schedule.get_archetype") as mock_arch,
            patch("app.simulation.schedule.random") as mock_rng,
        ):
            # Archetype returns socialize for evening
            arch = mock_arch.return_value
            arch.default_schedule = {"evening": {"activity": "socialize"}}
            mock_rng.random.return_value = 0.99  # avoid all random overrides
            mock_rng.choice.return_value = "rest"

            result = self.engine.get_activity(npc, "evening", 1)

        assert result["action"] == "rest"

    def test_work_action_includes_occupation(self):
        """'work' action should have activity_desc mentioning occupation."""
        npc = self._make_npc(occupation="healer")
        with patch("app.simulation.schedule.random") as mock_rng:
            mock_rng.random.return_value = 0.99
            mock_rng.choice.return_value = "work"
            result = self.engine.get_activity(npc, "afternoon", 1)

        if result["action"] == "work":
            assert "healer" in result["activity_desc"]

    def test_distrustful_npc_avoids_evening_socialize(self):
        """NPC with low trust_baseline should avoid socialize in evening."""
        npc = self._make_npc(
            trust_baseline=-0.5,
            archetype="merchant",
        )
        with (
            patch("app.simulation.schedule.get_archetype") as mock_arch,
            patch("app.simulation.schedule.random") as mock_rng,
        ):
            arch = mock_arch.return_value
            arch.default_schedule = {"evening": {"activity": "socialize"}}
            mock_rng.random.return_value = 0.99
            mock_rng.choice.return_value = "rest"

            result = self.engine.get_activity(npc, "evening", 5)

        assert result["action"] == "rest"

    def test_dawn_maps_to_morning_slot(self):
        """Phase 'dawn' should map to 'morning' slot."""
        npc = self._make_npc(personality="O: 1/10, C: 9/10, E: 5/10, A: 5/10, N: 1/10")
        with patch("app.simulation.schedule.random") as mock_rng:
            mock_rng.random.return_value = 0.99
            mock_rng.choice.return_value = "work"
            result = self.engine.get_activity(npc, "dawn", 1)
        # High C in morning slot => work
        assert result["action"] == "work"

    def test_no_archetype_defaults_to_work(self):
        """NPC without archetype should default to 'work' base action."""
        npc = self._make_npc(archetype=None)
        with patch("app.simulation.schedule.random") as mock_rng:
            mock_rng.random.return_value = 0.99
            mock_rng.choice.return_value = "work"
            result = self.engine.get_activity(npc, "afternoon", 1)
        assert result["action"] == "work"

    def test_aggressive_npc_may_patrol(self):
        """NPC with high aggression baseline may switch to patrol."""
        npc = self._make_npc(aggression_baseline=0.5)
        with patch("app.simulation.schedule.random") as mock_rng:
            # 0.1 < 0.25 => aggressive override triggers
            # But also <0.10 => random variety. Use 0.15 to avoid variety.
            mock_rng.random.return_value = 0.15
            mock_rng.choice.return_value = "patrol"
            result = self.engine.get_activity(npc, "morning", 1)
        assert result["action"] == "patrol"
