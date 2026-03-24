"""Pure data tables for NPC evolution — trait shifts, fear triggers, goal templates."""

from __future__ import annotations

from enum import StrEnum

from app.models.evolution import parse_big_five, TraitScale


# ── Trigger types that cause evolution ──

class TriggerType(StrEnum):
    NEAR_DEATH = "near_death"
    KILLED_SOMEONE = "killed_someone"
    WITNESSED_DEATH = "witnessed_death"
    BETRAYED = "betrayed"
    SAVED_BY = "saved_by"
    COMBAT_VICTORY = "combat_victory"
    COMBAT_DEFEAT = "combat_defeat"
    ROBBERY_VICTIM = "robbery_victim"
    ROBBERY_SUCCESS = "robbery_success"
    THREAT_RECEIVED = "threat_received"
    HELPED_SOMEONE = "helped_someone"
    RECEIVED_HELP = "received_help"
    SOCIAL_REJECTION = "social_rejection"
    GOAL_PROGRESS = "goal_progress"
    # Nemesis triggers
    NEMESIS_DEFEAT = "nemesis_defeat"        # Lost to nemesis target
    NEMESIS_VICTORY = "nemesis_victory"      # Won against nemesis target
    NEMESIS_ENCOUNTER = "nemesis_encounter"  # Met nemesis in same location


# ── Trait shift deltas per trigger (O, C, E, A, N) ──
# Values are base deltas, multiplied by trigger magnitude (0-1)

TRAIT_SHIFT_TABLE: dict[str, dict[str, float]] = {
    TriggerType.NEAR_DEATH:       {"O": 0.0,  "C": 0.0,   "E": -0.02, "A": 0.0,   "N": 0.05},
    TriggerType.KILLED_SOMEONE:   {"O": 0.0,  "C": 0.0,   "E": 0.0,   "A": -0.03, "N": 0.03},
    TriggerType.WITNESSED_DEATH:  {"O": 0.0,  "C": 0.0,   "E": -0.01, "A": 0.01,  "N": 0.03},
    TriggerType.BETRAYED:         {"O": 0.0,  "C": 0.0,   "E": -0.02, "A": -0.04, "N": 0.03},
    TriggerType.SAVED_BY:         {"O": 0.01, "C": 0.0,   "E": 0.01,  "A": 0.03,  "N": -0.02},
    TriggerType.COMBAT_VICTORY:   {"O": 0.0,  "C": 0.01,  "E": 0.02,  "A": 0.0,   "N": -0.01},
    TriggerType.COMBAT_DEFEAT:    {"O": 0.0,  "C": -0.01, "E": -0.02, "A": 0.0,   "N": 0.03},
    TriggerType.ROBBERY_VICTIM:   {"O": 0.0,  "C": 0.0,   "E": -0.01, "A": -0.02, "N": 0.03},
    TriggerType.ROBBERY_SUCCESS:  {"O": 0.0,  "C": -0.02, "E": 0.01,  "A": -0.03, "N": 0.0},
    TriggerType.THREAT_RECEIVED:  {"O": 0.0,  "C": 0.0,   "E": -0.01, "A": 0.0,   "N": 0.02},
    TriggerType.HELPED_SOMEONE:   {"O": 0.01, "C": 0.01,  "E": 0.01,  "A": 0.02,  "N": -0.01},
    TriggerType.RECEIVED_HELP:    {"O": 0.0,  "C": 0.0,   "E": 0.01,  "A": 0.01,  "N": -0.01},
    TriggerType.SOCIAL_REJECTION: {"O": 0.0,  "C": 0.0,   "E": -0.02, "A": 0.0,   "N": 0.02},
    TriggerType.GOAL_PROGRESS:    {"O": 0.0,  "C": 0.01,  "E": 0.01,  "A": 0.0,   "N": -0.01},
    # Nemesis — anger, obsession, eroding empathy
    TriggerType.NEMESIS_DEFEAT:    {"O": 0.0,  "C": 0.02,  "E": -0.03, "A": -0.05, "N": 0.04},
    TriggerType.NEMESIS_VICTORY:   {"O": 0.0,  "C": 0.02,  "E": 0.03,  "A": 0.0,   "N": -0.03},
    TriggerType.NEMESIS_ENCOUNTER: {"O": 0.0,  "C": 0.01,  "E": 0.0,   "A": -0.02, "N": 0.02},
}


