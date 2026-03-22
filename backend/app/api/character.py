"""Character management API — D&D character creation, dice rolls, leveling."""

import math
import random
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.utils.logger import get_logger

log = get_logger("character")

character_router = APIRouter(tags=["character"])


# ── D&D Reference Data ───────────────────────────────────────────────────


RACES = [
    {"id": "human", "name": "Human", "speed": 30, "ability_bonus": {"all": 1}, "traits": ["Extra feat", "Extra skill"]},
    {"id": "elf", "name": "Elf", "speed": 30, "ability_bonus": {"dex": 2}, "traits": ["Darkvision", "Fey Ancestry", "Trance"]},
    {"id": "dwarf", "name": "Dwarf", "speed": 25, "ability_bonus": {"con": 2}, "traits": ["Darkvision", "Dwarven Resilience", "Stonecunning"]},
    {"id": "halfling", "name": "Halfling", "speed": 25, "ability_bonus": {"dex": 2}, "traits": ["Lucky", "Brave", "Halfling Nimbleness"]},
    {"id": "dragonborn", "name": "Dragonborn", "speed": 30, "ability_bonus": {"str": 2, "cha": 1}, "traits": ["Breath Weapon", "Damage Resistance"]},
    {"id": "gnome", "name": "Gnome", "speed": 25, "ability_bonus": {"int": 2}, "traits": ["Darkvision", "Gnome Cunning"]},
    {"id": "half-elf", "name": "Half-Elf", "speed": 30, "ability_bonus": {"cha": 2}, "traits": ["Darkvision", "Fey Ancestry", "Skill Versatility"]},
    {"id": "half-orc", "name": "Half-Orc", "speed": 30, "ability_bonus": {"str": 2, "con": 1}, "traits": ["Darkvision", "Relentless Endurance", "Savage Attacks"]},
    {"id": "tiefling", "name": "Tiefling", "speed": 30, "ability_bonus": {"cha": 2, "int": 1}, "traits": ["Darkvision", "Hellish Resistance", "Infernal Legacy"]},
]

CLASSES = [
    {"id": "fighter", "name": "Fighter", "hit_die": 10, "primary_ability": "str", "saves": ["str", "con"]},
    {"id": "wizard", "name": "Wizard", "hit_die": 6, "primary_ability": "int", "saves": ["int", "wis"]},
    {"id": "rogue", "name": "Rogue", "hit_die": 8, "primary_ability": "dex", "saves": ["dex", "int"]},
    {"id": "cleric", "name": "Cleric", "hit_die": 8, "primary_ability": "wis", "saves": ["wis", "cha"]},
    {"id": "ranger", "name": "Ranger", "hit_die": 10, "primary_ability": "dex", "saves": ["str", "dex"]},
    {"id": "paladin", "name": "Paladin", "hit_die": 10, "primary_ability": "str", "saves": ["wis", "cha"]},
    {"id": "bard", "name": "Bard", "hit_die": 8, "primary_ability": "cha", "saves": ["dex", "cha"]},
    {"id": "barbarian", "name": "Barbarian", "hit_die": 12, "primary_ability": "str", "saves": ["str", "con"]},
    {"id": "sorcerer", "name": "Sorcerer", "hit_die": 6, "primary_ability": "cha", "saves": ["con", "cha"]},
    {"id": "warlock", "name": "Warlock", "hit_die": 8, "primary_ability": "cha", "saves": ["wis", "cha"]},
    {"id": "druid", "name": "Druid", "hit_die": 8, "primary_ability": "wis", "saves": ["int", "wis"]},
    {"id": "monk", "name": "Monk", "hit_die": 8, "primary_ability": "dex", "saves": ["str", "dex"]},
]

