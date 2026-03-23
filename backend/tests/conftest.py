"""Shared test fixtures for the DND backend test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_graph_queries():
    """Mock GraphQueries with all async methods stubbed."""
    gq = MagicMock()

    # NPC operations
    gq.create_npc = AsyncMock()
    gq.get_npc = AsyncMock(return_value=None)
    gq.get_all_npcs = AsyncMock(return_value=[])
    gq.update_npc = AsyncMock()
    gq.kill_npc = AsyncMock()
    gq.damage_npc = AsyncMock(return_value=None)
    gq.heal_npc = AsyncMock()
    gq.transfer_gold = AsyncMock(return_value=True)

    # Location operations
    gq.create_location = AsyncMock()
    gq.connect_locations = AsyncMock()
    gq.get_all_locations = AsyncMock(return_value=[])
    gq.get_connected_locations = AsyncMock(return_value=[])

    # NPC Location operations
    gq.set_npc_location = AsyncMock()
    gq.get_npcs_at_location = AsyncMock(return_value=[])
    gq.get_dead_npcs_at_location = AsyncMock(return_value=[])
    gq.get_npc_location = AsyncMock(return_value=None)

    # Relationships
    gq.set_relationship = AsyncMock()
    gq.get_relationships = AsyncMock(return_value=[])
    gq.set_knows = AsyncMock()

    # Items
    gq.create_item = AsyncMock()
    gq.give_item_to_npc = AsyncMock()

    # Factions
    gq.create_faction = AsyncMock()
    gq.set_faction_member = AsyncMock()

    # Player operations
    gq.create_player = AsyncMock()
    gq.get_player = AsyncMock(return_value=None)
    gq.set_player_location = AsyncMock()
    gq.get_player_location = AsyncMock(return_value=None)
    gq.set_player_reputation = AsyncMock()
    gq.get_player_reputation = AsyncMock(return_value=0)
    gq.give_item_to_player = AsyncMock()
    gq.get_player_items = AsyncMock(return_value=[])
    gq.update_player = AsyncMock()

    # World events
    gq.create_world_event = AsyncMock()
    gq.link_event_to_npc = AsyncMock()
    gq.link_event_to_location = AsyncMock()
    gq.get_recent_events = AsyncMock(return_value=[])

    # World map
    gq.get_world_map = AsyncMock(return_value={"locations": [], "connections": []})

    # Scenarios
    gq.create_scenario = AsyncMock()
    gq.get_active_scenarios = AsyncMock(return_value=[])
    gq.update_scenario = AsyncMock()
    gq.deactivate_scenario = AsyncMock()
    gq.link_scenario_to_npc = AsyncMock()

    # World state
    gq.get_world_day = AsyncMock(return_value=1)
    gq.increment_world_day = AsyncMock(return_value=2)

    # Quests
    gq.create_quest = AsyncMock()
    gq.get_quests = AsyncMock(return_value=[])
    gq.update_quest = AsyncMock()

    # XP
    gq.add_player_xp = AsyncMock(return_value={"leveled_up": False, "level": 1, "xp": 10, "xp_needed": 100})

    # Utility
    gq.clear_all = AsyncMock()

    return gq
