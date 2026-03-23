"""Tests for character management API endpoints."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.character import (
    character_router,
    _roll_4d6kh3,
    _roll_stats,
    _ability_modifier,
    _roll_notation,
    _find_race,
    _find_class,
    _compute_hp,
    RACES,
    CLASSES,
    WEAPONS,
    ARMORS,
    _current_character,
)

# Build test app
_app = FastAPI()
_app.include_router(character_router)
client = TestClient(_app)


class TestDiceHelpers:
    def test_roll_4d6kh3_range(self):
        for _ in range(50):
            val = _roll_4d6kh3()
            assert 3 <= val <= 18

    def test_roll_stats_length(self):
        stats = _roll_stats()
        assert len(stats) == 6
        assert all(3 <= s <= 18 for s in stats)

    def test_ability_modifier_10(self):
        assert _ability_modifier(10) == 0

    def test_ability_modifier_16(self):
        assert _ability_modifier(16) == 3

    def test_ability_modifier_8(self):
        assert _ability_modifier(8) == -1

    def test_roll_notation_2d6(self):
        result = _roll_notation("2d6+3")
        assert result["modifier"] == 3
        assert len(result["rolls"]) == 2

    def test_roll_notation_invalid(self):
        with pytest.raises(ValueError):
            _roll_notation("xd6")

    def test_compute_hp_level1(self):
        hp = _compute_hp(hit_die=10, con_modifier=2, level=1)
        assert hp == 12  # 10 + 2

    def test_compute_hp_level3(self):
        hp = _compute_hp(hit_die=10, con_modifier=2, level=3)
        # level 1: 10+2=12, level 2-3: 2*(6+2)=16, total=28
        assert hp == 28


class TestReferenceDataEndpoints:
    def test_get_races(self):
        resp = client.get("/api/dnd/races")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == len(RACES)
        assert data[0]["id"] == "human"

    def test_get_classes(self):
        resp = client.get("/api/dnd/classes")
        assert resp.status_code == 200
        assert len(resp.json()) == len(CLASSES)

    def test_get_weapons(self):
        resp = client.get("/api/dnd/weapons")
        assert resp.status_code == 200
        assert len(resp.json()) == len(WEAPONS)

    def test_get_armors(self):
        resp = client.get("/api/dnd/armors")
        assert resp.status_code == 200
        assert len(resp.json()) == len(ARMORS)


class TestDiceEndpoint:
    def test_roll_dice(self):
        resp = client.post("/api/dnd/roll", json={"notation": "1d20"})
        assert resp.status_code == 200
        data = resp.json()
        assert 1 <= data["total"] <= 20

    def test_roll_dice_invalid(self):
        resp = client.post("/api/dnd/roll", json={"notation": "bad"})
        assert resp.status_code == 400

    def test_roll_stats(self):
        resp = client.post("/api/character/roll-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["stats"]) == 6
        assert len(data["modifiers"]) == 6


class TestCharacterCRUD:
    def test_create_character(self):
        resp = client.post("/api/character/create", json={
            "name": "Thorin",
            "race_id": "dwarf",
            "class_id": "fighter",
            "ability_scores": {
                "strength": 16, "dexterity": 12, "constitution": 14,
                "intelligence": 10, "wisdom": 13, "charisma": 8,
            },
            "proficiencies": ["athletics"],
            "equipment": ["longsword"],
            "backstory": "A sturdy dwarf."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Thorin"
        assert data["level"] == 1
        assert data["hp"] > 0

    def test_get_character(self):
        # Create first
        client.post("/api/character/create", json={
            "name": "Test",
            "race_id": "human",
            "class_id": "wizard",
            "ability_scores": {
                "strength": 8, "dexterity": 14, "constitution": 12,
                "intelligence": 16, "wisdom": 10, "charisma": 13,
            },
        })
        resp = client.get("/api/character")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"

    def test_update_character(self):
        client.post("/api/character/create", json={
            "name": "Updateable",
            "race_id": "elf",
            "class_id": "rogue",
            "ability_scores": {
                "strength": 10, "dexterity": 16, "constitution": 12,
                "intelligence": 14, "wisdom": 10, "charisma": 10,
            },
        })
        resp = client.put("/api/character", json={"name": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_level_up(self):
        client.post("/api/character/create", json={
            "name": "Leveler",
            "race_id": "human",
            "class_id": "fighter",
            "ability_scores": {
                "strength": 14, "dexterity": 12, "constitution": 14,
                "intelligence": 10, "wisdom": 10, "charisma": 10,
            },
        })
        resp = client.post("/api/character/level-up")
        assert resp.status_code == 200
        data = resp.json()
        assert data["level"] == 2
        assert data["hp_gain"] > 0

    def test_create_bad_race(self):
        resp = client.post("/api/character/create", json={
            "name": "Bad",
            "race_id": "alien",
            "class_id": "fighter",
            "ability_scores": {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10,
            },
        })
        assert resp.status_code == 400


class TestFindHelpers:
    def test_find_race_valid(self):
        r = _find_race("elf")
        assert r["name"] == "Elf"

    def test_find_class_valid(self):
        c = _find_class("wizard")
        assert c["name"] == "Wizard"
