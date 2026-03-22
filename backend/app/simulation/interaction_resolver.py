"""NPC interaction resolution — extracted from ticker.py."""

from __future__ import annotations

import random

from app.graph.queries import GraphQueries
from app.models.memory import add_memory
from app.utils.logger import get_logger

log = get_logger("interactions")


async def resolve_interactions(
    gq: GraphQueries,
    npc_agent_inst,
    active_npcs: list[dict],
    world_day: int,
    scenario_context: str | None = None,
) -> list[dict]:
    """Find NPC pairs at same locations and resolve their interactions."""
    interactions = []
    locations_to_npcs: dict[str, list[dict]] = {}
    loc_name_map: dict[str, str] = {}

    for npc in active_npcs:
        loc = await gq.get_npc_location(npc["id"])
        if loc:
            locations_to_npcs.setdefault(loc["id"], []).append(npc)
            loc_name_map[loc["id"]] = loc["name"]

    # Run interactions in parallel per location
    import asyncio

    async def _run_pair(npc_a, npc_b, loc_id):
        try:
            a_rels = await gq.get_relationships(npc_a["id"])
            b_rels = await gq.get_relationships(npc_b["id"])
            a_to_b = next((r for r in a_rels if r["id"] == npc_b["id"]), None)
            b_to_a = next((r for r in b_rels if r["id"] == npc_a["id"]), None)

            result = await npc_agent_inst.interact(npc_a, npc_b, {
                "a_to_b_relationship": a_to_b,
                "b_to_a_relationship": b_to_a,
                "location_name": loc_name_map.get(loc_id, "the village"),
                "scenario_context": scenario_context,
            })

            # Apply relationship changes
            if result.get("a_sentiment_change"):
                old = a_to_b["sentiment"] if a_to_b else 0.0
                new_s = min(1.0, max(-1.0, old + result["a_sentiment_change"]))
                await gq.set_relationship(npc_a["id"], npc_b["id"], new_s, "recent interaction")

            if result.get("b_sentiment_change"):
                old = b_to_a["sentiment"] if b_to_a else 0.0
                new_s = min(1.0, max(-1.0, old + result["b_sentiment_change"]))
                await gq.set_relationship(npc_b["id"], npc_a["id"], new_s, "recent interaction")

            # Apply mood changes
            for npc_ref, mood_key in [(npc_a, "a_mood_change"), (npc_b, "b_mood_change")]:
                mc = result.get(mood_key, "same")
                if mc != "same":
                    mood = npc_ref["mood"]
                    if mc == "better":
                        mood = "content" if mood in ("angry", "fearful") else "excited"
                    elif mc == "worse":
                        mood = "angry" if mood in ("content", "excited") else "fearful"
                    if mood != npc_ref["mood"]:
                        await gq.update_npc(npc_ref["id"], {"mood": mood})

            # Execute interaction action
            from app.simulation.ticker import _resolve_npc_combat
            action = result.get("action", "none")
            initiator_key = result.get("action_initiator", "a")
            attacker = npc_a if initiator_key == "a" else npc_b
            defender = npc_b if initiator_key == "a" else npc_a

            if action == "fight" and attacker.get("alive", True) and defender.get("alive", True):
                await _resolve_npc_combat(gq, attacker, defender, "fight", world_day)
            elif action == "rob":
                await _resolve_npc_combat(gq, attacker, defender, "rob", world_day)
            elif action == "trade":
                details = result.get("action_details", {})
                amount = min(details.get("gold_amount", 2), attacker.get("gold", 0) or 1)
                if amount > 0:
                    await gq.transfer_gold(attacker["id"], defender["id"], amount)
            elif action == "help":
                old_s = (b_to_a["sentiment"] if b_to_a else 0.0) if initiator_key == "a" else (a_to_b["sentiment"] if a_to_b else 0.0)
                await gq.set_relationship(defender["id"], attacker["id"], min(1.0, old_s + 0.2), f"helped by {attacker['name']}")
            elif action == "threaten":
                old_s = (b_to_a["sentiment"] if b_to_a else 0.0) if initiator_key == "a" else (a_to_b["sentiment"] if a_to_b else 0.0)
                await gq.set_relationship(defender["id"], attacker["id"], max(-1.0, old_s - 0.3), f"threatened by {attacker['name']}")
                await gq.update_npc(defender["id"], {"mood": "fearful"})
            elif action == "gift":
                details = result.get("action_details", {})
                amount = min(details.get("gold_amount", 1), attacker.get("gold", 0) or 1)
                if amount > 0:
                    await gq.transfer_gold(attacker["id"], defender["id"], amount)

            # Store memories
            add_memory(npc_a["id"], f"Day {world_day}: Interacted with {npc_b['name']}. {result['summary']}", day=world_day)
            add_memory(npc_b["id"], f"Day {world_day}: Interacted with {npc_a['name']}. {result['summary']}", day=world_day)

            return {
                "npc_a": npc_a["name"],
                "npc_b": npc_b["name"],
                "summary": result["summary"],
                "interaction_type": result.get("interaction_type", "conversation"),
                "action": result.get("action", "none"),
            }
        except Exception as e:
            log.error("interaction_failed", a=npc_a["name"], b=npc_b["name"], error=str(e))
            return None

    # Collect all pairs
    all_pairs = []
    for loc_id, npcs_here in locations_to_npcs.items():
        if len(npcs_here) < 2:
            continue
        shuffled = list(npcs_here)
        random.shuffle(shuffled)
        for i in range(0, len(shuffled) - 1, 2):
            all_pairs.append((shuffled[i], shuffled[i + 1], loc_id))

    # Limit total interactions
    all_pairs = all_pairs[:15]

    # Run all interactions in parallel
    results = await asyncio.gather(
        *[_run_pair(a, b, lid) for a, b, lid in all_pairs],
        return_exceptions=True,
    )

    for r in results:
        if r and not isinstance(r, Exception):
            interactions.append(r)

    return interactions
