"""Abstract base class for fine-tuning scenario generators."""

from __future__ import annotations

import hashlib
import random
from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from finetune.config import PROMPTS_DIR
from finetune.scenarios.pools import (
    ARCHETYPE_ABILITY_BIAS,
    ARCHETYPE_IDS,
    BACKSTORIES,
    CASTER_SPELLS,
    CLASS_ARMOR,
    CLASS_EQUIPMENT,
    CLASS_NUM_SKILLS,
    CLASS_SKILL_POOL,
    DAMAGE_TYPES,
    EVENT_TEMPLATES,
    FEARS,
    LOCATIONS,
    MEMORY_TEMPLATES,
    MOODS,
    NAMES,
    NPC_ACTIONS,
    NPC_CLASS_WEIGHTS,
    OCCUPATIONS,
    PERSONALITY_STRINGS,
    RELATIONSHIP_REASONS,
    RELATIONSHIP_SENTIMENTS,
    WORLD_SITUATIONS,
)


class BaseScenarioGenerator(ABC):
    """Base class providing shared helpers for all scenario generators.

    Each subclass generates scenarios for a specific agent type
    (npc_decision, npc_dialogue, combat_intent, etc.).
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self._generated_hashes: set[str] = set()
        self._jinja_env: Environment | None = None

    # ── Abstract interface ──────────────────────────────────────────────

    @abstractmethod
    def agent_type(self) -> str:
        """Return the agent type string (e.g. 'npc_decision')."""
        ...

    @abstractmethod
    def _generate_one(self) -> dict:
        """Generate a single scenario dict with prompt context and expected output."""
        ...

    # ── Batch generation with dedup ────────────────────────────────────

    def generate_batch(self, count: int) -> list[dict]:
        """Generate *count* unique scenarios, deduplicating by content hash."""
        results: list[dict] = []
        max_attempts = count * 3
        attempts = 0

        while len(results) < count and attempts < max_attempts:
            attempts += 1
            scenario = self._generate_one()
            h = self._hash_scenario(scenario)
            if h not in self._generated_hashes:
                self._generated_hashes.add(h)
                results.append(scenario)

        return results

    # ── Random NPC generator ───────────────────────────────────────────

    def _random_npc(self, **overrides) -> dict:
        """Generate a random NPC dict with all fields used by templates.

        Produces realistic combinations:
        - Ability scores biased by archetype
        - Equipment matching the class
        - Spells only for caster classes
        - HP scaled by level and class hit die
        """
        name = overrides.get("name", self.rng.choice(NAMES))
        age = overrides.get("age", self.rng.randint(18, 70))
        occupation = overrides.get("occupation", self.rng.choice(OCCUPATIONS))
        archetype = overrides.get("archetype", self.rng.choice(ARCHETYPE_IDS))
        personality = overrides.get("personality", self.rng.choice(PERSONALITY_STRINGS))
        mood = overrides.get("mood", self.rng.choice(MOODS))
        level = overrides.get("level", self._weighted_level())

        # Pick class with weighting
        class_id = overrides.get("class_id", self._weighted_class())

        # Ability scores biased by archetype and class
        ability_scores = overrides.get(
            "ability_scores",
            self._random_ability_scores(archetype=archetype, class_id=class_id),
        )

        # Equipment matching class
        equipment_ids = overrides.get("equipment_ids", self._class_equipment(class_id))

        # Armor
        armor_id = CLASS_ARMOR.get(class_id)

        # HP from class hit die
        hit_die = self._hit_die_for_class(class_id)
        con_mod = (ability_scores.get("CON", 10) - 10) // 2
        max_hp = overrides.get(
            "max_hp",
            hit_die + (level - 1) * (hit_die // 2 + 1 + con_mod) + con_mod,
        )
        max_hp = max(1, max_hp)
        current_hp = overrides.get("current_hp", max(1, self.rng.randint(max_hp // 2, max_hp)))

        # AC from armor + DEX
        dex_mod = (ability_scores.get("DEX", 10) - 10) // 2
        ac = overrides.get("ac", self._compute_ac(armor_id, dex_mod, class_id))

        # Gold
        gold = overrides.get("gold", self.rng.randint(0, 50 + level * 10))

        # Fears (1-3 random)
        num_fears = self.rng.randint(1, 3)
        fears = overrides.get(
            "fears",
            [{"trigger": f, "intensity": round(self.rng.uniform(0.3, 1.0), 2)}
             for f in self.rng.sample(FEARS, min(num_fears, len(FEARS)))],
        )

        # Goals
        goal_templates = [
            "Protect the village from threats",
            "Earn enough gold to retire",
            "Find a cure for a sick loved one",
            "Uncover the truth about the disappearances",
            "Gain the trust of the villagers",
            "Avenge a past wrong",
            "Secure a trade deal with the traveling merchants",
            "Master a new skill or craft",
            "Win the heart of someone special",
            "Explore the abandoned mine",
        ]
        num_active = self.rng.randint(1, 3)
        active_goals = overrides.get("active_goals", [
            {"description": g, "priority": round(self.rng.uniform(0.3, 1.0), 2),
             "progress": round(self.rng.uniform(0.0, 0.8), 2)}
            for g in self.rng.sample(goal_templates, min(num_active, len(goal_templates)))
        ])
        completed_goals = overrides.get("completed_goals", (
            [self.rng.choice(goal_templates)] if self.rng.random() > 0.6 else []
        ))

        # Skills
        skill_pool = CLASS_SKILL_POOL.get(class_id, ["perception", "athletics"])
        num_skills = CLASS_NUM_SKILLS.get(class_id, 2)
        proficient_skills = overrides.get(
            "proficient_skills",
            self.rng.sample(skill_pool, min(num_skills, len(skill_pool))),
        )

        # Spells (only for caster classes)
        known_spells = overrides.get("known_spells", self._class_spells(class_id, level))

        # Backstory
        location_name = self.rng.choice(LOCATIONS)["name"].lower()
        backstory = overrides.get("backstory", self.rng.choice(BACKSTORIES).format(
            location=location_name,
            skill=occupation,
            occupation=occupation,
        ))

        # Goals as string list (used by some templates)
        goals = overrides.get("goals", [g["description"] for g in active_goals])

        return {
            "name": name,
            "age": age,
            "occupation": occupation,
            "personality": personality,
            "mood": mood,
            "backstory": backstory,
            "goals": goals,
            "archetype": archetype,
            "level": level,
            "class_id": class_id,
            "ability_scores": ability_scores,
            "equipment_ids": equipment_ids,
            "armor_id": armor_id,
            "max_hp": max_hp,
            "current_hp": current_hp,
            "ac": ac,
            "gold": gold,
            "fears": fears,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "proficient_skills": proficient_skills,
            "known_spells": known_spells,
        }

    # ── Random location ────────────────────────────────────────────────

    def _random_location(self) -> dict:
        """Pick a random location from the pool."""
        return dict(self.rng.choice(LOCATIONS))

    # ── Random relationship ────────────────────────────────────────────

    def _random_relationship(self) -> dict:
        """Generate a random sentiment + reason pair."""
        return {
            "sentiment": self.rng.choice(RELATIONSHIP_SENTIMENTS),
            "reason": self.rng.choice(RELATIONSHIP_REASONS),
        }

    # ── Random memories ────────────────────────────────────────────────

    def _random_memories(self, count: int = 5) -> list[str]:
        """Generate plausible memory strings."""
        memories: list[str] = []
        base_day = self.rng.randint(1, 100)
        for i in range(count):
            template = self.rng.choice(MEMORY_TEMPLATES)
            memory = template.format(
                day=base_day + i,
                name=self.rng.choice(NAMES),
                location=self.rng.choice(LOCATIONS)["name"].lower(),
            )
            memories.append(memory)
        return memories

    # ── Random events ──────────────────────────────────────────────────

    def _random_events(self, count: int = 3) -> list[str]:
        """Generate plausible recent event strings."""
        return self.rng.sample(EVENT_TEMPLATES, min(count, len(EVENT_TEMPLATES)))

    # ── Ability scores ─────────────────────────────────────────────────

    def _random_ability_scores(
        self,
        archetype: str | None = None,
        class_id: str | None = None,
    ) -> dict[str, int]:
        """Generate D&D ability scores (4d6-drop-lowest style, range 8-18).

        Biases the primary ability higher for the archetype and class.
        """
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        scores: dict[str, int] = {}

        # Determine which abilities get a boost
        boosted: set[str] = set()
        if archetype and archetype in ARCHETYPE_ABILITY_BIAS:
            boosted.add(ARCHETYPE_ABILITY_BIAS[archetype])

        # Class primary ability boost
        class_primary_map = {
            "barbarian": "STR", "bard": "CHA", "cleric": "WIS",
            "druid": "WIS", "fighter": "STR", "monk": "DEX",
            "paladin": "STR", "ranger": "DEX", "rogue": "DEX",
            "sorcerer": "CHA", "warlock": "CHA", "wizard": "INT",
        }
        if class_id and class_id in class_primary_map:
            boosted.add(class_primary_map[class_id])

        for ability in abilities:
            if ability in boosted:
                # Boosted: roll 4d6 drop lowest, min 12
                rolls = sorted([self.rng.randint(1, 6) for _ in range(4)])
                score = max(12, sum(rolls[1:]))
            else:
                # Standard: 4d6 drop lowest, clamp 8-18
                rolls = sorted([self.rng.randint(1, 6) for _ in range(4)])
                score = max(8, min(18, sum(rolls[1:])))
            scores[ability] = score

        return scores

    # ── Prompt rendering ───────────────────────────────────────────────

    def _render_prompt(self, template_name: str, **context) -> str:
        """Render a Jinja2 template from the agents/prompts/ directory."""
        if self._jinja_env is None:
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(PROMPTS_DIR)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        template = self._jinja_env.get_template(template_name)
        return template.render(**context)

    # ── Private helpers ────────────────────────────────────────────────

    def _hash_scenario(self, scenario: dict) -> str:
        """Produce a deterministic hash for deduplication."""
        raw = str(sorted(scenario.items()))
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()

    def _weighted_level(self) -> int:
        """NPC levels weighted toward lower values (most villagers are low-level)."""
        weights = [
            (1, 30), (2, 25), (3, 15), (4, 10), (5, 7),
            (6, 4), (7, 3), (8, 2), (9, 2), (10, 2),
        ]
        levels, w = zip(*weights)
        return self.rng.choices(levels, weights=w, k=1)[0]

    def _weighted_class(self) -> str:
        """Pick a class weighted by NPC-appropriateness."""
        classes = list(NPC_CLASS_WEIGHTS.keys())
        weights = list(NPC_CLASS_WEIGHTS.values())
        return self.rng.choices(classes, weights=weights, k=1)[0]

    def _class_equipment(self, class_id: str) -> list[str]:
        """Return 1-3 equipment IDs appropriate for the class."""
        pool = CLASS_EQUIPMENT.get(class_id, ["dagger"])
        count = min(self.rng.randint(1, 3), len(pool))
        return self.rng.sample(pool, count)

    def _class_spells(self, class_id: str, level: int) -> list[str]:
        """Return known spells appropriate for the class and level."""
        spells_data = CASTER_SPELLS.get(class_id)
        if not spells_data:
            return []

        known: list[str] = []

        # Cantrips (always available for casters)
        cantrips = spells_data.get("cantrips", [])
        if cantrips:
            num_cantrips = min(self.rng.randint(2, 3), len(cantrips))
            known.extend(self.rng.sample(cantrips, num_cantrips))

        # Level 1 spells
        if level >= 1:
            pool = spells_data.get("level_1", [])
            if pool:
                num = min(self.rng.randint(2, 4), len(pool))
                known.extend(self.rng.sample(pool, num))

        # Level 2 spells
        if level >= 3:
            pool = spells_data.get("level_2", [])
            if pool:
                num = min(self.rng.randint(1, 3), len(pool))
                known.extend(self.rng.sample(pool, num))

        # Level 3 spells
        if level >= 5:
            pool = spells_data.get("level_3", [])
            if pool:
                num = min(self.rng.randint(1, 2), len(pool))
                known.extend(self.rng.sample(pool, num))

        return known

    @staticmethod
    def _hit_die_for_class(class_id: str) -> int:
        """Return hit die size for a class."""
        hit_dice = {
            "barbarian": 12, "bard": 8, "cleric": 8, "druid": 8,
            "fighter": 10, "monk": 8, "paladin": 10, "ranger": 10,
            "rogue": 8, "sorcerer": 6, "warlock": 8, "wizard": 6,
        }
        return hit_dice.get(class_id, 8)

    @staticmethod
    def _compute_ac(armor_id: str | None, dex_mod: int, class_id: str) -> int:
        """Compute AC from armor and DEX modifier."""
        if armor_id is None:
            # Unarmored: 10 + DEX (barbarian/monk have special rules)
            if class_id == "barbarian":
                return 10 + dex_mod + 2  # simplified unarmored defense
            if class_id == "monk":
                return 10 + dex_mod + 2  # simplified unarmored defense
            return 10 + dex_mod

        # Lookup armor base AC and type
        armor_data = {
            "padded": (11, "light"), "leather": (11, "light"),
            "studded-leather": (12, "light"),
            "hide": (12, "medium"), "chain-shirt": (13, "medium"),
            "scale-mail": (14, "medium"), "breastplate": (14, "medium"),
            "half-plate": (15, "medium"),
            "ring-mail": (14, "heavy"), "chain-mail": (16, "heavy"),
            "splint": (17, "heavy"), "plate": (18, "heavy"),
            "shield": (2, "shield"),
        }
        if armor_id not in armor_data:
            return 10 + dex_mod

        base, armor_type = armor_data[armor_id]
        if armor_type == "light":
            return base + dex_mod
        if armor_type == "medium":
            return base + min(dex_mod, 2)
        if armor_type == "heavy":
            return base
        # shield handled separately
        return base + dex_mod
