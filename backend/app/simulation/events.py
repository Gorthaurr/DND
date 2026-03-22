"""World event processing and memory summarization."""

import uuid

from app.graph.queries import GraphQueries
from app.models.memory import add_memory, get_old_memories, mark_summarized
from app.utils.llm import generate
from app.utils.logger import get_logger

log = get_logger("events")


async def process_events(gq: GraphQueries, events: list[dict], world_day: int) -> list[dict]:
    """Process generated events: create in graph and notify affected NPCs."""
    results = []

    for event in events:
        # Create event in graph
        event_data = {
            "id": event.get("id", f"evt-{uuid.uuid4().hex[:8]}"),
            "day": world_day,
            "description": event["description"],
            "type": event.get("type", "natural"),
        }
        await gq.create_world_event(event_data)

        # Link to location
        if event.get("location_id"):
            await gq.link_event_to_location(event_data["id"], event["location_id"])

            # Notify NPCs at that location
            affected_npcs = await gq.get_npcs_at_location(event["location_id"])
            for npc in affected_npcs:
                add_memory(npc["id"], f"Day {world_day}: {event['description']}", day=world_day, importance=0.7)
                await gq.link_event_to_npc(event_data["id"], npc["id"])

        # Also notify specifically mentioned NPCs
        for npc_id in event.get("affected_npc_ids", []):
            add_memory(npc_id, f"Day {world_day}: {event['description']}", day=world_day, importance=0.7)
            await gq.link_event_to_npc(event_data["id"], npc_id)

        results.append(event_data)
        log.info("event_processed", description=event["description"][:50])

    return results


async def summarize_old_memories(npc_id: str) -> None:
    """Summarize old memories into a condensed form using LLM."""
    old_memories = get_old_memories(npc_id, limit=20)
    if len(old_memories) < 10:
        return

    memories_text = "\n".join(f"- {m['content']}" for m in old_memories)
    prompt = (
        f"Summarize these memories into 2-3 key points that this person would remember:\n\n"
        f"{memories_text}\n\n"
        f"Write 2-3 concise summary statements."
    )

    try:
        summary = await generate(prompt, temperature=0.3)
        if summary:
            # Mark old memories as summarized
            ids = [m["id"] for m in old_memories]
            mark_summarized(ids)

            # Add summary as new memory
            for line in summary.strip().split("\n"):
                line = line.strip().lstrip("- ")
                if line:
                    add_memory(npc_id, f"[Summary] {line}", day=old_memories[-1].get("day", 0), importance=0.8)

            log.info("memories_summarized", npc_id=npc_id, old_count=len(old_memories))
    except Exception as e:
        log.error("summarize_failed", npc_id=npc_id, error=str(e))
