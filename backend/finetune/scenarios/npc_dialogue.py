"""Scenario generator for NPC dialogue responses."""

from __future__ import annotations

from app.models.archetypes import ARCHETYPES, ArchetypeID
from finetune.scenarios.base import BaseScenarioGenerator
from finetune.scenarios.pools import PLAYER_MESSAGES

_LANGS = ["en", "en", "en", "en", "ru", "de", "fr", "es"]
_MESSAGE_CATEGORIES = list(PLAYER_MESSAGES.keys())
_REPUTATION_RANGE = [-50, -30, -10, 0, 10, 30, 50]


class NPCDialogueGenerator(BaseScenarioGenerator):
    """Generates NPC dialogue scenarios across message types, archetypes, sentiments."""

    def agent_type(self) -> str:
        return "npc_dialogue"

    def _generate_one(self) -> dict:
        npc = self._random_npc()
        category = self.rng.choice(_MESSAGE_CATEGORIES)
        message = self.rng.choice(PLAYER_MESSAGES[category])
        rel = self._random_relationship()
        reputation = self.rng.choice(_REPUTATION_RANGE)
        lang = self.rng.choice(_LANGS)

        # Archetype metadata
        arch_id = npc["archetype"]
        try:
            arch = ARCHETYPES[ArchetypeID(arch_id)]
        except (ValueError, KeyError):
            arch = None

        # Other speaker
        other = self._random_npc()
        is_player = self.rng.random() > 0.3

        # Recent chat (0-4 lines)
        recent_chat = []
        if self.rng.random() > 0.4:
            chat_count = self.rng.randint(1, 4)
            speakers = [npc["name"], other["name"] if not is_player else "Player"]
            for _ in range(chat_count):
                speaker = self.rng.choice(speakers)
                line = self.rng.choice(PLAYER_MESSAGES[self.rng.choice(_MESSAGE_CATEGORIES)])
                recent_chat.append(f"{speaker}: {line}")

        context = {
            "name": npc["name"],
            "age": npc["age"],
            "occupation": npc["occupation"],
            "personality": npc["personality"],
            "mood": npc["mood"],
            "backstory": npc["backstory"],
            "other_name": "Player" if is_player else other["name"],
            "relationship": rel,
            "relevant_memories": self._random_memories(self.rng.randint(1, 3)),
            "message": message,
            "is_player": is_player,
            "reputation": reputation,
            "archetype_dialogue_style": arch.dialogue_style if arch else None,
            "recent_chat": recent_chat,
            "lang": lang,
        }

        return {
            "context": context,
            "rendered_prompt": self._render_prompt("npc_dialogue.j2", **context),
            "agent_type": self.agent_type(),
            "metadata": {
                "archetype": arch_id,
                "message_category": category,
                "sentiment": rel["sentiment"],
                "reputation": reputation,
                "is_player": is_player,
                "lang": lang,
            },
        }
