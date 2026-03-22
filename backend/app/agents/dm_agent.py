"""Dungeon Master narration and quest generation agent."""

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("dm_agent")


class DMAgent:
    """Handles DM narration and quest generation."""

    def __init__(self):
        self._narrate_agent = BaseAgent("dm_narrate.j2")
        self._quest_agent = BaseAgent("dm_quest.j2")
        self._quest_gen_agent = BaseAgent("quest_generate.j2")

    async def narrate(
        self,
        player_action: str,
        location_name: str,
        location_description: str,
        present_npcs: list[dict],
        recent_events: list[str],
        inventory: list[str],
        reputation: int,
        world_day: int,
        player_level: int = 1,
        player_class: str = "commoner",
        player_hp: int = 10,
        player_max_hp: int = 10,
        player_ac: int = 10,
        time_of_day: str = "day",
    ) -> dict:
        """Generate DM narration for a player action."""
        result = await self._narrate_agent.generate_json(
            player_action=player_action,
            location_name=location_name,
            location_description=location_description,
            present_npcs=present_npcs,
            recent_events=recent_events,
            inventory=inventory,
            reputation=reputation,
            world_day=world_day,
            player_level=player_level,
            player_class=player_class,
            player_hp=player_hp,
            player_max_hp=player_max_hp,
            player_ac=player_ac,
            time_of_day=time_of_day,
        )

        if not result:
            return {
                "narration": "Nothing seems to happen...",
                "npcs_involved": [],
                "items_changed": [],
                "location_changed": None,
                "reputation_changes": {},
            }

        return {
            "narration": result.get("narration", "The world is quiet."),
            "npcs_involved": result.get("npcs_involved", []),
            "items_changed": result.get("items_changed", []),
            "location_changed": result.get("location_changed"),
            "reputation_changes": result.get("reputation_changes", {}),
        }

    async def generate_quest(
        self,
        conflicts: list[str],
        recent_events: list[str],
        reputation: int,
        location_name: str,
        world_day: int,
    ) -> dict:
        """Generate a quest from current world state."""
        result = await self._quest_agent.generate_json(
            conflicts=conflicts,
            recent_events=recent_events,
            reputation=reputation,
            location_name=location_name,
            world_day=world_day,
        )

        if not result:
            return {}

        return {
            "quest_name": result.get("quest_name", "Unknown Quest"),
            "description": result.get("description", ""),
            "quest_giver_npc_id": result.get("quest_giver_npc_id"),
            "objectives": result.get("objectives", []),
            "reward": result.get("reward", "gratitude"),
            "difficulty": result.get("difficulty", "medium"),
        }


    async def generate_scenario_quest(
        self,
        scenario_title: str,
        scenario_description: str,
        phase_name: str,
        npcs: list[dict],
        recent_events: list[str],
    ) -> dict | None:
        result = await self._quest_gen_agent.generate_json(
            scenario_title=scenario_title,
            scenario_description=scenario_description,
            phase_name=phase_name,
            npcs=npcs,
            recent_events=recent_events,
        )
        if not result or "title" not in result:
            return None
        return result


dm_agent = DMAgent()
