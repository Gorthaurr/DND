"""Long-term NPC personality evolution through experience.

NPC baselines shift based on what happens to them:
- Robbed 3 times → trust_baseline drops, they lock doors and suspect strangers.
- Lost a fight → confidence drops, they hesitate and defer.
- Made a friend → mood_baseline rises.

These are small numerical shifts (±0.02–0.10) that accumulate over time
and feed into schedule engine, speech patterns, and LLM prompts.
"""

from __future__ import annotations

from app.utils.logger import get_logger

log = get_logger("evolution")


# ── Event → baseline deltas ──────────────────────────────────
# Keys match action names and outcomes from ticker._apply_decision
# and _resolve_npc_combat.

ACTION_SHIFTS: dict[str, dict[str, float]] = {
    # Combat outcomes
    "killed_enemy":     {"confidence": +0.06, "aggression": +0.03, "mood": -0.02},
    "killed_in_defense": {"confidence": +0.04, "aggression": +0.01},
    "lost_fight":       {"confidence": -0.08, "aggression": -0.03, "mood": -0.04},
    "survived_fight":   {"confidence": +0.02, "aggression": +0.02},
    "witnessed_murder": {"mood": -0.06, "trust": -0.04, "confidence": -0.03},

    # Theft / betrayal
    "was_robbed":       {"trust": -0.06, "mood": -0.03, "aggression": +0.02},
    "caught_thief":     {"trust": -0.03, "confidence": +0.02},
    "robbed_someone":   {"trust": -0.02, "aggression": +0.02},

    # Social
    "was_threatened":   {"trust": -0.04, "mood": -0.02, "confidence": -0.02},
    "threatened_someone": {"aggression": +0.02, "confidence": +0.01},
    "was_helped":       {"trust": +0.03, "mood": +0.02},
    "helped_someone":   {"mood": +0.02},
    "made_trade":       {"trust": +0.01, "mood": +0.01},
    "had_conversation": {"mood": +0.01},

    # Work / routine
    "earned_gold":      {"mood": +0.01, "confidence": +0.01},
    "rested":           {"mood": +0.01},
    "prayed":           {"mood": +0.01, "confidence": +0.01},
}


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


class EvolutionEngine:
    """Evaluate NPC actions/outcomes and compute baseline shifts."""

    def compute_shifts(self, event_type: str) -> dict[str, float]:
        """Return baseline deltas for a given event type.

        Returns empty dict if event_type is unknown.
        """
        return ACTION_SHIFTS.get(event_type, {})

    def classify_action_outcome(
        self,
        action: str,
        target: str | None,
        combat_result: dict | None = None,
    ) -> list[str]:
        """Classify an NPC's action + outcome into event types for shift computation.

        Returns a list of event type strings (may be empty).
        """
        events: list[str] = []

        if action == "fight":
            if combat_result:
                if combat_result.get("attacker_won"):
                    if combat_result.get("defender_died"):
                        events.append("killed_enemy")
                    else:
                        events.append("survived_fight")
                elif combat_result.get("attacker_died"):
                    pass  # dead NPC doesn't evolve
                else:
                    events.append("survived_fight")
            else:
                events.append("survived_fight")

        elif action == "rob":
            events.append("robbed_someone")

        elif action == "threaten":
            events.append("threatened_someone")

        elif action == "help":
            events.append("helped_someone")

        elif action == "trade":
            events.append("made_trade")

        elif action == "talk" or action == "gossip":
            events.append("had_conversation")

        elif action in ("work", "craft"):
            events.append("earned_gold")

        elif action == "rest":
            events.append("rested")

        elif action == "pray":
            events.append("prayed")

        return events

    async def apply_shifts(
        self,
        gq,  # GraphQueries
        npc_id: str,
        npc: dict,
        event_types: list[str],
    ) -> dict[str, float]:
        """Apply baseline shifts to NPC in the graph. Returns final baselines."""
        if not event_types:
            return {}

        # Accumulate deltas
        deltas: dict[str, float] = {}
        for et in event_types:
            for key, val in self.compute_shifts(et).items():
                deltas[key] = deltas.get(key, 0.0) + val

        if not deltas:
            return {}

        # Compute new baselines
        baseline_map = {
            "trust": "trust_baseline",
            "mood": "mood_baseline",
            "aggression": "aggression_baseline",
            "confidence": "confidence_baseline",
        }

        updates: dict[str, float] = {}
        for short_key, graph_key in baseline_map.items():
            if short_key in deltas:
                old = npc.get(graph_key, 0.0) or 0.0
                new = _clamp(old + deltas[short_key])
                if abs(new - old) > 0.001:
                    updates[graph_key] = round(new, 3)

        if updates:
            await gq.update_npc(npc_id, updates)
            log.debug("baseline_shifted", npc=npc.get("name", npc_id),
                       shifts={k: round(v, 3) for k, v in deltas.items()})

        return updates


# Module-level singleton
evolution_engine = EvolutionEngine()
