"""Tests for app.worldgen — text_to_world pipeline and ontology extraction."""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── text_to_world helpers ────────────────────────────────────────────────

def _sample_extracted():
    """Minimal extraction result from ontology extractor."""
    return {
        "world_name": "Test Realm",
        "world_description": "A small test world.",
        "locations": [
            {"name": "Village Square", "type": "village", "description": "Central hub."},
            {"name": "Dark Forest", "type": "forest", "description": "Spooky trees."},
        ],
        "npcs": [
            {"name": "Aldric", "occupation": "blacksmith", "personality": "gruff"},
            {"name": "Lila", "occupation": "herbalist", "personality": "kind"},
        ],
        "factions": [
            {"name": "Iron Guard", "description": "Protectors.", "goals": ["defend the village"]},
        ],
        "conflicts": [
            {"title": "The Missing Ore", "description": "Iron ore supply dwindling.",
             "type": "main", "tension": "rising"},
        ],
    }


def _sample_generated_npcs():
    """Minimal NPC generation result."""
    return [
        {"name": "Aldric", "occupation": "blacksmith", "personality": "Strong and gruff",
         "backstory": "Grew up forging swords.", "goals": ["craft a masterwork"],
         "mood": "neutral", "age": 42},
        {"name": "Lila", "occupation": "herbalist", "personality": "Kind-hearted",
         "backstory": "Studies rare herbs.", "goals": ["find moonpetal"],
         "mood": "content", "age": 28},
    ]


# ── _slugify ─────────────────────────────────────────────────────────────

def test_slugify():
    from app.worldgen.text_to_world import _slugify
    assert _slugify("Hello World!") == "hello_world"
    assert _slugify("  Spaces  ") == "spaces"
    assert len(_slugify("A" * 100)) <= 50


# ── _build_world_json ────────────────────────────────────────────────────

def test_build_world_json():
    from app.worldgen.text_to_world import _build_world_json
    extracted = _sample_extracted()
    wj = _build_world_json(extracted)

    assert wj["name"] == "Test Realm"
    assert len(wj["locations"]) == 2
    assert all(loc["id"].startswith("loc-") for loc in wj["locations"])
    # Connections should link nearby locations
    assert len(wj["connections"]) >= 1
    assert len(wj["factions"]) == 1
    assert wj["start_location"] == wj["locations"][0]["id"]


def test_build_world_json_empty():
    from app.worldgen.text_to_world import _build_world_json
    wj = _build_world_json({"locations": [], "factions": []})
    assert wj["locations"] == []
    assert wj["start_location"] == ""


# ── _build_npcs_json ─────────────────────────────────────────────────────

def test_build_npcs_json():
    from app.worldgen.text_to_world import _build_npcs_json, _build_world_json
    extracted = _sample_extracted()
    wj = _build_world_json(extracted)
    npcs = _build_npcs_json(_sample_generated_npcs(), wj)

    assert len(npcs) == 2
    assert all(n["id"].startswith("npc-") for n in npcs)
    assert all("location_id" in n for n in npcs)
    # Every NPC should have required fields
    for n in npcs:
        assert "name" in n
        assert "occupation" in n
        assert "goals" in n
        assert "ability_scores" in n
        assert isinstance(n["relationships"], list)


def test_build_npcs_json_assigns_locations():
    from app.worldgen.text_to_world import _build_npcs_json
    world = {"locations": [{"id": "loc-a"}, {"id": "loc-b"}]}
    npcs = _build_npcs_json([{"name": "NPC0"}, {"name": "NPC1"}, {"name": "NPC2"}], world)
    loc_ids = {n["location_id"] for n in npcs}
    # All location IDs should be from the world
    assert loc_ids.issubset({"loc-a", "loc-b"})


# ── _build_scenarios_json ────────────────────────────────────────────────

def test_build_scenarios_json():
    from app.worldgen.text_to_world import _build_scenarios_json
    npcs = [{"id": "npc-aldric", "name": "Aldric"}, {"id": "npc-lila", "name": "Lila"}]
    conflicts = [{"title": "Conflict A", "description": "Something bad.", "type": "main", "tension": "rising"}]
    scenarios = _build_scenarios_json(conflicts, npcs)

    assert len(scenarios) == 1
    sc = scenarios[0]
    assert sc["id"].startswith("sc-")
    assert sc["title"] == "Conflict A"
    assert "phases" in sc
    assert len(sc["phases"]) == 4  # default phases


def test_build_scenarios_name_matching():
    from app.worldgen.text_to_world import _build_scenarios_json
    npcs = [{"id": "npc-aldric", "name": "Aldric"}, {"id": "npc-lila", "name": "Lila"}]
    conflicts = [{"title": "X", "description": "Y", "involved_npcs": ["Aldric"]}]
    scenarios = _build_scenarios_json(conflicts, npcs)
    assert "npc-aldric" in scenarios[0]["involved_npc_ids"]


# ── _build_events_json ───────────────────────────────────────────────────

