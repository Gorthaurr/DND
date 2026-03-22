"""D&D 5e SRD races with ability bonuses, traits, and features."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Race:
    id: str
    name: str
    ability_bonuses: dict[str, int]
    speed: int
    size: str  # "Medium" or "Small"
    darkvision: int = 0  # range in feet, 0 = none
    traits: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    description: str = ""


RACES: dict[str, Race] = {}


def _r(race: Race) -> None:
    RACES[race.id] = race


_r(Race(
    id="human", name="Human",
    ability_bonuses={"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1},
    speed=30, size="Medium", darkvision=0,
    traits=["Extra Language"],
    languages=["Common", "one extra"],
    description="Versatile and ambitious, humans are the most diverse of the races.",
))

_r(Race(
    id="elf", name="High Elf",
    ability_bonuses={"DEX": 2, "INT": 1},
    speed=30, size="Medium", darkvision=60,
    traits=["Darkvision", "Keen Senses (Perception proficiency)", "Fey Ancestry (charm advantage, sleep immunity)", "Trance (4hr rest)", "One wizard cantrip"],
    languages=["Common", "Elvish", "one extra"],
    description="Graceful and long-lived, elves are creatures of magic and refinement.",
))

_r(Race(
    id="dwarf", name="Hill Dwarf",
    ability_bonuses={"CON": 2, "WIS": 1},
    speed=25, size="Medium", darkvision=60,
    traits=["Darkvision", "Dwarven Resilience (poison resistance/advantage)", "Stonecunning", "Dwarven Toughness (+1 HP per level)"],
    languages=["Common", "Dwarvish"],
    description="Bold and hardy, dwarves are known for their skill in warfare and craftsmanship.",
))

_r(Race(
    id="halfling", name="Lightfoot Halfling",
    ability_bonuses={"DEX": 2, "CHA": 1},
    speed=25, size="Small", darkvision=0,
    traits=["Lucky (reroll natural 1s)", "Brave (advantage vs frightened)", "Halfling Nimbleness (move through larger)", "Naturally Stealthy (hide behind larger)"],
    languages=["Common", "Halfling"],
    description="Small and resourceful, halflings survive by their wits and the loyalty of their kin.",
))

_r(Race(
    id="half-orc", name="Half-Orc",
    ability_bonuses={"STR": 2, "CON": 1},
    speed=30, size="Medium", darkvision=60,
    traits=["Darkvision", "Menacing (Intimidation proficiency)", "Relentless Endurance (drop to 1 HP once/long rest)", "Savage Attacks (extra crit die)"],
    languages=["Common", "Orc"],
    description="Powerful and proud, half-orcs combine the best of both their heritages.",
))

_r(Race(
    id="tiefling", name="Tiefling",
    ability_bonuses={"CHA": 2, "INT": 1},
    speed=30, size="Medium", darkvision=60,
    traits=["Darkvision", "Hellish Resistance (fire resistance)", "Infernal Legacy (thaumaturgy; hellish rebuke at 3; darkness at 5)"],
    languages=["Common", "Infernal"],
    description="Bearing the mark of their infernal heritage, tieflings are both feared and fascinating.",
))

_r(Race(
    id="dragonborn", name="Dragonborn",
    ability_bonuses={"STR": 2, "CHA": 1},
    speed=30, size="Medium", darkvision=0,
    traits=["Breath Weapon (2d6 scaling)", "Damage Resistance (by ancestry)"],
    languages=["Common", "Draconic"],
    description="Proud dragon-blooded warriors with a breath weapon tied to their draconic ancestry.",
))

_r(Race(
    id="gnome", name="Rock Gnome",
    ability_bonuses={"INT": 2, "CON": 1},
    speed=25, size="Small", darkvision=60,
    traits=["Darkvision", "Gnome Cunning (advantage on INT/WIS/CHA saves vs magic)", "Artificer's Lore", "Tinker"],
    languages=["Common", "Gnomish"],
    description="Curious inventors and illusionists with an insatiable love of knowledge.",
))

_r(Race(
    id="half-elf", name="Half-Elf",
    ability_bonuses={"CHA": 2},  # +1 to two others chosen at creation
    speed=30, size="Medium", darkvision=60,
    traits=["Darkvision", "Fey Ancestry", "Skill Versatility (2 free skill proficiencies)", "+1 to two ability scores of choice"],
    languages=["Common", "Elvish", "one extra"],
    description="Combining elven grace with human versatility, half-elves walk between two worlds.",
))


def get_race(race_id: str) -> Race | None:
    return RACES.get(race_id)


def list_races() -> list[Race]:
    return list(RACES.values())
