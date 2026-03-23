"""World analytics — aggregates simulation data for reports."""

from __future__ import annotations

from app.graph.queries import GraphQueries
from app.models.memory import get_recent_memories
from app.utils.logger import get_logger

log = get_logger("analytics")


async def get_world_report(gq: GraphQueries, from_day: int, to_day: int) -> dict:
    """Collect comprehensive world data for a given day range."""
    events = await gq.get_events_in_range(from_day, to_day)
    all_rels = await gq.get_all_relationships()
    active_scenarios = await gq.get_active_scenarios()
    completed_scenarios = await gq.get_completed_scenarios()
    dead_npcs = await gq.get_dead_npcs()
    npc_stats = await gq.get_npc_stats_summary()
    world_day = await gq.get_world_day()

    # Categorize relationships
    alliances = [r for r in all_rels if r["sentiment"] >= 0.5]
    rivalries = [r for r in all_rels if r["sentiment"] <= -0.5]

    # Get key memories from living NPCs
    all_npcs = await gq.get_all_npcs()
    notable_memories: list[dict] = []
    for npc in all_npcs[:20]:
        mems = get_recent_memories(npc["id"], limit=3)
        for m in mems:
            notable_memories.append({"npc_name": npc["name"], "memory": m})

    return {
        "world_day": world_day,
        "period": {"from_day": from_day, "to_day": to_day},
        "events": [{"day": e.get("day"), "description": e.get("description"), "type": e.get("type")} for e in events],
        "deaths": [{"name": n.get("name"), "occupation": n.get("occupation")} for n in dead_npcs],
        "npc_stats": npc_stats,
        "relationships": {
            "total": len(all_rels),
            "alliances": [{"from": r["from_name"], "to": r["to_name"], "sentiment": r["sentiment"]} for r in alliances],
            "rivalries": [{"from": r["from_name"], "to": r["to_name"], "sentiment": r["sentiment"]} for r in rivalries],
        },
        "scenarios": {
            "active": [{"title": s.get("title"), "tension": s.get("tension_level")} for s in active_scenarios],
            "completed": [{"title": s.get("title")} for s in completed_scenarios],
        },
        "notable_memories": notable_memories[:20],
    }


async def get_event_timeline(gq: GraphQueries, limit: int = 50) -> list[dict]:
    """Get a chronological timeline of key world events."""
    world_day = await gq.get_world_day()
    from_day = max(1, world_day - 50)
    events = await gq.get_events_in_range(from_day, world_day)

    timeline = []
    for e in events[:limit]:
        timeline.append({
            "day": e.get("day"),
            "description": e.get("description"),
            "type": e.get("type", "event"),
        })

    # Add deaths as timeline entries
    dead_npcs = await gq.get_dead_npcs()
    for npc in dead_npcs:
        timeline.append({
            "day": None,
            "description": f"{npc.get('name')} ({npc.get('occupation')}) died",
            "type": "death",
        })

    timeline.sort(key=lambda x: x.get("day") or 0)
    return timeline
