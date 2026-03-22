"""Scheduler: decides which NPCs are active during a tick."""

from app.config import settings
from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("scheduler")


async def get_active_npcs(
    gq: GraphQueries,
    all_npcs: list[dict],
    player_id: str,
) -> list[dict]:
    """
    Select which NPCs are active this tick.
    Priority:
    1. NPCs at the player's location
    2. NPCs with active goals/quests
    3. Random selection of remaining NPCs
    """
    max_active = settings.max_active_npcs_per_tick
    active: list[dict] = []
    seen_ids: set[str] = set()

    # Priority 1: NPCs near the player
    player_loc = await gq.get_player_location(player_id)
    if player_loc:
        nearby = await gq.get_npcs_at_location(player_loc["id"])
        for npc in nearby:
            if npc["id"] not in seen_ids:
                active.append(npc)
                seen_ids.add(npc["id"])

    # Priority 2: NPCs with goals (they're more "interesting")
    for npc in all_npcs:
        if len(active) >= max_active:
            break
        if npc["id"] not in seen_ids and npc.get("goals"):
            active.append(npc)
            seen_ids.add(npc["id"])

    # Priority 3: Fill remaining slots with other NPCs
    import random
    remaining = [n for n in all_npcs if n["id"] not in seen_ids]
    random.shuffle(remaining)
    for npc in remaining:
        if len(active) >= max_active:
            break
        active.append(npc)
        seen_ids.add(npc["id"])

    log.info("npcs_scheduled", total=len(all_npcs), active=len(active))
    return active