WEAPONS = [
    {"id": "longsword", "name": "Longsword", "damage": "1d8", "type": "martial", "properties": ["versatile (1d10)"]},
    {"id": "shortsword", "name": "Shortsword", "damage": "1d6", "type": "martial", "properties": ["finesse", "light"]},
    {"id": "greataxe", "name": "Greataxe", "damage": "1d12", "type": "martial", "properties": ["heavy", "two-handed"]},
    {"id": "dagger", "name": "Dagger", "damage": "1d4", "type": "simple", "properties": ["finesse", "light", "thrown (20/60)"]},
    {"id": "longbow", "name": "Longbow", "damage": "1d8", "type": "martial", "properties": ["ammunition (150/600)", "heavy", "two-handed"]},
    {"id": "handaxe", "name": "Handaxe", "damage": "1d6", "type": "simple", "properties": ["light", "thrown (20/60)"]},
    {"id": "quarterstaff", "name": "Quarterstaff", "damage": "1d6", "type": "simple", "properties": ["versatile (1d8)"]},
    {"id": "light-crossbow", "name": "Light Crossbow", "damage": "1d8", "type": "simple", "properties": ["ammunition (80/320)", "loading", "two-handed"]},
    {"id": "mace", "name": "Mace", "damage": "1d6", "type": "simple", "properties": []},
    {"id": "rapier", "name": "Rapier", "damage": "1d8", "type": "martial", "properties": ["finesse"]},
]

ARMORS = [
    {"id": "leather", "name": "Leather Armor", "ac": 11, "type": "light", "stealth_disadvantage": False},
    {"id": "studded-leather", "name": "Studded Leather", "ac": 12, "type": "light", "stealth_disadvantage": False},
    {"id": "chain-shirt", "name": "Chain Shirt", "ac": 13, "type": "medium", "stealth_disadvantage": False},
    {"id": "scale-mail", "name": "Scale Mail", "ac": 14, "type": "medium", "stealth_disadvantage": True},
    {"id": "chain-mail", "name": "Chain Mail", "ac": 16, "type": "heavy", "stealth_disadvantage": True},
    {"id": "plate", "name": "Plate Armor", "ac": 18, "type": "heavy", "stealth_disadvantage": True},
    {"id": "shield", "name": "Shield", "ac": 2, "type": "shield", "stealth_disadvantage": False},
]


# ── Dice logic ───────────────────────────────────────────────────────────


def _roll_4d6kh3() -> int:
    """Roll 4d6, keep highest 3."""
    rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
    return sum(rolls[:3])


def _roll_stats() -> list[int]:
    return [_roll_4d6kh3() for _ in range(6)]


def _ability_modifier(score: int) -> int:
    return math.floor((score - 10) / 2)


_DICE_RE = re.compile(r"^(\d+)?d(\d+)([+-]\d+)?$", re.IGNORECASE)


def _roll_notation(notation: str) -> dict:
    """Parse and roll dice notation like '2d6+3'."""
    m = _DICE_RE.match(notation.strip().replace(" ", ""))
    if not m:
        raise ValueError(f"Invalid dice notation: {notation}")
    count = int(m.group(1) or 1)
    sides = int(m.group(2))
    modifier = int(m.group(3) or 0)
    if count < 1 or count > 100 or sides < 1 or sides > 100:
        raise ValueError("Dice count and sides must be between 1 and 100")
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + modifier
    return {"notation": notation.strip(), "rolls": rolls, "modifier": modifier, "total": total}


# ── Character storage (in-memory) ────────────────────────────────────────


_current_character: dict | None = None


# ── Request / Response models ────────────────────────────────────────────


class AbilityScores(BaseModel):
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)


class CharacterCreate(BaseModel):
    name: str
    race_id: str
    class_id: str
    ability_scores: AbilityScores
    proficiencies: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=list)
    backstory: str = ""


class CharacterUpdate(BaseModel):
    name: str | None = None
    ability_scores: AbilityScores | None = None
    proficiencies: list[str] | None = None
    equipment: list[str] | None = None
    backstory: str | None = None


class DiceRollRequest(BaseModel):
    notation: str  # e.g. "2d6+3"


# ── Helpers ──────────────────────────────────────────────────────────────


