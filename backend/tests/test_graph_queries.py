"""Tests for app.graph.queries — GraphQueries class."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graph.queries import GraphQueries


class MockResult:
    """Simulates neo4j async result with async iteration."""

    def __init__(self, records=None, single_record=None):
        self._records = records or []
        self._single_record = single_record

    async def single(self):
        return self._single_record

    def __aiter__(self):
        return self._ait()

    async def _ait(self):
        for r in self._records:
            yield r


@pytest.fixture
def gq():
    """Create GraphQueries with a mocked neo4j driver."""
    driver = MagicMock()
    session = MagicMock()

    # Make session an async context manager
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)

    driver.session.return_value = session

    gq = GraphQueries(driver, world_id="test-world")
    gq._mock_session = session  # expose for assertions
    return gq


@pytest.mark.asyncio
async def test_world_id_property(gq):
    assert gq.world_id == "test-world"


@pytest.mark.asyncio
async def test_create_npc(gq):
    npc = {"id": "npc-1", "name": "Ava", "mood": "neutral", "occupation": "healer", "age": 25}
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.create_npc(npc)
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_npc_found(gq):
    record = {"n": {"id": "npc-1", "name": "Ava"}}
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=record))
    result = await gq.get_npc("npc-1")
    assert result == {"id": "npc-1", "name": "Ava"}


@pytest.mark.asyncio
async def test_get_npc_not_found(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=None))
    result = await gq.get_npc("npc-unknown")
    assert result is None


@pytest.mark.asyncio
async def test_get_all_npcs(gq):
    records = [{"n": {"id": "npc-1"}}, {"n": {"id": "npc-2"}}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_all_npcs()
    assert len(result) == 2
    assert result[0]["id"] == "npc-1"


@pytest.mark.asyncio
async def test_update_npc(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.update_npc("npc-1", {"mood": "angry", "current_activity": "fighting"})
    call_args = gq._mock_session.run.call_args
    cypher = call_args[0][0]
    assert "n.mood" in cypher
    assert "n.current_activity" in cypher


@pytest.mark.asyncio
async def test_kill_npc(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.kill_npc("npc-1")
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_world_event(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    event = {"id": "evt-1", "day": 5, "description": "Storm", "type": "weather"}
    await gq.create_world_event(event)
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recent_events(gq):
    records = [{"e": {"id": "evt-1", "day": 5, "description": "Storm"}}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_recent_events(3)
    assert len(result) == 1
    assert result[0]["description"] == "Storm"


@pytest.mark.asyncio
async def test_create_location(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    loc = {"id": "loc-1", "name": "Tavern", "type": "building", "description": "A cozy tavern"}
    await gq.create_location(loc)
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_locations(gq):
    records = [{"l": {"id": "loc-1", "name": "Tavern"}}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_all_locations()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_set_npc_location(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.set_npc_location("npc-1", "loc-1")
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_npc_location_found(gq):
    record = {"l": {"id": "loc-1", "name": "Market"}}
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=record))
    result = await gq.get_npc_location("npc-1")
    assert result["name"] == "Market"


@pytest.mark.asyncio
async def test_get_npc_location_not_found(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=None))
    result = await gq.get_npc_location("npc-1")
    assert result is None


@pytest.mark.asyncio
async def test_set_relationship(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.set_relationship("npc-a", "npc-b", 0.5, "friends")
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_relationships(gq):
    records = [{"name": "Bob", "id": "npc-b", "sentiment": 0.3, "reason": "helped me"}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_relationships("npc-a")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


@pytest.mark.asyncio
async def test_transfer_gold_success(gq):
    # First call: check balance => 10 gold
    # Second call: subtract
    # Third call: add
    check_result = MockResult(single_record={"gold": 10})
    sub_result = MockResult()
    add_result = MockResult()
    gq._mock_session.run = AsyncMock(side_effect=[check_result, sub_result, add_result])

    result = await gq.transfer_gold("from-npc", "to-npc", 5)
    assert result is True
    assert gq._mock_session.run.await_count == 3


@pytest.mark.asyncio
async def test_transfer_gold_insufficient(gq):
    check_result = MockResult(single_record={"gold": 2})
    gq._mock_session.run = AsyncMock(return_value=check_result)

    result = await gq.transfer_gold("from-npc", "to-npc", 5)
    assert result is False


@pytest.mark.asyncio
async def test_increment_world_day(gq):
    record = {"day": 7}
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=record))
    day = await gq.increment_world_day()
    assert day == 7


@pytest.mark.asyncio
async def test_get_world_day(gq):
    record = {"day": 3}
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=record))
    day = await gq.get_world_day()
    assert day == 3


@pytest.mark.asyncio
async def test_clear_all(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    await gq.clear_all()
    gq._mock_session.run.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_dead_npcs(gq):
    records = [{"n": {"id": "dead-1", "name": "Ghost", "alive": False}}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_dead_npcs()
    assert len(result) == 1
    assert result[0]["alive"] is False


@pytest.mark.asyncio
async def test_get_all_factions(gq):
    records = [{"f": {"id": "fac-1", "name": "Thieves Guild"}}]
    gq._mock_session.run = AsyncMock(return_value=MockResult(records=records))
    result = await gq.get_all_factions()
    assert len(result) == 1
    assert result[0]["name"] == "Thieves Guild"


@pytest.mark.asyncio
async def test_create_quest(gq):
    gq._mock_session.run = AsyncMock(return_value=MockResult())
    quest = {
        "id": "q-1",
        "title": "Save the Village",
        "description": "Help the villagers",
        "objectives": [{"text": "Talk to elder"}],
    }
    await gq.create_quest(quest)
    gq._mock_session.run.assert_awaited()


@pytest.mark.asyncio
async def test_get_npc_stats_summary(gq):
    record = {"total": 10, "alive": 8, "dead": 2, "avg_gold": 15.5}
    gq._mock_session.run = AsyncMock(return_value=MockResult(single_record=record))
    result = await gq.get_npc_stats_summary()
    assert result["total"] == 10
    assert result["alive"] == 8
