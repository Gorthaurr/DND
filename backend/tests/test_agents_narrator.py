"""Tests for Narrator Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_mock_gq(**overrides):
    """Build a mock GraphQueries with sensible defaults."""
    gq = MagicMock()
    gq.get_all_relationships = AsyncMock(return_value=overrides.get("relationships", []))
    gq.get_all_factions = AsyncMock(return_value=overrides.get("factions", []))
    gq.get_faction_members = AsyncMock(return_value=overrides.get("faction_members", []))
    gq.get_dead_npcs = AsyncMock(return_value=overrides.get("dead_npcs", []))
    gq.get_all_npcs = AsyncMock(return_value=overrides.get("all_npcs", []))
    gq.get_all_locations = AsyncMock(return_value=overrides.get("locations", []))
    gq.get_active_scenarios = AsyncMock(return_value=overrides.get("active_scenarios", []))
    return gq


class TestNarratorAgentAnalyzeTensions:
    """Tests for NarratorAgent.analyze_tensions()."""

    @pytest.mark.asyncio
    async def test_analyze_tensions_basic(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._tensions_agent = AsyncMock()
        agent._tensions_agent.generate_json = AsyncMock(return_value={
            "tensions": [
                {"type": "rivalry", "involved_npc_names": ["A", "B"], "severity": "high"},
            ]
        })

        gq = _make_mock_gq(
            relationships=[
                {"from_id": "a", "to_id": "b", "sentiment": -0.8, "from_name": "A", "to_name": "B"},
            ],
        )

        result = await agent.analyze_tensions(gq, world_day=5)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["type"] == "rivalry"

    @pytest.mark.asyncio
    async def test_analyze_tensions_empty_world(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._tensions_agent = AsyncMock()
        agent._tensions_agent.generate_json = AsyncMock(return_value={"tensions": []})

        gq = _make_mock_gq()
        result = await agent.analyze_tensions(gq, world_day=1)
        assert result == []

    @pytest.mark.asyncio
    async def test_analyze_tensions_with_factions(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._tensions_agent = AsyncMock()
        agent._tensions_agent.generate_json = AsyncMock(return_value={
            "tensions": [
                {"type": "faction_conflict", "severity": "critical"},
            ]
        })

        gq = _make_mock_gq(
            factions=[
                {"id": "f1", "name": "Thieves Guild", "influence": 0.8, "morale": 0.3, "strategy": "aggressive"},
                {"id": "f2", "name": "Town Guard", "influence": 0.6, "morale": 0.7, "strategy": "defensive"},
            ],
            faction_members=[{"id": "npc-1"}, {"id": "npc-2"}],
        )

        result = await agent.analyze_tensions(gq, world_day=10)
        assert len(result) == 1
        assert result[0]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_analyze_tensions_with_economic_issues(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._tensions_agent = AsyncMock()
        agent._tensions_agent.generate_json = AsyncMock(return_value={
            "tensions": [
                {"type": "economic_crisis", "severity": "medium"},
            ]
        })

        gq = _make_mock_gq(
            locations=[
                {"name": "Village", "resources": {"food": 1, "water": 0}},
            ],
        )

        result = await agent.analyze_tensions(gq, world_day=15)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_analyze_tensions_with_unfulfilled_goals(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._tensions_agent = AsyncMock()
        agent._tensions_agent.generate_json = AsyncMock(return_value={
            "tensions": [{"type": "desperation", "severity": "high"}]
        })

        gq = _make_mock_gq(
            all_npcs=[
                {"name": "Farmer", "goals": ["get food"], "mood": "angry"},
            ],
        )

        result = await agent.analyze_tensions(gq, world_day=20)
        assert len(result) == 1


class TestNarratorAgentGenerateArc:
    """Tests for NarratorAgent.generate_arc()."""

    @pytest.mark.asyncio
    async def test_generate_arc_success(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._arc_agent = AsyncMock()
        agent._arc_agent.generate_json = AsyncMock(return_value={
            "title": "Blood Feud",
            "description": "An old grudge erupts into violence",
            "scenario_type": "main",
            "tension_level": "rising",
            "involved_npc_names": ["Guard", "Thief"],
            "phases": [
                {
                    "name": "Confrontation",
                    "description": "The two meet",
                    "trigger_day_offset": 0,
                    "events_to_inject": [],
                    "npc_directives": {"guard": "Confront the thief"},
                },
                {
                    "name": "Escalation",
                    "description": "Things get worse",
                    "trigger_day_offset": 3,
                    "events_to_inject": ["A fight breaks out"],
                    "npc_directives": {},
                },
            ],
        })

        gq = MagicMock()
        gq.get_all_npcs = AsyncMock(return_value=[
            {"id": "npc-guard", "name": "Guard"},
            {"id": "npc-thief", "name": "Thief"},
        ])

        tension = {
            "type": "rivalry",
            "severity": "high",
            "involved_npc_names": ["Guard", "Thief"],
        }

        result = await agent.generate_arc(tension, gq, world_day=5, active_arcs=[])
        assert result is not None
        assert result["title"] == "Blood Feud"
        assert result["id"].startswith("sc-")
        assert len(result["phases"]) == 2
        assert result["phases"][0]["phase_id"].startswith("ph-")
        assert "npc-guard" in result["involved_npc_ids"]
        assert "npc-thief" in result["involved_npc_ids"]

    @pytest.mark.asyncio
    async def test_generate_arc_returns_none_on_empty(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._arc_agent = AsyncMock()
        agent._arc_agent.generate_json = AsyncMock(return_value=None)

        gq = MagicMock()
        gq.get_all_npcs = AsyncMock(return_value=[])

        result = await agent.generate_arc(
            {"type": "x", "involved_npc_names": []}, gq, world_day=1, active_arcs=[],
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_arc_returns_none_on_missing_title(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        agent._arc_agent = AsyncMock()
        agent._arc_agent.generate_json = AsyncMock(return_value={"description": "no title here"})

        gq = MagicMock()
        gq.get_all_npcs = AsyncMock(return_value=[])

        result = await agent.generate_arc(
            {"type": "x", "involved_npc_names": []}, gq, world_day=1, active_arcs=[],
        )
        assert result is None


class TestNarratorAgentShouldGenerateArc:
    """Tests for NarratorAgent.should_generate_arc()."""

    def test_returns_none_when_too_many_active_arcs(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [{"severity": "critical"}]
        active_arcs = [{}, {}, {}]  # 3 active arcs
        result = agent.should_generate_arc(tensions, active_arcs)
        assert result is None

    def test_returns_critical_tension(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [
            {"severity": "low", "type": "minor"},
            {"severity": "critical", "type": "war"},
        ]
        result = agent.should_generate_arc(tensions, active_arcs=[])
        assert result is not None
        assert result["severity"] == "critical"

    def test_returns_high_tension(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [{"severity": "high", "type": "rivalry"}]
        result = agent.should_generate_arc(tensions, active_arcs=[])
        assert result is not None
        assert result["severity"] == "high"

    def test_returns_medium_when_few_arcs(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [{"severity": "medium", "type": "dispute"}]
        result = agent.should_generate_arc(tensions, active_arcs=[{}])
        assert result is not None
        assert result["severity"] == "medium"

    def test_returns_none_for_medium_when_two_arcs(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [{"severity": "medium", "type": "dispute"}]
        result = agent.should_generate_arc(tensions, active_arcs=[{}, {}])
        assert result is None

    def test_returns_none_for_only_low_tensions(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        tensions = [{"severity": "low"}, {"severity": "low"}]
        result = agent.should_generate_arc(tensions, active_arcs=[])
        assert result is None

    def test_returns_none_for_empty_tensions(self):
        from app.agents.narrator_agent import NarratorAgent

        agent = NarratorAgent()
        result = agent.should_generate_arc([], active_arcs=[])
        assert result is None