def _find_race(race_id: str) -> dict:
    for r in RACES:
        if r["id"] == race_id:
            return r
    raise HTTPException(400, f"Unknown race: {race_id}")


def _find_class(class_id: str) -> dict:
    for c in CLASSES:
        if c["id"] == class_id:
            return c
    raise HTTPException(400, f"Unknown class: {class_id}")


def _compute_hp(hit_die: int, con_modifier: int, level: int) -> int:
    """Level 1 = max hit die + CON mod; subsequent levels = avg + CON mod each."""
    base = hit_die + con_modifier
    if level > 1:
        avg_roll = hit_die // 2 + 1
        base += (avg_roll + con_modifier) * (level - 1)
    return max(1, base)


# ── Endpoints ────────────────────────────────────────────────────────────


@character_router.get("/api/dnd/races")
async def list_races():
    return RACES


@character_router.get("/api/dnd/classes")
async def list_classes():
    return CLASSES


@character_router.get("/api/dnd/weapons")
async def list_weapons():
    return WEAPONS


@character_router.get("/api/dnd/armors")
async def list_armors():
    return ARMORS


@character_router.post("/api/character/roll-stats")
async def roll_stats():
    stats = _roll_stats()
    return {"stats": stats, "modifiers": [_ability_modifier(s) for s in stats]}


@character_router.post("/api/dnd/roll")
async def roll_dice(req: DiceRollRequest):
    try:
        result = _roll_notation(req.notation)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return result


@character_router.post("/api/character/create")
async def create_character(req: CharacterCreate):
    global _current_character
    race = _find_race(req.race_id)
    cls = _find_class(req.class_id)

    scores = req.ability_scores.model_dump()
    con_mod = _ability_modifier(scores["constitution"])
    hp = _compute_hp(cls["hit_die"], con_mod, level=1)

    _current_character = {
        "name": req.name,
        "race": race,
        "class": cls,
        "level": 1,
        "ability_scores": scores,
        "modifiers": {k: _ability_modifier(v) for k, v in scores.items()},
        "hp": hp,
        "max_hp": hp,
        "proficiencies": req.proficiencies,
        "equipment": req.equipment,
        "backstory": req.backstory,
        "xp": 0,
    }
    log.info("character_created", name=req.name, race=req.race_id, cls=req.class_id)
    return _current_character


@character_router.get("/api/character")
async def get_character():
    if _current_character is None:
        raise HTTPException(404, "No character created yet")
    return _current_character


@character_router.put("/api/character")
async def update_character(req: CharacterUpdate):
    global _current_character
    if _current_character is None:
        raise HTTPException(404, "No character created yet")
    updates = req.model_dump(exclude_none=True)
    if "ability_scores" in updates:
        scores = updates.pop("ability_scores")
        _current_character["ability_scores"] = scores
        _current_character["modifiers"] = {k: _ability_modifier(v) for k, v in scores.items()}
        con_mod = _ability_modifier(scores["constitution"])
        cls = _current_character["class"]
        _current_character["max_hp"] = _compute_hp(cls["hit_die"], con_mod, _current_character["level"])
        _current_character["hp"] = min(_current_character["hp"], _current_character["max_hp"])
    _current_character.update(updates)
    return _current_character


@character_router.post("/api/character/level-up")
async def level_up():
    global _current_character
    if _current_character is None:
        raise HTTPException(404, "No character created yet")
    _current_character["level"] += 1
    con_mod = _current_character["modifiers"]["constitution"]
    cls = _current_character["class"]
    new_max = _compute_hp(cls["hit_die"], con_mod, _current_character["level"])
    hp_gain = new_max - _current_character["max_hp"]
    _current_character["max_hp"] = new_max
    _current_character["hp"] += hp_gain
    log.info("character_leveled_up", name=_current_character["name"], level=_current_character["level"])
    return {
        "level": _current_character["level"],
        "hp_gain": hp_gain,
        "max_hp": _current_character["max_hp"],
        "character": _current_character,
    }
