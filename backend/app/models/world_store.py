"""World preset storage — CRUD for custom worlds stored as JSON files."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from app.config import settings
from app.utils.logger import get_logger

log = get_logger("world_store")


class WorldStore:
    """Manages world presets as directories of JSON files under worlds/."""

    def __init__(self, base_dir: Path | None = None):
        self._base = base_dir or settings.worlds_dir
        self._base.mkdir(parents=True, exist_ok=True)

    def list_worlds(self) -> list[dict]:
        """List all available world presets."""
        worlds = []
        for d in sorted(self._base.iterdir()):
            if d.is_dir() and (d / "world.json").exists():
                meta = self._read_world_meta(d)
                meta["id"] = d.name
                worlds.append(meta)
        return worlds

    def get_world(self, world_id: str) -> dict | None:
        """Get full world data (locations, connections, factions, NPCs)."""
        world_dir = self._base / world_id
        if not world_dir.exists():
            return None

        world_data = self._read_json(world_dir / "world.json")
        npcs_data = self._read_json(world_dir / "npcs.json") if (world_dir / "npcs.json").exists() else {"npcs": []}
        events_data = self._read_json(world_dir / "events.json") if (world_dir / "events.json").exists() else {"events": []}

        return {
            "id": world_id,
            "name": world_data.get("name", world_id),
            "description": world_data.get("description", ""),
            "locations": world_data.get("locations", []),
            "connections": world_data.get("connections", []),
            "factions": world_data.get("factions", []),
            "items": world_data.get("items", []),
            "start_location": world_data.get("start_location", ""),
            "npcs": npcs_data.get("npcs", []),
            "events": events_data.get("events", []),
        }

    def create_world(self, data: dict) -> str:
        """Create a new world preset. Returns world_id."""
        world_id = data.get("id") or self._make_id(data.get("name", "world"))
        world_dir = self._base / world_id
        world_dir.mkdir(parents=True, exist_ok=True)

        world_json = {
            "name": data.get("name", "New World"),
            "description": data.get("description", ""),
            "locations": data.get("locations", []),
            "connections": data.get("connections", []),
            "factions": data.get("factions", []),
            "items": data.get("items", []),
            "start_location": data.get("start_location", ""),
        }
        self._write_json(world_dir / "world.json", world_json)

        npcs_json = {"npcs": data.get("npcs", [])}
        self._write_json(world_dir / "npcs.json", npcs_json)

        events_json = {"events": data.get("events", [])}
        self._write_json(world_dir / "events.json", events_json)

        log.info("world_created", id=world_id, name=data.get("name"))
        return world_id

    def update_world(self, world_id: str, data: dict) -> bool:
        """Update world metadata (name, description) and optional lists."""
        world_dir = self._base / world_id
        if not world_dir.exists():
            return False

        world_json = self._read_json(world_dir / "world.json")
        for key in ("name", "description", "locations", "connections", "factions", "items", "start_location"):
            if key in data:
                world_json[key] = data[key]
        self._write_json(world_dir / "world.json", world_json)

        if "npcs" in data:
            self._write_json(world_dir / "npcs.json", {"npcs": data["npcs"]})

        return True

    def delete_world(self, world_id: str) -> bool:
        """Delete a world preset."""
        world_dir = self._base / world_id
        if not world_dir.exists():
            return False
        shutil.rmtree(world_dir)
        log.info("world_deleted", id=world_id)
        return True

    # ── Location CRUD ──

    def add_location(self, world_id: str, location: dict) -> bool:
        world_dir = self._base / world_id
        wj = self._read_json(world_dir / "world.json")
        if not location.get("id"):
            location["id"] = f"loc-{uuid.uuid4().hex[:8]}"
        wj.setdefault("locations", []).append(location)
        self._write_json(world_dir / "world.json", wj)
        return True

    def update_location(self, world_id: str, loc_id: str, data: dict) -> bool:
        world_dir = self._base / world_id
        wj = self._read_json(world_dir / "world.json")
        for loc in wj.get("locations", []):
            if loc["id"] == loc_id:
                loc.update(data)
                self._write_json(world_dir / "world.json", wj)
                return True
        return False

    def delete_location(self, world_id: str, loc_id: str) -> bool:
        world_dir = self._base / world_id
        wj = self._read_json(world_dir / "world.json")
        locs = wj.get("locations", [])
        wj["locations"] = [l for l in locs if l["id"] != loc_id]
        # Also remove connections referencing this location
        conns = wj.get("connections", [])
        wj["connections"] = [c for c in conns if c["from"] != loc_id and c["to"] != loc_id]
        self._write_json(world_dir / "world.json", wj)
        return True

    def add_connection(self, world_id: str, from_id: str, to_id: str, distance: int = 1) -> bool:
        world_dir = self._base / world_id
        wj = self._read_json(world_dir / "world.json")
        wj.setdefault("connections", []).append({"from": from_id, "to": to_id, "distance": distance})
        self._write_json(world_dir / "world.json", wj)
        return True

    # ── NPC CRUD ──

    def add_npc(self, world_id: str, npc: dict) -> bool:
        world_dir = self._base / world_id
        nj = self._read_json(world_dir / "npcs.json") if (world_dir / "npcs.json").exists() else {"npcs": []}
        if not npc.get("id"):
            npc["id"] = f"npc-{uuid.uuid4().hex[:8]}"
        nj["npcs"].append(npc)
        self._write_json(world_dir / "npcs.json", nj)
        return True

    def update_npc(self, world_id: str, npc_id: str, data: dict) -> bool:
        world_dir = self._base / world_id
        nj = self._read_json(world_dir / "npcs.json")
        for npc in nj.get("npcs", []):
            if npc["id"] == npc_id:
                npc.update(data)
                self._write_json(world_dir / "npcs.json", nj)
                return True
        return False

    def delete_npc(self, world_id: str, npc_id: str) -> bool:
        world_dir = self._base / world_id
        nj = self._read_json(world_dir / "npcs.json")
        nj["npcs"] = [n for n in nj.get("npcs", []) if n["id"] != npc_id]
        self._write_json(world_dir / "npcs.json", nj)
        return True

    # ── Helpers ──

    @staticmethod
    def _make_id(name: str) -> str:
        slug = name.lower().replace(" ", "_")[:30]
        return f"{slug}_{uuid.uuid4().hex[:6]}"

    @staticmethod
    def _read_json(path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path: Path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _read_world_meta(self, world_dir: Path) -> dict:
        wj = self._read_json(world_dir / "world.json")
        npcs_count = 0
        if (world_dir / "npcs.json").exists():
            nj = self._read_json(world_dir / "npcs.json")
            npcs_count = len(nj.get("npcs", []))
        return {
            "name": wj.get("name", world_dir.name),
            "description": wj.get("description", ""),
            "locations_count": len(wj.get("locations", [])),
            "npcs_count": npcs_count,
            "factions_count": len(wj.get("factions", [])),
        }


# Singleton
world_store = WorldStore()
