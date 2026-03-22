"""Reputation system — tracks player standing with NPCs and factions."""

from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("reputation")


async def update_reputation(
    gq: GraphQueries,
    player_id: str,
    npc_id: str,
    change: int,
    reason: str = "",
) -> int:
    """Update player reputation with a specific NPC."""
    current = await gq.get_player_reputation(player_id, npc_id)
    new_value = max(-100, min(100, current + change))
    await gq.set_player_reputation(player_id, npc_id, new_value)
    log.info("reputation_changed", npc=npc_id, old=current, new=new_value, reason=reason)
    return new_value


async def get_reputation_summary(gq: GraphQueries, player_id: str) -> dict:
    """Get a summary of player's reputation across all NPCs."""
    all_npcs = await gq.get_all_npcs()
    summary = {}
    for npc in all_npcs:
        rep = await gq.get_player_reputation(player_id, npc["id"])
        if rep != 0:
            summary[npc["name"]] = rep
    return summary


def reputation_label(value: int) -> str:
    """Convert numeric reputation to a human-readable label."""
    if value >= 80:
        return "Hero"
    elif value >= 50:
        return "Trusted Friend"
    elif value >= 20:
        return "Friendly"
    elif value >= -20:
        return "Neutral"
    elif value >= -50:
        return "Distrusted"
    elif value >= -80:
        return "Hated"
    else:
        return "Nemesis"
