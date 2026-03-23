"""Tests for Report Agent."""

import pytest
from unittest.mock import AsyncMock, patch


def _make_report_data(**overrides):
    """Helper to build report data with sensible defaults."""
    defaults = {
        "world_day": 10,
        "period": {"from_day": 1, "to_day": 10},
        "events": [
            {"day": 3, "description": "A storm passed"},
            {"day": 7, "description": "Market day"},
        ],
        "deaths": [],
        "relationships": {"alliances": [], "rivalries": []},
        "scenarios": {"active": [], "completed": []},
    }
    defaults.update(overrides)
    return defaults


class TestReportAgentAnalyze:
    """Tests for ReportAgent.analyze()."""

    @pytest.mark.asyncio
    async def test_analyze_returns_string(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()

        with patch.object(agent, "generate_text", new_callable=AsyncMock, return_value="World is peaceful."):
            result = await agent.analyze(_make_report_data())
            assert isinstance(result, str)
            assert result == "World is peaceful."

    @pytest.mark.asyncio
    async def test_analyze_returns_default_on_empty_response(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()

        with patch.object(agent, "generate_text", new_callable=AsyncMock, return_value=""):
            result = await agent.analyze(_make_report_data())
            assert result == "No significant events to report."

    @pytest.mark.asyncio
    async def test_analyze_returns_none_fallback(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()

        with patch.object(agent, "generate_text", new_callable=AsyncMock, return_value=None):
            result = await agent.analyze(_make_report_data())
            assert result == "No significant events to report."

    @pytest.mark.asyncio
    async def test_analyze_falls_back_on_exception(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()

        with patch.object(agent, "generate_text", new_callable=AsyncMock, side_effect=RuntimeError("LLM down")):
            result = await agent.analyze(_make_report_data())
            assert isinstance(result, str)
            # Should contain fallback report content
            assert "World Report" in result


class TestReportAgentFallback:
    """Tests for ReportAgent._fallback_report()."""

    def test_fallback_report_basic(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data()
        result = agent._fallback_report(data)
        assert isinstance(result, str)
        assert "World Report" in result
        assert "Days 1 to 10" in result

    def test_fallback_report_with_events(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data(events=[
            {"day": 1, "description": "A fire broke out"},
            {"day": 2, "description": "Rain extinguished the fire"},
        ])
        result = agent._fallback_report(data)
        assert "Events (2)" in result
        assert "A fire broke out" in result

    def test_fallback_report_with_deaths(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data(deaths=[
            {"name": "Old Tom", "occupation": "farmer"},
        ])
        result = agent._fallback_report(data)
        assert "Deaths (1)" in result
        assert "Old Tom" in result

    def test_fallback_report_with_alliances_and_rivalries(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data(relationships={
            "alliances": [{"from": "Guard", "to": "Merchant", "sentiment": 0.8}],
            "rivalries": [{"from": "Thief", "to": "Guard", "sentiment": -0.9}],
        })
        result = agent._fallback_report(data)
        assert "Alliances (1)" in result
        assert "Guard" in result
        assert "Rivalries (1)" in result

    def test_fallback_report_with_scenarios(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data(scenarios={
            "active": [{"title": "The Siege"}],
            "completed": [{"title": "Lost Artifact"}],
        })
        result = agent._fallback_report(data)
        assert "Active Scenarios" in result
        assert "The Siege" in result
        assert "Completed" in result
        assert "Lost Artifact" in result

    def test_fallback_report_empty_data(self):
        from app.agents.report_agent import ReportAgent

        agent = ReportAgent()
        data = _make_report_data(events=[], deaths=[], relationships={}, scenarios={})
        result = agent._fallback_report(data)
        assert "World Report" in result
        # Should not crash, just minimal output
        assert isinstance(result, str)
