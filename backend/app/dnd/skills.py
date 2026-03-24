"""D&D 5e skills — all 18 skills mapped to ability scores."""

from __future__ import annotations

from dataclasses import dataclass
from app.dnd.dice import ability_modifier, proficiency_bonus, roll_d20


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    ability: str  # STR, DEX, CON, INT, WIS, CHA
    description: str


# ── All 18 D&D 5e Skills ──

SKILLS: dict[str, Skill] = {}


def _s(s: Skill) -> None:
    SKILLS[s.id] = s


# STR
_s(Skill("athletics", "Athletics", "STR", "Climbing, jumping, swimming, grappling."))

# DEX
_s(Skill("acrobatics", "Acrobatics", "DEX", "Balance, tumbling, aerial maneuvers."))
_s(Skill("sleight-of-hand", "Sleight of Hand", "DEX", "Pickpocketing, concealing objects, legerdemain."))
_s(Skill("stealth", "Stealth", "DEX", "Hiding, sneaking, avoiding detection."))

# INT
_s(Skill("arcana", "Arcana", "INT", "Magical lore, spells, magical items, planes."))
_s(Skill("history", "History", "INT", "Historical events, legends, past civilizations."))
_s(Skill("investigation", "Investigation", "INT", "Deducing, searching for clues, analyzing evidence."))
_s(Skill("nature", "Nature", "INT", "Flora, fauna, weather, natural cycles."))
_s(Skill("religion", "Religion", "INT", "Deities, rites, prayers, holy symbols, cults."))

# WIS
_s(Skill("animal-handling", "Animal Handling", "WIS", "Calming, training, controlling animals."))
_s(Skill("insight", "Insight", "WIS", "Reading body language, detecting lies, sensing motives."))
_s(Skill("medicine", "Medicine", "WIS", "Stabilizing wounded, diagnosing illness."))
_s(Skill("perception", "Perception", "WIS", "Noticing hidden things, spotting danger, hearing sounds."))
_s(Skill("survival", "Survival", "WIS", "Tracking, foraging, navigating, predicting weather."))

# CHA
_s(Skill("deception", "Deception", "CHA", "Lying, misleading, disguising intentions."))
_s(Skill("intimidation", "Intimidation", "CHA", "Threatening, coercing, frightening."))
_s(Skill("performance", "Performance", "CHA", "Music, acting, storytelling, oratory."))
_s(Skill("persuasion", "Persuasion", "CHA", "Influencing, negotiating, convincing."))


def get_skill(skill_id: str) -> Skill | None:
    return SKILLS.get(skill_id)


def list_skills() -> list[Skill]:
    return list(SKILLS.values())


def skill_check(
    skill_id: str,
    ability_scores: dict[str, int],
    level: int = 1,
    proficient_skills: list[str] | None = None,
    expertise_skills: list[str] | None = None,
    dc: int = 10,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict:
    """
    Make a skill check.

    expertise_skills — double proficiency bonus (Rogue Expertise, Bard, etc.)
    """
    skill = SKILLS.get(skill_id)
    if not skill:
        return {"error": f"Unknown skill: {skill_id}"}

    ability_score = ability_scores.get(skill.ability, 10)
    mod = ability_modifier(ability_score)
    prof = proficiency_bonus(level)

    prof_skills = proficient_skills or []
    exp_skills = expertise_skills or []

    if skill_id in exp_skills:
        total_mod = mod + prof * 2
        prof_label = "expertise"
    elif skill_id in prof_skills:
        total_mod = mod + prof
        prof_label = "proficient"
    else:
        total_mod = mod
        prof_label = "none"

    r = roll_d20(total_mod, advantage, disadvantage)
    success = r.total >= dc

    return {
        "skill": skill.name,
        "ability": skill.ability,
        "roll": r,
        "modifier": total_mod,
        "total": r.total,
        "dc": dc,
        "success": success,
        "proficiency": prof_label,
        "natural": r.natural,
        "description": (
            f"{skill.name} ({skill.ability}): "
            f"d20({r.natural}) + {total_mod} = {r.total} vs DC {dc} "
            f"→ {'SUCCESS' if success else 'FAIL'}"
        ),
    }


def passive_score(
    skill_id: str,
    ability_scores: dict[str, int],
    level: int = 1,
    proficient_skills: list[str] | None = None,
    expertise_skills: list[str] | None = None,
) -> int:
    """Passive score = 10 + all modifiers. Used for Passive Perception, etc."""
    skill = SKILLS.get(skill_id)
    if not skill:
        return 10

    ability_score = ability_scores.get(skill.ability, 10)
    mod = ability_modifier(ability_score)
    prof = proficiency_bonus(level)

    prof_skills = proficient_skills or []
    exp_skills = expertise_skills or []

    if skill_id in exp_skills:
        return 10 + mod + prof * 2
    elif skill_id in prof_skills:
        return 10 + mod + prof
    return 10 + mod
