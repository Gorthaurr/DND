"""Tests for Big Five → speech instruction mapping."""

from app.agents.speech_patterns import _parse_big_five, build_speech_instructions


class TestParseBigFive:
    def test_standard_format(self):
        scores = _parse_big_five("Big Five: O:7/10, C:3/10, E:2/10, A:8/10, N:9/10")
        assert scores == {"O": 7, "C": 3, "E": 2, "A": 8, "N": 9}

    def test_named_format(self):
        scores = _parse_big_five("Openness 6/10, Conscientiousness 8/10, Extraversion 4/10, Agreeableness 3/10, Neuroticism 2/10")
        assert scores == {"O": 6, "C": 8, "E": 4, "A": 3, "N": 2}

    def test_empty_string(self):
        assert _parse_big_five("") == {}

    def test_partial_data(self):
        scores = _parse_big_five("O:7/10, C:3/10")
        assert scores == {"O": 7, "C": 3}


class TestBuildSpeechInstructions:
    def test_high_openness_rules(self):
        result = build_speech_instructions("Big Five: O:8/10, C:5/10, E:5/10, A:5/10, N:5/10")
        assert "metaphor" in result.lower() or "analog" in result.lower()

    def test_low_extraversion_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:2/10, A:5/10, N:5/10")
        assert "short" in result.lower() or "brief" in result.lower()

    def test_low_agreeableness_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:2/10, N:5/10")
        assert "blunt" in result.lower() or "apolog" in result.lower()

    def test_high_neuroticism_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:9/10")
        assert "worr" in result.lower() or "catastroph" in result.lower()

    def test_mood_modifiers_angry(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10", "angry")
        assert "angry" in result.lower() or "sharp" in result.lower() or "clench" in result.lower()

    def test_mood_modifiers_fearful(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10", "fearful")
        assert "stutter" in result.lower() or "nervous" in result.lower()

    def test_max_6_rules(self):
        # All extreme traits → lots of rules, but capped at 6
        result = build_speech_instructions("Big Five: O:9/10, C:1/10, E:1/10, A:1/10, N:9/10", "angry")
        lines = [l for l in result.strip().split("\n") if l.strip()]
        assert len(lines) <= 6

    def test_empty_personality_returns_empty(self):
        result = build_speech_instructions("")
        assert result == ""

    def test_neutral_personality_no_rules(self):
        # All 5/10 → no high/low triggers
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10")
        assert result == ""

    def test_partial_traits_skips_missing(self):
        """Only O present — other traits skipped via continue branch."""
        result = build_speech_instructions("Big Five: O:8/10")
        assert "metaphor" in result.lower() or "analog" in result.lower()
        # Should NOT contain rules for C, E, A, N since they're missing
        lines = result.strip().split("\n")
        assert len(lines) <= 3  # only openness rules

    def test_high_conscientiousness_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:9/10, E:5/10, A:5/10, N:5/10")
        assert "structured" in result.lower() or "precise" in result.lower()

    def test_low_conscientiousness_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:2/10, E:5/10, A:5/10, N:5/10")
        assert "ramble" in result.lower() or "filler" in result.lower()

    def test_high_agreeableness_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:8/10, N:5/10")
        assert "soften" in result.lower() or "polite" in result.lower()

    def test_low_neuroticism_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:2/10")
        assert "calm" in result.lower() or "measured" in result.lower()

    def test_high_extraversion_rules(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:9/10, A:5/10, N:5/10")
        assert "loud" in result.lower() or "question" in result.lower() or "emphatic" in result.lower()

    def test_content_mood(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10", "content")
        assert "warm" in result.lower() or "relaxed" in result.lower()

    def test_excited_mood(self):
        result = build_speech_instructions("Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10", "excited")
        assert "quickly" in result.lower() or "superlative" in result.lower()
