"""Big Five personality → concrete speech instructions for LLM.

Instead of passing abstract "O:7/10" to the LLM, we convert Big Five scores
into specific, actionable speech rules that the LLM follows much better.
"""

from __future__ import annotations

import re

# ── Trait thresholds ──────────────────────────────────────────
HIGH = 7  # score >= 7 activates "high" rules
LOW = 4   # score <= 3 activates "low" rules

# ── Speech rules per trait level ──────────────────────────────
# Each entry: (trait_letter, threshold_direction, list_of_rules)

TRAIT_RULES: list[tuple[str, str, int, list[str]]] = [
    # Openness
    ("O", ">=", HIGH, [
        "Use rich vocabulary with metaphors and analogies.",
        "Go on brief philosophical tangents or 'what-if' musings.",
        "Reference stories, legends, or creative comparisons.",
    ]),
    ("O", "<=", LOW, [
        "Use plain, concrete language — no metaphors.",
        "Stick to practical matters; dismiss abstract ideas.",
        "Prefer facts and direct statements over speculation.",
    ]),

    # Conscientiousness
    ("C", ">=", HIGH, [
        "Speak in structured, complete sentences.",
        "Give specific details — numbers, names, times.",
        "No filler words; be precise and deliberate.",
    ]),
    ("C", "<=", LOW, [
        "Ramble and change topic mid-sentence.",
        "Use filler words: 'uh', 'well', 'I guess', 'sort of'.",
        "Make vague promises; lose track of details.",
    ]),

    # Extraversion
    ("E", ">=", HIGH, [
        "Be loud and emphatic — use exclamations.",
        "Ask questions about the other person.",
        "Share anecdotes and laugh easily.",
    ]),
    ("E", "<=", LOW, [
        "Give short, measured responses (1-2 sentences max).",
        "Leave long pauses; be uncomfortable with small talk.",
        "Avoid volunteering information unprompted.",
    ]),

    # Agreeableness
    ("A", ">=", HIGH, [
        "Soften bad news; avoid direct conflict.",
        "Use excessive politeness: 'if you don't mind', 'perhaps'.",
        "Agree readily; compliment often.",
    ]),
    ("A", "<=", LOW, [
        "Be blunt — no sugarcoating, no apologies.",
        "Give backhanded compliments at best.",
        "Refuse directly: 'No.' — not 'I'm sorry but...'",
    ]),

    # Neuroticism
    ("N", ">=", HIGH, [
        "Interrupt yourself with worries and worst-case scenarios.",
        "Jump between topics when anxious.",
        "Have emotional outbursts — sudden anger, tears, or panic.",
    ]),
    ("N", "<=", LOW, [
        "Stay calm and measured, even under pressure.",
        "Rarely show strong emotion in speech.",
        "Respond to bad news with pragmatic acceptance.",
    ]),
]

# ── Mood modifiers (layered on top of personality) ────────────
MOOD_SPEECH: dict[str, list[str]] = {
    "angry": [
        "Clench your words — short, sharp sentences.",
        "Mention what made you angry; don't hide it.",
    ],
    "fearful": [
        "Stutter or trail off mid-sentence.",
        "Glance around nervously; mention feeling unsafe.",
    ],
    "excited": [
        "Speak quickly, with enthusiasm.",
        "Use superlatives: 'amazing', 'incredible', 'the best'.",
    ],
    "content": [
        "Speak warmly and at a relaxed pace.",
    ],
}


def _parse_big_five(personality_str: str) -> dict[str, int]:
    """Parse 'Big Five: O:7/10, C:3/10, ...' or 'Openness 7/10, ...' into {O: 7, ...}."""
    scores: dict[str, int] = {}

    # Pattern 1: "O:7/10" or "O: 7/10"
    for match in re.finditer(r"\b([OCEAN]):\s*(\d+)/10", personality_str):
        scores[match.group(1)] = int(match.group(2))

    # Pattern 2: "Openness 7/10"
    name_map = {"Openness": "O", "Conscientiousness": "C", "Extraversion": "E",
                "Agreeableness": "A", "Neuroticism": "N"}
    for name, letter in name_map.items():
        m = re.search(rf"{name}\s+(\d+)/10", personality_str)
        if m and letter not in scores:
            scores[letter] = int(m.group(1))

    return scores


def build_speech_instructions(personality_str: str, mood: str = "neutral") -> str:
    """Convert Big Five scores + mood into 3-6 concrete speech instructions.

    Returns a newline-separated string ready to inject into LLM prompts.
    """
    scores = _parse_big_five(personality_str)
    if not scores:
        return ""

    rules: list[str] = []

    for trait, op, threshold, trait_rules in TRAIT_RULES:
        val = scores.get(trait)
        if val is None:
            continue
        if op == ">=" and val >= threshold:
            rules.extend(trait_rules)
        elif op == "<=" and val <= threshold:
            rules.extend(trait_rules)

    # Add mood-specific rules
    mood_rules = MOOD_SPEECH.get(mood, [])
    rules.extend(mood_rules)

    # Cap at 6 rules to keep prompt focused
    if len(rules) > 6:
        rules = rules[:6]

    if not rules:
        return ""

    return "\n".join(f"- {r}" for r in rules)
