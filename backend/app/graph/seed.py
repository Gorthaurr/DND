"""Load world preset data into Neo4j."""

import json
from pathlib import Path

from neo4j import AsyncDriver

from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("seed")


async def seed_world(driver: AsyncDriver, world_dir: Path) -> None:
    """Load a world preset from JSON files into Neo4j."""
    gq = GraphQueries(driver)

    # Clear existing data
    await gq.clear_all()

    # Load world.json (locations and connections)
    world_file = world_dir / "world.json"
    with open(world_file, encoding="utf-8") as f:
        world_data = json.load(f)

    for loc in world_data["locations"]:
        await gq.create_location(loc)
        log.info("location_created", name=loc["name"])

    for conn in world_data.get("connections", []):
        await gq.connect_locations(conn["from"], conn["to"], conn.get("distance", 1))

    # Load factions
    for faction in world_data.get("factions", []):
        await gq.create_faction(faction)
        log.info("faction_created", name=faction["name"])

    # Load npcs.json
    npcs_file = world_dir / "npcs.json"
    with open(npcs_file, encoding="utf-8") as f:
        npcs_data = json.load(f)

    # First pass: create all NPCs and place them
    npc_relationships: dict[str, list[dict]] = {}
    for npc in npcs_data["npcs"]:
        npc_copy = dict(npc)
        location_id = npc_copy.pop("location_id", None)
        faction_info = npc_copy.pop("faction", None)
        relationships = npc_copy.pop("relationships", [])
        npc_copy.pop("schedule", None)  # Schedule is handled at runtime, not in graph

        npc_relationships[npc_copy["id"]] = relationships

        await gq.create_npc(npc_copy)
        log.info("npc_created", name=npc_copy["name"], archetype=npc_copy.get("archetype"))

        if location_id:
            await gq.set_npc_location(npc_copy["id"], location_id)
        if faction_info:
            await gq.set_faction_member(npc_copy["id"], faction_info["id"], faction_info["role"])

    # Second pass: set up relationships (after all NPCs exist)
    for npc_id, rels in npc_relationships.items():
        for rel in rels:
            await gq.set_relationship(npc_id, rel["target_id"], rel["sentiment"], rel["reason"])
            await gq.set_knows(npc_id, rel["target_id"], 0, rel.get("context", "known each other"))

    # Create items
    for item in world_data.get("items", []):
        owner_id = item.pop("owner_id", None)
        await gq.create_item(item)
        if owner_id:
            await gq.give_item_to_npc(item["id"], owner_id)

    # Create default player
    player = {
        "id": "player-1",
        "name": "Adventurer",
        "reputation": 0,
        "gold": 50,
    }
    await gq.create_player(player)
    start_location = world_data.get("start_location", world_data["locations"][0]["id"])
    await gq.set_player_location(player["id"], start_location)

    log.info("world_seeded", world=world_dir.name)
