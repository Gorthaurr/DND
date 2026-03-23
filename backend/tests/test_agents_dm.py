"""Tests for DM Agent."""

import pytest
from unittest.mock import AsyncMock, patch


class TestDMAgent:
    """Tests for DMAgent narration and quest generation."""

    @pytest.mark.asyncio
    async def test_narrate_returns_dict_with_all_keys(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._narrate_agent = AsyncMock()
        agent._narrate_agent.generate_json = AsyncMock(return_value={
            "narration": "You enter the tavern.",
            "npcs_involved": ["bartender"],
            "items_changed": [],
            "location_changed": None,
            "reputation_changes": {},
        })

        result = await agent.narrate(
            player_action="enter tavern",
            location_name="Village Square",
            location_description="A bustling square.",
            present_npcs=[{"name": "Bartender", "mood": "neutral"}],
            recent_events=["A storm passed"],
            inventory=["sword"],
            reputation=10,
            world_day=5,
            player_level=3,
            player_class="fighter",
            player_hp=20,
            player_max_hp=25,
        )
        assert isinstance(result, dict)
        assert result["narration"] == "You enter the tavern."
        assert result["npcs_involved"] == ["bartender"]
        assert result["items_changed"] == []
        assert result["location_changed"] is None
        assert result["reputation_changes"] == {}

    @pytest.mark.asyncio
    async def test_narrate_returns_fallback_on_empty_result(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._narrate_agent = AsyncMock()
        agent._narrate_agent.generate_json = AsyncMock(return_value=None)

        result = await agent.narrate(
            player_action="look around",
            location_name="Forest",
            location_description="Dark woods.",
            present_npcs=[],
            recent_events=[],
            inventory=[],
            reputation=0,
            world_day=1,
        )
        assert result["narration"] == "Nothing seems to happen..."
        assert result["npcs_involved"] == []

    @pytest.mark.asyncio
    async def test_narrate_fills_defaults_for_missing_keys(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._narrate_agent = AsyncMock()
        # Return a truthy dict missing most expected keys
        agent._narrate_agent.generate_json = AsyncMock(return_value={
            "extra_field": "something",  # makes dict truthy
        })

        result = await agent.narrate(
            player_action="wait",
            location_name="Road",
            location_description="A dusty road.",
            present_npcs=[],
            recent_events=[],
            inventory=[],
            reputation=0,
            world_day=2,
        )
        # Missing keys filled by .get() defaults
        assert result["narration"] == "The world is quiet."
        assert result["npcs_involved"] == []
        assert result["items_changed"] == []
        assert result["location_changed"] is None
        assert result["reputation_changes"] == {}

    @pytest.mark.asyncio
    async def test_generate_quest_returns_dict(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_agent = AsyncMock()
        agent._quest_agent.generate_json = AsyncMock(return_value={
            "quest_name": "Missing Merchant",
            "description": "Find the lost merchant",
            "quest_giver_npc_id": "npc-guard",
            "objectives": [{"description": "Search the forest", "completed": False}],
            "reward": "50 gold",
            "difficulty": "medium",
        })

        result = await agent.generate_quest(
            conflicts=["A vs B"],
            recent_events=["Storm"],
            reputation=20,
            location_name="Village",
            world_day=10,
        )
        assert isinstance(result, dict)
        assert result["quest_name"] == "Missing Merchant"
        assert result["difficulty"] == "medium"

    @pytest.mark.asyncio
    async def test_generate_quest_returns_empty_on_none(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_agent = AsyncMock()
        agent._quest_agent.generate_json = AsyncMock(return_value=None)

        result = await agent.generate_quest(
            conflicts=[],
            recent_events=[],
            reputation=0,
            location_name="Desert",
            world_day=1,
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_generate_quest_fills_defaults(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_agent = AsyncMock()
        agent._quest_agent.generate_json = AsyncMock(return_value={
            "extra": "truthy",  # makes dict truthy so defaults apply
        })

        result = await agent.generate_quest(
            conflicts=["dispute"],
            recent_events=[],
            reputation=5,
            location_name="Town",
            world_day=3,
        )
        assert result["quest_name"] == "Unknown Quest"
        assert result["difficulty"] == "medium"
        assert result["reward"] == "gratitude"

    @pytest.mark.asyncio
    async def test_generate_scenario_quest_success(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_gen_agent = AsyncMock()
        agent._quest_gen_agent.generate_json = AsyncMock(return_value={
            "title": "Defend the Gate",
            "description": "Hold the gate against invaders",
            "objectives": [{"task": "Defend", "completed": False}],
        })

        result = await agent.generate_scenario_quest(
            scenario_title="Siege",
            scenario_description="Enemy at the gates",
            phase_name="Phase 1",
            npcs=[{"name": "Guard"}],
            recent_events=["Alarm raised"],
        )
        assert result is not None
        assert result["title"] == "Defend the Gate"

    @pytest.mark.asyncio
    async def test_generate_scenario_quest_returns_none_on_missing_title(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_gen_agent = AsyncMock()
        agent._quest_gen_agent.generate_json = AsyncMock(return_value={"description": "no title"})

        result = await agent.generate_scenario_quest(
            scenario_title="X",
            scenario_description="Y",
            phase_name="P",
            npcs=[],
            recent_events=[],
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_scenario_quest_returns_none_on_empty(self):
        from app.agents.dm_agent import DMAgent

        agent = DMAgent()
        agent._quest_gen_agent = AsyncMock()
        agent._quest_gen_agent.generate_json = AsyncMock(return_value=None)

        result = await agent.generate_scenario_quest(
            scenario_title="X",
            scenario_description="Y",
            phase_name="P",
            npcs=[],
            recent_events=[],
        )
        assert result is None
