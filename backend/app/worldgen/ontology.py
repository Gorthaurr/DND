"""Extract world entities from text using LLM."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("ontology")


class OntologyExtractor(BaseAgent):
    """Extracts locations, NPCs, factions, and conflicts from text."""

    def __init__(self):
        super().__init__("worldgen_extract.j2")

    async def extract(self, text: str) -> dict:
        """Extract world entities from a text description.

        Returns dict with keys: locations, npcs, factions, conflicts, world_name, world_description.
        """
        result = await self.generate_json(
            temperature=0.4,
            text=text,
        )
        if result.get("error"):
            log.error("ontology_extraction_failed", error=result)
            return self._empty_result()
        return result

    def _empty_result(self) -> dict:
        return {
            "world_name": "unnamed_world",
            "world_description": "",
            "locations": [],
            "npcs": [],
            "factions": [],
            "conflicts": [],
        }


class NPCGenerator(BaseAgent):
    """Generate full NPC stats from extracted character descriptions."""

    def __init__(self):
        super().__init__("worldgen_npcs.j2")

    async def generate(self, characters: list[dict], world_context: str) -> list[dict]:
        """Generate full D&D NPC definitions from character summaries."""
        result = await self.generate_json(
            temperature=0.6,
            characters=characters,
            world_context=world_context,
        )
        if isinstance(result, dict) and result.get("npcs"):
            return result["npcs"]
        if isinstance(result, list):
            return result
        return []


ontology_extractor = OntologyExtractor()
npc_generator = NPCGenerator()
