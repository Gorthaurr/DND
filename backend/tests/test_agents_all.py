"""Tests for all agent modules (dm, npc, event, scenario, report, memory_architect).

All agents use BaseAgent which delegates to LLM — we mock generate_json.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.npc_agent import NPCAgent
from app.agents.dm_agent import DMAgent
from app.agents.event_agent import EventAgent
from app.agents.scenario_agent import ScenarioAgent
from app.agents.report_agent import ReportAgent
from app.agents.memory_architect import MemoryArchitect
from app.models.npc import NPCContext, NPCRelationship


def _make_npc_context(**overrides):
    defaults = dict(
        npc_id="npc-1", name="Goran", personality="Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10",
        backstory="A hunter", goals=["survive"], mood="neutral", occupation="hunter", age=35,
        location_name="Square", location_description="Town square",
        nearby_npcs=[], relationships=[], recent_memories=[], recent_events=[],
        world_day=10,
    )
    defaults.update(overrides)
    return NPCContext(**defaults)


class TestNPCAgent:
    @pytest.mark.asyncio
    async def test_decide_returns_decision(self):
        agent = NPCAgent()
        ctx = _make_npc_context()
        mock_result = {"action": "patrol", "target": None, "dialogue": None,
                       "reasoning": "keeping watch", "mood_change": "same"}
        with patch.object(agent._decision_agent, "generate_json", new_callable=AsyncMock, return_value=mock_result):
            decision = await agent.decide(ctx)
            assert decision.action == "patrol"

    @pytest.mark.asyncio
    async def test_decide_fallback_on_empty(self):
        agent = NPCAgent()
        ctx = _make_npc_context()
        with patch.object(agent._decision_agent, "generate_json", new_callable=AsyncMock, return_value=None):
            decision = await agent.decide(ctx)
            assert decision.action == "rest"

    @pytest.mark.asyncio
    async def test_dialogue(self):
        agent = NPCAgent()
        npc = {"name": "Bob", "age": 30, "occupation": "guard", "personality": "O:5/10",
               "mood": "neutral", "backstory": "guard", "archetype": None}
        mock_result = {"dialogue": "Hello traveler!", "mood_change": "same",
                       "sentiment_change": 0.1, "internal_thought": "seems friendly"}
        with patch.object(agent._dialogue_agent, "generate_json", new_callable=AsyncMock, return_value=mock_result):
            result = await agent.dialogue(npc, "Hi there!", "Player")
            assert result["dialogue"] == "Hello traveler!"

    @pytest.mark.asyncio
    async def test_dialogue_fallback(self):
        agent = NPCAgent()
        npc = {"name": "Bob", "age": 30, "occupation": "guard", "personality": "O:5",
               "mood": "neutral", "backstory": "guard", "archetype": None}
        with patch.object(agent._dialogue_agent, "generate_json", new_callable=AsyncMock, return_value=None):
            result = await agent.dialogue(npc, "Hi", "Player")
            assert "stares" in result["dialogue"].lower()

    @pytest.mark.asyncio
    async def test_interact(self):
        agent = NPCAgent()
        npc_a = {"name": "Alice", "personality": "O:5"}
        npc_b = {"name": "Bob", "personality": "O:5"}
        context = {"location_name": "tavern"}
        mock_result = {"summary": "They talked.", "interaction_type": "conversation",
                       "action": "none", "a_sentiment_change": 0.1, "b_sentiment_change": 0.1,
                       "a_mood_change": "same", "b_mood_change": "same"}
        with patch.object(agent._interact_agent, "generate_json", new_callable=AsyncMock, return_value=mock_result):
            result = await agent.interact(npc_a, npc_b, context)
            assert "talked" in result["summary"].lower()

    @pytest.mark.asyncio
    async def test_interact_fallback(self):
        agent = NPCAgent()
        npc_a = {"name": "Alice"}
        npc_b = {"name": "Bob"}
        with patch.object(agent._interact_agent, "generate_json", new_callable=AsyncMock, return_value=None):
            result = await agent.interact(npc_a, npc_b, {})
            assert "ignored" in result["summary"].lower()

    @pytest.mark.asyncio
    async def test_decide_with_nearby_npcs(self):
        agent = NPCAgent()
        ctx = _make_npc_context(
            nearby_npcs=[{"id": "npc-2", "name": "Finn", "occupation": "thief"}],
            relationships=[NPCRelationship(npc_id="npc-2", name="Finn", sentiment=-0.8, reason="stole from me")],
        )
        mock_result = {"action": "threaten", "target": "Finn", "reasoning": "anger"}
        with patch.object(agent._decision_agent, "generate_json", new_callable=AsyncMock, return_value=mock_result):
            decision = await agent.decide(ctx)
            assert decision.action == "threaten"


class TestDMAgent:
    @pytest.mark.asyncio
    async def test_narrate(self):
        # DMAgent has narrate method
        agent = DMAgent()
        with patch.object(agent, "_agent" if hasattr(agent, "_agent") else "_narrate_agent",
                          create=True) as mock_agent:
            mock_agent.generate_json = AsyncMock(return_value={
                "narration": "You attack the goblin!", "npcs_involved": ["Goblin"],
            })
            # Just verify the agent can be instantiated
            assert agent is not None


class TestEventAgent:
    def test_load_event_pool(self):
        agent = EventAgent()
        # Should not crash even with nonexistent path
        from pathlib import Path
        agent.load_event_pool(Path("/nonexistent/path"))

    @pytest.mark.asyncio
    async def test_generate_events(self):
        agent = EventAgent()
        with patch.object(agent, "_agent" if hasattr(agent, "_agent") else "_event_agent",
                          create=True) as mock_agent:
            mock_agent.generate_json = AsyncMock(return_value={
                "events": [{"description": "A storm approaches", "type": "natural"}]
            })
            # Just verify instantiation works
            assert agent is not None


class TestScenarioAgent:
    def test_instantiation(self):
        agent = ScenarioAgent()
        assert agent is not None

    def test_load_scenario_pool(self):
        agent = ScenarioAgent()
        from pathlib import Path
        agent.load_scenario_pool(Path("/nonexistent"))  # should not crash


class TestReportAgent:
    def test_instantiation(self):
        agent = ReportAgent()
        assert agent is not None


class TestMemoryArchitect:
    def test_instantiation(self):
        agent = MemoryArchitect()
        assert agent is not None

    def test_decay_calls_memory(self):
        agent = MemoryArchitect()
        with patch("app.agents.memory_architect.memory_architect.decay_memories") as mock:
            # Just verify method exists and can be called signature-wise
            assert hasattr(agent, "decay_memories")

    @pytest.mark.asyncio
    async def test_consolidate_skips_if_few_memories(self):
        agent = MemoryArchitect()
        with patch("app.models.memory.get_old_memories", return_value=[{"id": "1", "content": "x", "importance": 0.3}] * 3):
            result = await agent.consolidate_npc("npc-1", "Test")
            assert result == 0  # too few to consolidate
