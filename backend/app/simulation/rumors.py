"""Rumor propagation system — NPCs share information with nearby NPCs."""

import random

from app.graph.queries import GraphQueries
from app.models.memory import add_memory, get_recent_memories
from app.utils.logger import get_logger

log = get_logger("rumors")


async def propagate_rumors(gq: GraphQueries, active_npcs: list[dict], world_day: int) -> None:
    """
    Spread information between NPCs who are at the same location.
    Each NPC has a chance to share a recent memory with a nearby NPC.
    """
    # Group NPCs by location
    location_groups: dict[str, list[dict]] = {}
    for npc in active_npcs:
        loc = await gq.get_npc_location(npc["id"])
        if loc:
            location_groups.setdefault(loc["id"], []).append(npc)

    rumors_spread = 0

    for loc_id, npcs in location_groups.items():
        if len(npcs) < 2:
            continue

        for npc in npcs:
            # 30% chance this NPC shares something
            if random.random() > 0.3:
                continue

            memories = get_recent_memories(npc["id"], limit=5)
            if not memories:
                continue

            # Pick a random memory to share
            memory = random.choice(memories)

            # Skip meta-memories and summaries
            if memory.startswith("[Summary]") or "heard a rumor" in memory.lower():
                continue

            # Share with a random nearby NPC
            recipients = [n for n in npcs if n["id"] != npc["id"]]
            if not recipients:
                continue

            recipient = random.choice(recipients)

            # Check relationship — enemies are less likely to share
            rels = await gq.get_relationships(npc["id"])
            rel_to_recipient = next((r for r in rels if r["id"] == recipient["id"]), None)
            if rel_to_recipient and rel_to_recipient["sentiment"] < -0.5:
                continue

            # Add as rumor to recipient
            rumor_text = f"Day {world_day}: Heard a rumor from {npc['name']}: {memory}"
            add_memory(recipient["id"], rumor_text, day=world_day, importance=0.3)
            rumors_spread += 1

    if rumors_spread:
        log.info("rumors_propagated", count=rumors_spread)
