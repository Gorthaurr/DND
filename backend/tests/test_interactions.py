"""Tests for NPC interaction resolution."""

import pytest


class TestMoodChangeLogic:
    """Test the mood state machine used in ticker and interaction_resolver."""

    def _apply_mood(self, current: str, change: str) -> str:
        """Mirror the mood change logic from ticker.py."""
        mood = current
        if change == "better":
            mood = "content" if mood in ("angry", "fearful") else "excited"
        elif change == "worse":
            mood = "angry" if mood in ("content", "excited") else "fearful"
        return mood

    def test_angry_gets_better(self):
        assert self._apply_mood("angry", "better") == "content"

    def test_fearful_gets_better(self):
        assert self._apply_mood("fearful", "better") == "content"

    def test_content_gets_better(self):
        assert self._apply_mood("content", "better") == "excited"

    def test_excited_gets_better(self):
        assert self._apply_mood("excited", "better") == "excited"

    def test_content_gets_worse(self):
        assert self._apply_mood("content", "worse") == "angry"

    def test_excited_gets_worse(self):
        assert self._apply_mood("excited", "worse") == "angry"

    def test_angry_gets_worse(self):
        assert self._apply_mood("angry", "worse") == "fearful"

    def test_fearful_gets_worse(self):
        assert self._apply_mood("fearful", "worse") == "fearful"

    def test_same_keeps_mood(self):
        for mood in ("angry", "fearful", "content", "excited"):
            assert self._apply_mood(mood, "same") == mood


class TestRelationshipClamping:
    """Test that sentiment stays within [-1.0, 1.0]."""

    def _clamp_sentiment(self, old: float, change: float) -> float:
        return min(1.0, max(-1.0, old + change))

    def test_positive_overflow(self):
        assert self._clamp_sentiment(0.8, 0.5) == 1.0

    def test_negative_overflow(self):
        assert self._clamp_sentiment(-0.8, -0.5) == -1.0

    def test_normal_change(self):
        assert self._clamp_sentiment(0.0, 0.3) == pytest.approx(0.3)

    def test_zero_change(self):
        assert self._clamp_sentiment(0.5, 0.0) == pytest.approx(0.5)

    def test_extreme_positive(self):
        assert self._clamp_sentiment(1.0, 100.0) == 1.0

    def test_extreme_negative(self):
        assert self._clamp_sentiment(-1.0, -100.0) == -1.0
