"""Faction Agent — factions as collective decision-making entities.

Each faction analyzes its situation (members, rivals, economy) and makes
strategic decisions that translate into directives for member NPCs.
This transforms the world from a collection of individuals into a political system.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("faction_agent")


# ── Rule-based directive generation (no LLM) ─────────────────

_STRATEGY_DIRECTIVES = {
    "expand": {
        "leader": "Recruit new members and extend your faction's influence. Speak publicly about your faction's strengths.",
        "warrior": "Patrol the borders of your territory. Show strength to deter rivals.",
        "spy": "Infiltrate rival gatherings. Learn their plans and weaknesses.",
        "merchant": "Trade aggressively. Establish new trade contacts for the faction.",
        "default": "Spread the word about your faction. Recruit allies.",
    },
    "defend": {
        "leader": "Rally your members. Reinforce defenses and morale.",
        "warrior": "Guard key positions. Be ready for attack at any moment.",
        "spy": "Watch for threats. Report any suspicious activity immediately.",
        "merchant": "Stockpile supplies. Prepare for a siege or shortage.",
        "default": "Stay close to faction territory. Protect what's yours.",
    },
    "diplomacy": {
        "leader": "Meet with rival faction leaders. Seek common ground and alliances.",
        "warrior": "Stand down from aggressive patrols. Show restraint.",
        "spy": "Gather intelligence on potential allies. Find leverage for negotiations.",
        "merchant": "Propose trade deals with rival factions.",
        "default": "Be friendly to members of other factions. Build bridges.",
    },
    "raid": {
        "leader": "Plan the raid. Choose the target and coordinate your warriors.",
        "warrior": "Prepare for combat. Sharpen weapons, don armor.",
        "spy": "Scout the target location. Find weaknesses in their defenses.",
        "merchant": "Secure escape routes. Prepare to fence stolen goods.",
        "default": "Support the raid effort. Gather supplies and stay alert.",
    },
    "trade": {
        "leader": "Negotiate bulk deals. Seek new markets for your faction's goods.",
        "warrior": "Escort merchant caravans. Protect trade routes.",
        "spy": "Learn what other factions need. Find arbitrage opportunities.",
        "merchant": "Trade actively. Buy low, sell high. Grow the treasury.",
        "default": "Focus on your trade. Produce goods for the faction.",
    },
}


class FactionAgent:
    """Manages faction-level strategic decisions."""

    def __init__(self):
        self._strategy_agent = BaseAgent("faction_strategy.j2")

    async def strategize(
        self,
        faction: dict,
        members: list[dict],
        other_factions: list[dict],
        threats: list[str] | None = None,
        opportunities: list[str] | None = None,
    ) -> dict:
        """Make a strategic decision for a faction via LLM.

        Returns: {
            strategy: str,
            directives: {npc_id: str},
            treasury_action: dict,
            diplomatic_action: dict,
        }
        """
        # Build member info with roles
        member_data = []
        for m in members:
            member_data.append({
                "name": m["name"],
                "occupation": m["occupation"],
                "role": m.get("faction_role", "member"),
                "mood": m.get("mood", "neutral"),
            })

        other_data = []
        for f in other_factions:
            other_data.append({
                "name": f["name"],
                "member_count": f.get("member_count", 0),
                "influence": f.get("influence", 0.5),
                "strategy": f.get("strategy", "neutral"),
            })

        result = await self._strategy_agent.generate_json(
            faction_name=faction["name"],
            member_count=len(members),
            treasury=faction.get("treasury", 0),
            influence=faction.get("influence", 0.5),
            morale=faction.get("morale", 0.5),
            current_strategy=faction.get("strategy", "neutral"),
            goals=faction.get("goals", []),
            members=member_data,
            other_factions=other_data,
            threats=threats or [],
            opportunities=opportunities or [],
        )

        if not result or result.get("error"):
            # Fallback: keep current strategy
            return self._fallback_strategy(faction, members)

        # Resolve NPC name directives to IDs
        name_to_id = {m["name"].lower(): m["id"] for m in members}
        directives = {}
        for name, directive in result.get("directives", {}).items():
            npc_id = name_to_id.get(name.lower())
            if npc_id:
                directives[npc_id] = directive

        strategy = result.get("strategy", faction.get("strategy", "neutral"))

        log.info("faction_strategy", faction=faction["name"], strategy=strategy,
                 directives=len(directives))

        return {
            "strategy": strategy,
            "directives": directives,
            "treasury_action": result.get("treasury_action", {"type": "none", "amount": 0}),
            "diplomatic_action": result.get("diplomatic_action", {"action_type": "none"}),
        }

    def _fallback_strategy(self, faction: dict, members: list[dict]) -> dict:
        """Deterministic fallback when LLM is unavailable."""
        strategy = faction.get("strategy", "neutral")
        directives = self.generate_member_directives(strategy, members)
        return {
            "strategy": strategy,
            "directives": directives,
            "treasury_action": {"type": "none", "amount": 0},
            "diplomatic_action": {"action_type": "none"},
        }

    def generate_member_directives(
        self, strategy: str, members: list[dict],
    ) -> dict[str, str]:
        """Convert faction strategy into per-member directives (no LLM).

        Maps member roles to strategy-specific instructions.
        """
        role_directives = _STRATEGY_DIRECTIVES.get(strategy, _STRATEGY_DIRECTIVES["defend"])
        directives = {}
        for m in members:
            role = m.get("faction_role", "member")
            directive = role_directives.get(role, role_directives["default"])
            directives[m["id"]] = directive
        return directives


faction_agent = FactionAgent()
