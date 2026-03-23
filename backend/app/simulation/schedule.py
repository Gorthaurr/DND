"""Personality-driven schedule engine for NPC daily routines.

Replaces random.choice(["work", "rest", "patrol", ...]) with behavior
driven by archetype schedules, Big Five scores, mood, and evolution baselines.
No LLM calls — pure deterministic logic that creates the illusion of routine.
"""

from __future__ import annotations

import random
import re

from app.models.archetypes import get_archetype


def _parse_big_five(personality_str: str) -> dict[str, int]:
    """Parse Big Five string into {O: int, C: int, E: int, A: int, N: int}."""
    scores: dict[str, int] = {}
    for m in re.finditer(r"\b([OCEAN]):\s*(\d+)/10", personality_str):
        scores[m.group(1)] = int(m.group(2))
    name_map = {"Openness": "O", "Conscientiousness": "C", "Extraversion": "E",
                "Agreeableness": "A", "Neuroticism": "N"}
    for name, letter in name_map.items():
        m = re.search(rf"{name}\s+(\d+)/10", personality_str)
        if m and letter not in scores:
            scores[letter] = int(m.group(1))
    return scores


# Phase mapping: normalize 5-phase to 3-slot schedule
_PHASE_TO_SLOT = {
    "dawn": "morning",
    "morning": "morning",
    "afternoon": "afternoon",
    "evening": "evening",
    "night": "evening",
}


class ScheduleEngine:
    """Determine NPC activity based on personality, archetype, and mood."""

    def get_activity(
        self,
        npc: dict,
        phase: str,
        world_day: int,
    ) -> dict:
        """Return {action, location_hint, activity_desc} for a low-priority NPC.

        Uses archetype schedule as base, then applies Big Five + mood + baseline modifiers.
        """
        slot = _PHASE_TO_SLOT.get(phase, "afternoon")
        personality = npc.get("personality", "")
        scores = _parse_big_five(personality)
        mood = npc.get("mood", "neutral")
        occupation = npc.get("occupation", "villager")

        # Evolution baselines (from graph, default 0.0)
        trust_bl = npc.get("trust_baseline", 0.0)
        mood_bl = npc.get("mood_baseline", 0.0)
        aggression_bl = npc.get("aggression_baseline", 0.0)
        confidence_bl = npc.get("confidence_baseline", 0.0)

        # ── 1. Base from archetype schedule ──
        base_action = "work"
        archetype_id = npc.get("archetype")
        if archetype_id:
            arch = get_archetype(archetype_id)
            if arch and arch.default_schedule:
                slot_data = arch.default_schedule.get(slot, {})
                base_action = slot_data.get("activity", "work")

        # ── 2. Big Five modifiers ──
        action = base_action
        E = scores.get("E", 5)
        C = scores.get("C", 5)
        N = scores.get("N", 5)
        O = scores.get("O", 5)
        A = scores.get("A", 5)

        # Introvert override: evening socialize → rest
        if slot == "evening" and action == "socialize" and E <= 3:
            action = "rest"

        # High conscientiousness: morning always work, never skip
        if slot == "morning" and C >= 7:
            action = "work"

        # Low conscientiousness: afternoon work → may slack off
        if slot == "afternoon" and action == "work" and C <= 3:
            if random.random() < 0.4:
                action = "rest" if E <= 4 else "socialize"

        # High neuroticism: evening → may check_locks/worry
        if slot == "evening" and N >= 7:
            if random.random() < 0.3:
                action = "patrol"  # "checking locks" = patrol variant

        # High openness: chance to explore instead of routine
        if O >= 7 and action in ("work", "rest"):
            if random.random() < 0.2:
                action = "investigate"

        # Low agreeableness: help → patrol
        if action == "help" and A <= 3:
            action = "patrol"

        # ── 3. Mood modifiers ──
        if mood == "angry":
            if action in ("socialize", "rest") and random.random() < 0.4:
                action = "patrol" if aggression_bl <= 0.3 else "train"

        if mood == "fearful":
            if action in ("socialize", "patrol") and random.random() < 0.5:
                action = "pray" if random.random() < 0.5 else "rest"

        # ── 4. Evolution baseline modifiers ──
        if trust_bl < -0.3 and slot == "evening" and action == "socialize":
            action = "rest"  # distrustful NPC avoids tavern

        if mood_bl < -0.3 and action == "socialize":
            if random.random() < 0.4:
                action = "rest"  # melancholic NPC withdraws

        if aggression_bl > 0.3 and action in ("rest", "work"):
            if random.random() < 0.25:
                action = "patrol"  # aggressive NPC seeks confrontation

        if confidence_bl < -0.3 and action in ("investigate", "patrol"):
            if random.random() < 0.3:
                action = "work"  # insecure NPC sticks to routine

        # ── 5. Small randomness for variety (10%) ──
        if random.random() < 0.10:
            action = random.choice(["work", "rest", "pray", "forage", "patrol"])

        # ── 6. Build activity description ──
        activity_desc = _ACTION_DESC.get(action, action)
        if action == "work":
            activity_desc = f"working as {occupation}"

        return {
            "action": action,
            "location_hint": _action_location_hint(action, archetype_id, slot),
            "activity_desc": activity_desc,
        }


# ── Action → human-readable description ──
_ACTION_DESC = {
    "work": "working",
    "rest": "resting at home",
    "patrol": "patrolling the area",
    "forage": "foraging in the wilds",
    "pray": "praying quietly",
    "socialize": "talking with neighbors",
    "train": "training combat skills",
    "investigate": "investigating something curious",
    "study": "studying and reading",
    "gather": "gathering herbs and supplies",
    "trade": "trading goods",
    "eat": "eating a meal",
    "advise": "advising visitors",
    "preach": "preaching to passersby",
    "help": "helping someone in need",
}


def _action_location_hint(action: str, archetype_id: str | None, slot: str) -> str | None:
    """Suggest a location for the activity (optional, not enforced)."""
    hints = {
        "pray": "chapel",
        "trade": "market",
        "socialize": "tavern" if slot == "evening" else "square",
        "forage": "forest",
        "gather": "forest",
        "patrol": "square",
    }
    return hints.get(action)


# Module-level singleton
schedule_engine = ScheduleEngine()
