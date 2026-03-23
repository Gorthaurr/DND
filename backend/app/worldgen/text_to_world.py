"""Pipeline: text description → full world preset (JSON files)."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from app.config import settings
from app.utils.logger import get_logger
from app.worldgen.ontology import npc_generator, ontology_extractor

log = get_logger("worldgen")


async def generate_world_from_text(text: str, world_name: str | None = None) -> dict:
    """Full pipeline: extract entities from text and generate world JSON files.

    Returns dict with paths to generated files and world metadata.
    """
    # Step 1: Extract entities
    log.info("worldgen_extracting", text_len=len(text))
    extracted = await ontology_extractor.extract(text)

    if not extracted.get("locations"):
        log.error("worldgen_no_locations_extracted")
        return {"error": "Could not extract any locations from the text."}

    name = world_name or _slugify(extracted.get("world_name", "generated_world"))
    world_dir = settings.worlds_dir / name
    world_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Build world.json
    world_json = _build_world_json(extracted)
    (world_dir / "world.json").write_text(json.dumps(world_json, indent=2), encoding="utf-8")

    # Step 3: Generate full NPC definitions
    log.info("worldgen_generating_npcs", count=len(extracted.get("npcs", [])))
    npcs_raw = await npc_generator.generate(
        extracted.get("npcs", []),
        extracted.get("world_description", text[:500]),
    )
    npcs_json = _build_npcs_json(npcs_raw, world_json)
    (world_dir / "npcs.json").write_text(json.dumps(npcs_json, indent=2), encoding="utf-8")

    # Step 4: Build scenarios from conflicts
    scenarios_json = _build_scenarios_json(extracted.get("conflicts", []), npcs_json)
    (world_dir / "scenarios.json").write_text(json.dumps(scenarios_json, indent=2), encoding="utf-8")

    # Step 5: Build events
    events_json = _build_events_json(world_json, extracted)
    (world_dir / "events.json").write_text(json.dumps(events_json, indent=2), encoding="utf-8")

    log.info("worldgen_complete", world=name, locations=len(world_json["locations"]),
             npcs=len(npcs_json), scenarios=len(scenarios_json))

    return {
        "world_name": name,
        "world_dir": str(world_dir),
        "locations": len(world_json["locations"]),
        "npcs": len(npcs_json),
        "scenarios": len(scenarios_json),
        "events": len(events_json),
    }


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "_", text)[:50]


def _build_world_json(extracted: dict) -> dict:
    """Build world.json from extracted entities."""
    locations = []
    for i, loc in enumerate(extracted.get("locations", [])):
        loc_id = f"loc-{_slugify(loc.get('name', f'place{i}'))}"
        locations.append({
            "id": loc_id,
            "name": loc.get("name", f"Place {i}"),
            "type": loc.get("type", "building"),
            "description": loc.get("description", ""),
        })

    # Build connections — connect each location to 2-3 neighbors
    connections = []
    for i in range(len(locations)):
        for j in range(i + 1, min(i + 3, len(locations))):
            connections.append({
                "from": locations[i]["id"],
                "to": locations[j]["id"],
                "distance": 1,
            })

    factions = []
    for f in extracted.get("factions", []):
        factions.append({
            "id": f"fac-{_slugify(f.get('name', 'faction'))}",
            "name": f.get("name", "Unknown Faction"),
            "description": f.get("description", ""),
            "goals": f.get("goals", []),
        })

    return {
        "name": extracted.get("world_name", "Generated World"),
        "description": extracted.get("world_description", ""),
        "locations": locations,
        "connections": connections,
        "factions": factions,
        "start_location": locations[0]["id"] if locations else "",
    }


def _build_npcs_json(npcs_raw: list[dict], world_json: dict) -> list[dict]:
    """Ensure NPCs have all required fields."""
    location_ids = [loc["id"] for loc in world_json.get("locations", [])]
    npcs = []

    for i, npc in enumerate(npcs_raw):
        npc_id = f"npc-{_slugify(npc.get('name', f'npc{i}'))}"
        loc_id = npc.get("location_id")
        if not loc_id or loc_id not in location_ids:
            loc_id = location_ids[i % len(location_ids)] if location_ids else ""

        npcs.append({
            "id": npc_id,
            "name": npc.get("name", f"NPC {i}"),
            "occupation": npc.get("occupation", "villager"),
            "age": npc.get("age", 30),
            "personality": npc.get("personality", "Moderate in all Big Five traits"),
            "backstory": npc.get("backstory", ""),
            "goals": npc.get("goals", ["survive", "prosper"]),
            "mood": npc.get("mood", "neutral"),
            "archetype": npc.get("archetype"),
            "location_id": loc_id,
            "faction_id": npc.get("faction_id"),
            "faction_role": npc.get("faction_role"),
            "gold": npc.get("gold", 5),
            "level": npc.get("level", 1),
            "class_id": npc.get("class_id", "commoner"),
            "max_hp": npc.get("max_hp", 10),
            "ac": npc.get("ac", 10),
            "ability_scores": npc.get("ability_scores", {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10}),
            "equipment_ids": npc.get("equipment_ids", []),
            "relationships": npc.get("relationships", []),
        })

    return npcs


def _build_scenarios_json(conflicts: list[dict], npcs: list[dict]) -> list[dict]:
    """Generate scenario templates from extracted conflicts."""
    npc_ids = [n["id"] for n in npcs]
    scenarios = []

    for conflict in conflicts:
        scenario_id = f"sc-{uuid.uuid4().hex[:8]}"
        involved = conflict.get("involved_npc_ids", [])
        # Map names to IDs if needed
        if not involved and conflict.get("involved_npcs"):
            for name in conflict["involved_npcs"]:
                matched = next((n["id"] for n in npcs if name.lower() in n["name"].lower()), None)
                if matched:
                    involved.append(matched)
        if not involved and len(npc_ids) >= 2:
            involved = npc_ids[:2]

        scenarios.append({
            "id": scenario_id,
            "title": conflict.get("title", "Unnamed Conflict"),
            "description": conflict.get("description", ""),
            "scenario_type": conflict.get("type", "main"),
            "tension_level": conflict.get("tension", "rising"),
            "involved_npc_ids": involved,
            "phases": conflict.get("phases", [
                {"name": "setup", "description": "The conflict begins to emerge.", "duration_days": 3},
                {"name": "escalation", "description": "Tensions rise.", "duration_days": 5},
                {"name": "crisis", "description": "The situation reaches a breaking point.", "duration_days": 3},
                {"name": "resolution", "description": "The conflict is resolved or transformed.", "duration_days": 2},
            ]),
        })

    return scenarios


def _build_events_json(world_json: dict, extracted: dict) -> list[dict]:
    """Generate basic event templates for the world."""
    location_ids = [loc["id"] for loc in world_json.get("locations", [])]
    events = []

    # Generic events applicable to any world
    templates = [
        {"type": "natural", "template": "Strange weather affects {loc}", "severity": 2},
        {"type": "social", "template": "A dispute breaks out at {loc}", "severity": 3},
        {"type": "trade", "template": "A traveling merchant arrives at {loc}", "severity": 1},
        {"type": "conflict", "template": "Suspicious strangers seen near {loc}", "severity": 4},
        {"type": "natural", "template": "An unusual sound echoes through {loc}", "severity": 2},
        {"type": "social", "template": "A celebration begins at {loc}", "severity": 1},
    ]

    for i, tmpl in enumerate(templates):
        loc_id = location_ids[i % len(location_ids)] if location_ids else None
        loc_name = next((l["name"] for l in world_json["locations"] if l["id"] == loc_id), "the area") if loc_id else "the area"
        events.append({
            "id": f"evt-gen-{i}",
            "type": tmpl["type"],
            "description": tmpl["template"].format(loc=loc_name),
            "location_id": loc_id,
            "severity": tmpl["severity"],
            "tags": [tmpl["type"]],
        })

    return events
