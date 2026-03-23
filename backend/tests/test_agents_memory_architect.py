"""Tests for Memory Architect Agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call


class TestMemoryArchitectConsolidate:
    """Tests for MemoryArchitect.consolidate_npc()."""

    @pytest.mark.asyncio
    async def test_consolidate_npc_success(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        agent._consolidate_agent = AsyncMock()
        agent._consolidate_agent.generate_json = AsyncMock(return_value={
            "summary": "Had encounters with dragon and bought supplies",
        })

        # 12 memories total: 10 low-importance + 2 high-importance
        old_memories = [
            {"id": f"m{i}", "content": f"memory {i}", "day": i, "importance": 0.3}
            for i in range(10)
        ] + [
            {"id": "m10", "content": "saw a dragon", "day": 10, "importance": 0.9},
            {"id": "m11", "content": "nearly died", "day": 11, "importance": 0.85},
        ]

        with patch("app.models.memory.get_old_memories", return_value=old_memories), \
             patch("app.models.memory.mark_summarized") as mock_mark, \
             patch("app.models.memory.add_memory") as mock_add:

            result = await agent.consolidate_npc("npc-1", "Guard")
            assert result == 10  # 10 low-importance memories consolidated
            mock_mark.assert_called_once()
            mock_add.assert_called_once()
            # Verify the summary content starts with [Consolidated]
            add_call_args = mock_add.call_args
            assert add_call_args[0][1].startswith("[Consolidated]")

    @pytest.mark.asyncio
    async def test_consolidate_npc_too_few_memories(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()

        # Only 5 memories — below the threshold of 10
        old_memories = [
            {"id": f"m{i}", "content": f"memory {i}", "day": i, "importance": 0.3}
            for i in range(5)
        ]

        with patch("app.models.memory.get_old_memories", return_value=old_memories):
            result = await agent.consolidate_npc("npc-1", "Guard")
            assert result == 0

    @pytest.mark.asyncio
    async def test_consolidate_npc_too_few_low_importance(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()

        # 12 memories but most are high-importance (trauma)
        old_memories = [
            {"id": f"m{i}", "content": f"trauma {i}", "day": i, "importance": 0.9}
            for i in range(10)
        ] + [
            {"id": "m10", "content": "bought bread", "day": 10, "importance": 0.3},
            {"id": "m11", "content": "took a walk", "day": 11, "importance": 0.2},
        ]

        with patch("app.models.memory.get_old_memories", return_value=old_memories):
            result = await agent.consolidate_npc("npc-1", "Guard")
            # Only 2 low-importance, threshold is 5
            assert result == 0

    @pytest.mark.asyncio
    async def test_consolidate_npc_llm_returns_no_summary(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        agent._consolidate_agent = AsyncMock()
        agent._consolidate_agent.generate_json = AsyncMock(return_value={})

        old_memories = [
            {"id": f"m{i}", "content": f"memory {i}", "day": i, "importance": 0.3}
            for i in range(12)
        ]

        with patch("app.models.memory.get_old_memories", return_value=old_memories), \
             patch("app.models.memory.mark_summarized") as mock_mark, \
             patch("app.models.memory.add_memory") as mock_add:

            result = await agent.consolidate_npc("npc-1", "Guard")
            assert result == 0
            mock_mark.assert_not_called()
            mock_add.assert_not_called()


class TestMemoryArchitectDecay:
    """Tests for MemoryArchitect.decay_memories()."""

    def test_decay_memories_delegates_to_model(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()

        with patch("app.models.memory.decay_importance", return_value=5) as mock_decay:
            result = agent.decay_memories("npc-1", current_day=10)
            assert result == 5
            mock_decay.assert_called_once_with("npc-1", 10)

    def test_decay_memories_zero_affected(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()

        with patch("app.models.memory.decay_importance", return_value=0):
            result = agent.decay_memories("npc-1", current_day=1)
            assert result == 0


class TestMemoryArchitectLocationMemory:
    """Tests for MemoryArchitect.build_location_memory()."""

    @pytest.mark.asyncio
    async def test_build_location_memory_with_data(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        gq = MagicMock()
        gq.get_events_at_location = AsyncMock(return_value=[
            {"description": "A brawl broke out"},
            {"description": "Market opened"},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"name": "Guard", "current_activity": "patrolling"},
            {"name": "Merchant", "current_activity": "selling"},
        ])

        with patch("app.models.memory.set_location_memory") as mock_set:
            result = await agent.build_location_memory(gq, "loc-market", "Market", world_day=10)
            assert result is not None
            assert "Recent events" in result
            assert "People here" in result
            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_build_location_memory_empty(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        gq = MagicMock()
        gq.get_events_at_location = AsyncMock(return_value=[])
        gq.get_npcs_at_location = AsyncMock(return_value=[])

        result = await agent.build_location_memory(gq, "loc-empty", "Empty Field", world_day=5)
        assert result is None

    @pytest.mark.asyncio
    async def test_build_location_memory_only_events(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        gq = MagicMock()
        gq.get_events_at_location = AsyncMock(return_value=[
            {"description": "Earthquake"},
        ])
        gq.get_npcs_at_location = AsyncMock(return_value=[])

        with patch("app.models.memory.set_location_memory"):
            result = await agent.build_location_memory(gq, "loc-1", "Cave", world_day=3)
            assert result is not None
            assert "Recent events" in result

    @pytest.mark.asyncio
    async def test_build_location_memory_only_npcs(self):
        from app.agents.memory_architect import MemoryArchitect

        agent = MemoryArchitect()
        gq = MagicMock()
        gq.get_events_at_location = AsyncMock(return_value=[])
        gq.get_npcs_at_location = AsyncMock(return_value=[
            {"name": "Farmer", "current_activity": "harvesting"},
        ])

        with patch("app.models.memory.set_location_memory"):
            result = await agent.build_location_memory(gq, "loc-farm", "Farm", world_day=5)
            assert result is not None
            assert "People here" in result
