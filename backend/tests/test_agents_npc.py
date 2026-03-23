"""Tests for NPC Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.npc import NPCContext, NPCDecision, NPCRelationship


def _make_npc_context(**overrides) -> NPCContext:
    """Helper to build an NPCContext with sensible defaults."""
    defaults = dict(
        npc_id="npc-guard-1",
        name="Guard",
        personality="Stoic and dutiful",
        backstory="Grew up in the barracks",
        goals=["patrol village"],
        mood="neutral",
        occupation="guard",
        age=30,
        location_name="Gate",
        location_description="The village gate stands tall.",
        nearby_npcs=[],
        relationships=[],
        recent_memories=[],
        recent_events=[],
        world_day=1,
    )
    defaults.update(overrides)
    return NPCContext(**defaults)


class TestNPCAgentDecide:
    """Tests for NPCAgent.decide()."""

    @pytest.mark.asyncio
    async def test_decide_returns_npc_decision(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._decision_agent = AsyncMock()
        agent._decision_agent.generate_json = AsyncMock(return_value={
            "action": "patrol",
            "target": None,
            "dialogue": None,
            "mood_change": "same",
            "reasoning": "Duty calls",
        })

        ctx = _make_npc_context()
        result = await agent.decide(ctx)
        assert isinstance(result, NPCDecision)
        assert result.action == "patrol"
        assert result.reasoning == "Duty calls"

    @pytest.mark.asyncio
    async def test_decide_returns_rest_on_empty_result(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._decision_agent = AsyncMock()
        agent._decision_agent.generate_json = AsyncMock(return_value=None)

        ctx = _make_npc_context()
        result = await agent.decide(ctx)
        assert isinstance(result, NPCDecision)
        assert result.action == "rest"
        assert result.reasoning == "couldn't decide"

    @pytest.mark.asyncio
    async def test_decide_with_nearby_npcs_and_relationships(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._decision_agent = AsyncMock()
        agent._decision_agent.generate_json = AsyncMock(return_value={
            "action": "talk",
            "target": "Merchant",
            "dialogue": "Good morning!",
            "mood_change": "better",
            "reasoning": "Friendly neighbor",
        })

        ctx = _make_npc_context(
            nearby_npcs=[{"id": "npc-merchant", "name": "Merchant", "occupation": "merchant"}],
            relationships=[
                NPCRelationship(npc_id="npc-merchant", name="Merchant", sentiment=0.7, reason="old friend"),
            ],
        )
        result = await agent.decide(ctx)
        assert result.action == "talk"
        assert result.target == "Merchant"

    @pytest.mark.asyncio
    async def test_decide_fills_defaults_for_missing_keys(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._decision_agent = AsyncMock()
        agent._decision_agent.generate_json = AsyncMock(return_value={})

        ctx = _make_npc_context()
        result = await agent.decide(ctx)
        assert result.action == "rest"
        assert result.mood_change == "same"


class TestNPCAgentDialogue:
    """Tests for NPCAgent.dialogue()."""

    @pytest.mark.asyncio
    async def test_dialogue_returns_dict(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._dialogue_agent = AsyncMock()
        agent._dialogue_agent.generate_json = AsyncMock(return_value={
            "dialogue": "Hello traveler",
            "mood_change": "same",
            "sentiment_change": 0.1,
            "internal_thought": "Seems friendly",
        })

        npc = {
            "name": "Guard",
            "age": 30,
            "occupation": "guard",
            "personality": "Stoic",
            "mood": "neutral",
            "backstory": "A veteran",
            "biography": None,
        }

        with patch("app.agents.npc_agent.build_speech_instructions", return_value="Speak formally."):
            result = await agent.dialogue(
                npc=npc,
                message="Hello there!",
                other_name="Player",
                is_player=True,
                reputation=10,
            )
        assert isinstance(result, dict)
        assert result["dialogue"] == "Hello traveler"
        assert result["sentiment_change"] == 0.1

    @pytest.mark.asyncio
    async def test_dialogue_fallback_on_empty(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._dialogue_agent = AsyncMock()
        agent._dialogue_agent.generate_json = AsyncMock(return_value=None)

        npc = {
            "name": "Guard",
            "age": 30,
            "occupation": "guard",
            "personality": "Stoic",
            "mood": "neutral",
            "backstory": "A veteran",
        }

        with patch("app.agents.npc_agent.build_speech_instructions", return_value=""):
            result = await agent.dialogue(
                npc=npc,
                message="Hi",
                other_name="Player",
            )
        assert "stares at you blankly" in result["dialogue"]
        assert result["mood_change"] == "same"


class TestNPCAgentInteract:
    """Tests for NPCAgent.interact() (NPC-to-NPC)."""

    @pytest.mark.asyncio
    async def test_interact_returns_dict(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._interact_agent = AsyncMock()
        agent._interact_agent.generate_json = AsyncMock(return_value={
            "summary": "Guard and Merchant shared news.",
            "interaction_type": "conversation",
            "dialogue_a": "Any news?",
            "dialogue_b": "Trade is good.",
            "action": "none",
            "action_initiator": "none",
            "action_details": {},
            "a_sentiment_change": 0.1,
            "b_sentiment_change": 0.05,
            "a_mood_change": "same",
            "b_mood_change": "better",
        })

        npc_a = {"name": "Guard", "occupation": "guard"}
        npc_b = {"name": "Merchant", "occupation": "merchant"}
        context = {"location_name": "Market", "a_to_b_relationship": None, "b_to_a_relationship": None}

        result = await agent.interact(npc_a, npc_b, context)
        assert isinstance(result, dict)
        assert "summary" in result
        assert result["interaction_type"] == "conversation"
        assert result["a_sentiment_change"] == 0.1

    @pytest.mark.asyncio
    async def test_interact_fallback_on_empty(self):
        from app.agents.npc_agent import NPCAgent

        agent = NPCAgent()
        agent._interact_agent = AsyncMock()
        agent._interact_agent.generate_json = AsyncMock(return_value=None)

        npc_a = {"name": "Guard"}
        npc_b = {"name": "Thief"}
        context = {"location_name": "Alley"}

        result = await agent.interact(npc_a, npc_b, context)
        assert "ignored each other" in result["summary"]
        assert result["action"] == "none"
