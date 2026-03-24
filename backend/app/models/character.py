"""Player character model with full D&D 5e character sheet."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.dnd.dice import ability_modifier, proficiency_bonus
from app.dnd.classes import get_class, get_spell_slots
from app.dnd.races import get_race
from app.dnd.rules import compute_ac, compute_max_hp


ABILITY_NAMES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]


class EquipmentSlot(BaseModel):
    item_id: str
    item_type: str = "weapon"  # weapon, armor, shield, gear
    equipped: bool = False


class PlayerCharacter(BaseModel):
    """Full D&D 5e player character sheet."""

    id: str = "player-1"
    name: str = "Adventurer"
    race_id: str = "human"
    class_id: str = "fighter"
    level: int = Field(default=1, ge=1, le=20)
    xp: int = 0

    ability_scores: dict[str, int] = Field(
        default_factory=lambda: {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
    )

    max_hp: int = 0
    current_hp: int = 0
    temp_hp: int = 0

    proficiencies: list[str] = Field(default_factory=list)  # skill names
    saving_throw_proficiencies: list[str] = Field(default_factory=list)

    equipment: list[EquipmentSlot] = Field(default_factory=list)
    armor_id: str | None = None
    has_shield: bool = False

    known_spells: list[str] = Field(default_factory=list)
    prepared_spells: list[str] = Field(default_factory=list)
    spell_slots_used: dict[str, int] = Field(default_factory=dict)

    expertise_skills: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)  # active conditions

    # Class resources
    rage_uses: int = 0
    ki_points: int = 0
    sorcery_points: int = 0
    channel_divinity_uses: int = 0
    lay_on_hands_pool: int = 0
    bardic_inspiration_uses: int = 0
    wild_shape_uses: int = 0
    second_wind_used: bool = False
    action_surge_used: bool = False
    indomitable_uses: int = 0

    gold: int = 50
    silver: int = 0
    copper: int = 0

    backstory: str = ""
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""

    @property
    def ability_modifiers(self) -> dict[str, int]:
        return {k: ability_modifier(v) for k, v in self.ability_scores.items()}

    @property
    def prof_bonus(self) -> int:
        return proficiency_bonus(self.level)

    @property
    def ac(self) -> int:
        return compute_ac(self.armor_id, self.ability_scores.get("DEX", 10), self.has_shield)

    @property
    def initiative(self) -> int:
        return ability_modifier(self.ability_scores.get("DEX", 10))

    @property
    def spell_slots(self) -> dict[int, int]:
        return get_spell_slots(self.class_id, self.level)

    def apply_race_bonuses(self) -> None:
        """Apply racial ability score bonuses."""
        race = get_race(self.race_id)
        if race:
            for ability, bonus in race.ability_bonuses.items():
                if ability in self.ability_scores:
                    self.ability_scores[ability] += bonus

    def compute_hp(self) -> None:
        """Compute max HP from class hit die, level, and CON."""
        cls = get_class(self.class_id)
        if cls:
            self.max_hp = compute_max_hp(cls.hit_die, self.level, self.ability_scores.get("CON", 10))
            self.current_hp = self.max_hp

    def to_sheet_dict(self) -> dict:
        """Export as a full character sheet dictionary for API responses."""
        race = get_race(self.race_id)
        cls = get_class(self.class_id)
        return {
            "id": self.id,
            "name": self.name,
            "race": {"id": self.race_id, "name": race.name if race else "Unknown"},
            "class": {"id": self.class_id, "name": cls.name if cls else "Unknown", "hit_die": f"d{cls.hit_die}" if cls else "?"},
            "level": self.level,
            "xp": self.xp,
            "proficiency_bonus": self.prof_bonus,
            "ability_scores": self.ability_scores,
            "ability_modifiers": self.ability_modifiers,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "temp_hp": self.temp_hp,
            "ac": self.ac,
            "initiative": self.initiative,
            "proficiencies": self.proficiencies,
            "saving_throw_proficiencies": self.saving_throw_proficiencies,
            "equipment": [e.model_dump() for e in self.equipment],
            "armor_id": self.armor_id,
            "has_shield": self.has_shield,
            "spell_slots": self.spell_slots,
            "spell_slots_used": self.spell_slots_used,
            "known_spells": self.known_spells,
            "gold": self.gold, "silver": self.silver, "copper": self.copper,
            "backstory": self.backstory,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
        }
