"""NPC decision-making and dialogue agent."""

from app.agents.base import BaseAgent
from app.models.npc import NPCContext, NPCDecision
from app.utils.logger import get_logger

log = get_logger("npc_agent")


class NPCAgent:
    """Handles NPC autonomous decisions and dialogue."""

    def __init__(self):
        self._decision_agent = BaseAgent("npc_decision.j2")
        self._dialogue_agent = BaseAgent("npc_dialogue.j2")
        self._interact_agent = BaseAgent("npc_interact.j2")

    async def decide(self, ctx: NPCContext) -> NPCDecision:
        """Have an NPC decide their next action based on context."""
        nearby = []
        for npc in ctx.nearby_npcs:
            entry = {"name": npc.get("name", "unknown"), "occupation": npc.get("occupation", "")}
            # Find relationship info
            for rel in ctx.relationships:
                if rel.npc_id == npc.get("id"):
                    entry["sentiment"] = rel.sentiment
                    entry["reason"] = rel.reason
                    break
            nearby.append(entry)

        result = await self._decision_agent.generate_json(
            name=ctx.name,
            age=ctx.age,
            occupation=ctx.occupation,
            personality=ctx.personality,
            mood=ctx.mood,
            goals=ctx.goals,
            location_name=ctx.location_name,
            location_description=ctx.location_description,
            nearby_npcs=nearby,
            recent_memories=ctx.recent_memories,
            recent_events=ctx.recent_events,
            world_day=ctx.world_day,
            # Archetype fields
            archetype_name=ctx.archetype_name,
            archetype_decision_bias=ctx.archetype_decision_bias,
            archetype_group_role=ctx.archetype_group_role,
            # Phase & scene
            current_phase=ctx.current_phase,
            active_scene_context=ctx.active_scene_context,
            # Equipment & combat
            equipment_summary=ctx.equipment_summary,
            combat_capability=ctx.combat_capability,
            gold=ctx.gold,
        )

        if not result:
            log.warning("npc_decision_empty", npc=ctx.name)
            return NPCDecision(action="rest", reasoning="couldn't decide")

        return NPCDecision(
            action=result.get("action", "rest"),
            target=result.get("target"),
            dialogue=result.get("dialogue"),
            reasoning=result.get("reasoning", ""),
            mood_change=result.get("mood_change", "same"),
        )

    async def dialogue(
        self,
        npc: dict,
        message: str,
        other_name: str,
        relationship: dict | None = None,
        relevant_memories: list[str] | None = None,
        is_player: bool = True,
        reputation: int = 0,
    ) -> dict:
        """Generate NPC dialogue response."""
        # Resolve archetype dialogue style
        archetype_dialogue_style = None
        if npc.get("archetype"):
            from app.models.archetypes import get_archetype
            arch = get_archetype(npc["archetype"])
            if arch:
                archetype_dialogue_style = arch.dialogue_style

        result = await self._dialogue_agent.generate_json(
            name=npc["name"],
            age=npc["age"],
            occupation=npc["occupation"],
            personality=npc["personality"],
            mood=npc["mood"],
            backstory=npc["backstory"],
            other_name=other_name,
            relationship=relationship,
            relevant_memories=relevant_memories or [],
            message=message,
            is_player=is_player,
            reputation=reputation,
            archetype_dialogue_style=archetype_dialogue_style,
        )

        if not result:
            return {
                "dialogue": f"{npc['name']} stares at you blankly.",
                "mood_change": "same",
                "sentiment_change": 0.0,
                "internal_thought": "confused",
            }

        return {
            "dialogue": result.get("dialogue", "..."),
            "mood_change": result.get("mood_change", "same"),
            "sentiment_change": result.get("sentiment_change", 0.0),
            "internal_thought": result.get("internal_thought", ""),
        }

    async def interact(self, npc_a: dict, npc_b: dict, context: dict) -> dict:
        """Simulate NPC-to-NPC interaction with consequential actions."""
        result = await self._interact_agent.generate_json(
            location_name=context.get("location_name", "the village"),
            npc_a=npc_a,
            npc_b=npc_b,
            a_to_b=context.get("a_to_b_relationship"),
            b_to_a=context.get("b_to_a_relationship"),
            scenario_context=context.get("scenario_context"),
        )

        if not result:
            return {
                "summary": f"{npc_a['name']} and {npc_b['name']} ignored each other.",
                "action": "none",
            }

        return {
            "summary": result.get("summary", f"{npc_a['name']} and {npc_b['name']} interacted."),
            "interaction_type": result.get("interaction_type", "conversation"),
            "dialogue_a": result.get("dialogue_a"),
            "dialogue_b": result.get("dialogue_b"),
            "action": result.get("action", "none"),
            "action_initiator": result.get("action_initiator", "none"),
            "action_details": result.get("action_details", {}),
            "a_sentiment_change": result.get("a_sentiment_change", 0.0),
            "b_sentiment_change": result.get("b_sentiment_change", 0.0),
            "a_mood_change": result.get("a_mood_change", "same"),
            "b_mood_change": result.get("b_mood_change", "same"),
        }


npc_agent = NPCAgent()
