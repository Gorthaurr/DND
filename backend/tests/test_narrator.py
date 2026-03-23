"""Tests for Narrator Agent (tension analysis and arc generation)."""

from app.agents.narrator_agent import NarratorAgent


class TestShouldGenerateArc:
    def setup_method(self):
        self.agent = NarratorAgent()

    def test_high_severity_generates(self):
        tensions = [{"severity": "high", "type": "rivalry"}]
        result = self.agent.should_generate_arc(tensions, [])
        assert result is not None
        assert result["severity"] == "high"

    def test_critical_severity_generates(self):
        tensions = [{"severity": "critical", "type": "faction_conflict"}]
        result = self.agent.should_generate_arc(tensions, [])
        assert result is not None

    def test_too_many_active_arcs(self):
        tensions = [{"severity": "critical"}]
        arcs = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        result = self.agent.should_generate_arc(tensions, arcs)
        assert result is None

    def test_low_severity_no_generate(self):
        tensions = [{"severity": "low"}]
        result = self.agent.should_generate_arc(tensions, [])
        assert result is None

    def test_medium_with_few_arcs(self):
        tensions = [{"severity": "medium"}]
        result = self.agent.should_generate_arc(tensions, [{"id": "1"}])
        assert result is not None

    def test_medium_with_two_arcs_no_generate(self):
        tensions = [{"severity": "medium"}]
        result = self.agent.should_generate_arc(tensions, [{"id": "1"}, {"id": "2"}])
        assert result is None

    def test_empty_tensions(self):
        result = self.agent.should_generate_arc([], [])
        assert result is None

    def test_prefers_highest_severity(self):
        tensions = [
            {"severity": "low", "type": "personal"},
            {"severity": "high", "type": "faction_conflict"},
            {"severity": "medium", "type": "economic"},
        ]
        result = self.agent.should_generate_arc(tensions, [])
        assert result["severity"] == "high"