def test_build_events_json():
    from app.worldgen.text_to_world import _build_events_json
    world = {
        "locations": [
            {"id": "loc-a", "name": "Village"},
            {"id": "loc-b", "name": "Forest"},
        ],
    }
    events = _build_events_json(world, {})
    assert len(events) == 6  # 6 default templates
    assert all(e["id"].startswith("evt-gen-") for e in events)
    assert all("location_id" in e for e in events)


# ── Full pipeline (generate_world_from_text) ─────────────────────────────

@pytest.mark.asyncio
async def test_generate_world_from_text(tmp_path):
    extracted = _sample_extracted()
    generated_npcs = _sample_generated_npcs()

    with patch("app.worldgen.text_to_world.ontology_extractor") as mock_extractor, \
         patch("app.worldgen.text_to_world.npc_generator") as mock_npc_gen, \
         patch("app.worldgen.text_to_world.settings") as mock_settings:

        mock_settings.worlds_dir = tmp_path
        mock_extractor.extract = AsyncMock(return_value=extracted)
        mock_npc_gen.generate = AsyncMock(return_value=generated_npcs)

        from app.worldgen.text_to_world import generate_world_from_text
        result = await generate_world_from_text("A village with a blacksmith and herbalist.")

    assert "error" not in result
    assert result["locations"] == 2
    assert result["npcs"] == 2
    assert result["scenarios"] >= 1
    assert result["events"] >= 1

    # Verify files were written
    world_dir = Path(result["world_dir"])
    assert (world_dir / "world.json").exists()
    assert (world_dir / "npcs.json").exists()
    assert (world_dir / "scenarios.json").exists()
    assert (world_dir / "events.json").exists()

    # Validate JSON structure
    wj = json.loads((world_dir / "world.json").read_text(encoding="utf-8"))
    assert len(wj["locations"]) == 2


@pytest.mark.asyncio
async def test_generate_world_no_locations(tmp_path):
    """When extraction returns no locations, pipeline should return error."""
    with patch("app.worldgen.text_to_world.ontology_extractor") as mock_extractor, \
         patch("app.worldgen.text_to_world.settings") as mock_settings:

        mock_settings.worlds_dir = tmp_path
        mock_extractor.extract = AsyncMock(return_value={"locations": [], "npcs": []})

        from app.worldgen.text_to_world import generate_world_from_text
        result = await generate_world_from_text("Nothing useful.")

    assert "error" in result


@pytest.mark.asyncio
async def test_generate_world_custom_name(tmp_path):
    extracted = _sample_extracted()

    with patch("app.worldgen.text_to_world.ontology_extractor") as mock_ext, \
         patch("app.worldgen.text_to_world.npc_generator") as mock_npc, \
         patch("app.worldgen.text_to_world.settings") as mock_s:

        mock_s.worlds_dir = tmp_path
        mock_ext.extract = AsyncMock(return_value=extracted)
        mock_npc.generate = AsyncMock(return_value=[])

        from app.worldgen.text_to_world import generate_world_from_text
        result = await generate_world_from_text("text", world_name="my_custom_world")

    assert result["world_name"] == "my_custom_world"


# ── OntologyExtractor ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ontology_extractor_success():
    with patch("app.worldgen.ontology.OntologyExtractor.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = _sample_extracted()
        from app.worldgen.ontology import OntologyExtractor
        ext = OntologyExtractor()
        # Patch the instance method
        ext.generate_json = mock_gen
        result = await ext.extract("A village with people.")
    assert "locations" in result
    assert len(result["locations"]) == 2


@pytest.mark.asyncio
async def test_ontology_extractor_error():
    with patch("app.worldgen.ontology.OntologyExtractor.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {"error": "parse_failed"}
        from app.worldgen.ontology import OntologyExtractor
        ext = OntologyExtractor()
        ext.generate_json = mock_gen
        result = await ext.extract("bad input")
    assert result["locations"] == []
    assert result["world_name"] == "unnamed_world"


# ── NPCGenerator ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_npc_generator_dict_response():
    with patch("app.worldgen.ontology.NPCGenerator.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {"npcs": _sample_generated_npcs()}
        from app.worldgen.ontology import NPCGenerator
        gen = NPCGenerator()
        gen.generate_json = mock_gen
        result = await gen.generate([{"name": "Aldric"}], "context")
    assert len(result) == 2
    assert result[0]["name"] == "Aldric"


@pytest.mark.asyncio
async def test_npc_generator_list_response():
    with patch("app.worldgen.ontology.NPCGenerator.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = _sample_generated_npcs()
        from app.worldgen.ontology import NPCGenerator
        gen = NPCGenerator()
        gen.generate_json = mock_gen
        result = await gen.generate([], "context")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_npc_generator_empty():
    with patch("app.worldgen.ontology.NPCGenerator.generate_json", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {"error": "fail"}
        from app.worldgen.ontology import NPCGenerator
        gen = NPCGenerator()
        gen.generate_json = mock_gen
        result = await gen.generate([], "context")
    assert result == []