# ── Fear triggers — what events create what fears ──
# Maps (trigger_type, context_keyword) -> fear trigger name

FEAR_TRIGGERS: dict[str, list[dict]] = {
    TriggerType.NEAR_DEATH: [
        {"context_contains": "fire",    "fear": "fire",    "intensity": 0.6},
        {"context_contains": "magic",   "fear": "magic",   "intensity": 0.5},
        {"context_contains": "poison",  "fear": "poison",  "intensity": 0.5},
        {"context_contains": "combat",  "fear": "combat",  "intensity": 0.4},
        {"context_contains": "",        "fear": "death",   "intensity": 0.3},  # fallback
    ],
    TriggerType.BETRAYED: [
        {"context_contains": "", "fear": "betrayal", "intensity": 0.5},
    ],
    TriggerType.WITNESSED_DEATH: [
        {"context_contains": "", "fear": "death", "intensity": 0.3},
    ],
    TriggerType.ROBBERY_VICTIM: [
        {"context_contains": "", "fear": "theft", "intensity": 0.3},
    ],
    TriggerType.NEMESIS_DEFEAT: [
        {"context_contains": "humiliated", "fear": "humiliation", "intensity": 0.6},
        {"context_contains": "",           "fear": "player",      "intensity": 0.4},
    ],
}


# ── Goal templates generated from events ──

GOAL_TEMPLATES: dict[str, list[dict]] = {
    TriggerType.BETRAYED: [
        {"description": "get revenge on {source_npc}", "priority": 0.7},
    ],
    TriggerType.NEAR_DEATH: [
        {"description": "become stronger to survive", "priority": 0.6},
        {"description": "overcome fear of {fear_trigger}", "priority": 0.4},
    ],
    TriggerType.SAVED_BY: [
        {"description": "repay {source_npc} for saving my life", "priority": 0.5},
    ],
    TriggerType.ROBBERY_VICTIM: [
        {"description": "recover stolen gold", "priority": 0.5},
    ],
    TriggerType.COMBAT_VICTORY: [
        {"description": "prove myself in combat again", "priority": 0.3},
    ],
    TriggerType.KILLED_SOMEONE: [
        {"description": "atone for taking a life", "priority": 0.4},
    ],
    TriggerType.NEMESIS_DEFEAT: [
        {"description": "defeat {source_npc} and reclaim my honor", "priority": 0.9},
        {"description": "become stronger than {source_npc}", "priority": 0.7},
    ],
    TriggerType.NEMESIS_VICTORY: [
        {"description": "finish off {source_npc} once and for all", "priority": 0.8},
    ],
}


# ── Archetype profiles as numeric TraitScale ──
# Parsed from the existing big_five strings in archetypes.py

_RAW_PROFILES: dict[str, str] = {
    "guardian":      "O:mid, C:high, E:mid, A:high, N:low",
    "sage":          "O:high, C:high, N:low",
    "trickster":     "O:high, C:low, E:high",
    "zealot":        "C:high, A:low, N:mid",
    "caretaker":     "A:high, E:mid, N:mid",
    "merchant_soul": "O:mid, C:mid, A:low",
    "hermit":        "O:high, E:low, A:low",
    "brawler":       "E:high, A:low, N:high",
    "schemer":       "O:high, C:mid, A:low",
    "idealist":      "O:high, A:high, N:mid",
    "stoic":         "C:high, E:low, N:low",
    "gossip":        "E:high, A:mid, N:mid",
    "coward":        "N:high, A:mid, E:low",
    "rebel":         "O:high, C:low, A:low",
    "romantic":      "O:high, A:high, N:high",
    "sentinel":      "C:high, E:mid, N:mid",
    "hedonist":      "E:high, C:low, N:low",
    "martyr":        "A:high, N:high, C:mid",
    "predator":      "O:mid, A:low, N:low",
    "jester":        "E:high, O:high, A:mid",
    "curator":       "C:high, O:high, E:low",
    "survivalist":   "C:mid, N:high, A:low",
    "empath":        "A:high, O:high, E:mid",
}

ARCHETYPE_PROFILES: dict[str, TraitScale] = {
    k: parse_big_five(v) for k, v in _RAW_PROFILES.items()
}

# Minimum affinity difference to trigger archetype drift
ARCHETYPE_DRIFT_THRESHOLD = 0.15
# Days of consecutive higher affinity needed to actually drift
ARCHETYPE_DRIFT_DAYS_REQUIRED = 5
