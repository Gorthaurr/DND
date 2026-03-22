"""Quest generation from NPC conflicts and world state."""

from app.agents.dm_agent import dm_agent
from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("quests")


async def detect_conflicts(gq: GraphQueries) -> list[str]:
    """Detect conflicts between NPCs based on negative relationships."""
    all_npcs = await gq.get_all_npcs()
    conflicts = []

    for npc in all_npcs:
        rels = await gq.get_relationships(npc["id"])
        for rel in rels:
            if rel["sentiment"] < -0.3:
                conflicts.append(
                    f"{npc['name']} has negative feelings toward {rel['name']}: {rel['reason']}"
                )

    return conflicts


async def generate_quest_from_world(gq: GraphQueries, player_id: str) -> dict | None:
    """Generate a quest based on current world state."""
    conflicts = await detect_conflicts(gq)
    if not conflicts:
        return None

    recent_events = await gq.get_recent_events(0, limit=5)
    event_descs = [e["description"] for e in recent_events]

    player_loc = await gq.get_player_location(player_id)
    reputation = 0  # TODO: aggregate reputation

    quest = await dm_agent.generate_quest(
        conflicts=conflicts,
        recent_events=event_descs,
        reputation=reputation,
        location_name=player_loc["name"] if player_loc else "unknown",
        world_day=1,
    )

    if quest:
        log.info("quest_generated", name=quest.get("quest_name"))

    return quest if quest else None
