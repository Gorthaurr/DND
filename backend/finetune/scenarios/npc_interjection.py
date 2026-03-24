"""Scenario generator for NPC interjection decisions (90% false, 10% true)."""

from __future__ import annotations

from app.models.archetypes import ARCHETYPES, ArchetypeID
from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import PLAYER_MESSAGES

_LANGS = ["en", "en", "en", "en", "ru", "de", "fr"]
_REPUTATION_RANGE = [-50, -20, 0, 20, 50]

# Messages that might warrant interjection (name-mentions, threats)
_INTERJECTION_TRIGGERS = [
    "I'm going to kill {target}!",
    "{observer}, what do you think about this?",
    "Hey {observer}, come here!",
    "Someone told me {observer} is a thief.",
    "{target} is attacking me! Help!",
]


class NPCInterjectionGenerator(BaseScenarioGenerator):
    """Generates interjection scenarios — 90% should_interject=false, 10% true."""

    def agent_type(self) -> str:
        return "npc_interjection"

    def _generate_one(self) -> dict:
        observer = self._random_npc()
        target = self._random_npc()
        loc = self._random_location()
        lang = self.rng.choice(_LANGS)

        # 90% normal messages (expect false), 10% trigger messages (expect true)
        should_trigger = self.rng.random() < 0.10
        if should_trigger:
            template = self.rng.choice(_INTERJECTION_TRIGGERS)
            player_message = template.format(
                target=target["name"], observer=observer["name"],
            )
        else:
            category = self.rng.choice(list(PLAYER_MESSAGES.keys()))
            player_message = self.rng.choice(PLAYER_MESSAGES[category])

        target_reply = self.rng.choice(
            PLAYER_MESSAGES[self.rng.choice(list(PLAYER_MESSAGES.keys()))],
        )

        # Archetype metadata
        arch_id = observer["archetype"]
        try:
            arch = ARCHETYPES[ArchetypeID(arch_id)]
        except (ValueError, KeyError):
            arch = None

        rel_to_target = self._random_relationship()

        context = {
            "name": observer["name"],
            "age": observer["age"],
            "occupation": observer["occupation"],
            "personality": observer["personality"],
            "mood": observer["mood"],
            "archetype_dialogue_style": arch.dialogue_style if arch else None,
            "location_name": loc["name"],
            "target_npc_name": target["name"],
            "target_npc_occupation": target["occupation"],
            "player_message": player_message,
            "target_reply": target_reply,
            "player_reputation": self.rng.choice(_REPUTATION_RANGE),
            "relationship_to_target": f"sentiment {rel_to_target['sentiment']} ({rel_to_target['reason']})",
            "relevant_memories": self._random_memories(self.rng.randint(0, 3)),
            "recent_chat": [],
            "lang": lang,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("npc_interjection.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "archetype": arch_id,
                "should_trigger": should_trigger,
                "lang": lang,
            },
        }
