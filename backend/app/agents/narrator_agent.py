"""Narrator Agent — procedural screenwriter that generates story arcs from world tensions.

Instead of template-based scenarios, the Narrator analyzes the actual state of the world
(hostile relationships, faction struggles, economic pressure, unfulfilled goals) and
generates dramatic story arcs that emerge organically from what's happening.
"""

from __future__ import annotations

import uuid

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("narrator")


class NarratorAgent:
    """Analyzes world tensions and generates emergent story arcs."""

    def __init__(self):
        self._tensions_agent = BaseAgent("narrator_tensions.j2")
        self._arc_agent = BaseAgent("narrator_arc.j2")

    async def analyze_tensions(self, gq, world_day: int) -> list[dict]:
        """Scan the world for dramatic tensions that could drive stories.

        Sources:
        - Hostile NPC relationships (sentiment < -0.5)
        - Faction power imbalances
        - Economic shortages
        - Recent deaths/violence
        - Unfulfilled NPC goals
        """
        # Gather data from graph
        all_rels = await gq.get_all_relationships()
        hostile = [r for r in all_rels if r.get("sentiment", 0) < -0.5]

        factions = await gq.get_all_factions()
        faction_data = []
        for f in factions:
            members = await gq.get_faction_members(f["id"])
            faction_data.append({
                **f,
                "member_count": len(members),
                "influence": f.get("influence", 0.5),
                "morale": f.get("morale", 0.5),
                "strategy": f.get("strategy", "neutral"),
            })

        dead_npcs = await gq.get_dead_npcs()
        recent_deaths = [f"{d['name']} died" for d in dead_npcs[-5:]]

        all_npcs = await gq.get_all_npcs()
        unfulfilled = []
        for npc in all_npcs:
            goals = npc.get("goals", [])
            if goals and npc.get("mood") in ("angry", "fearful"):
                unfulfilled.append({
                    "name": npc["name"],
                    "goal": goals[0],
                    "mood": npc["mood"],
                })

        # Check for economic issues (if locations have resources)
        locations = await gq.get_all_locations()
        economic_issues = []
        for loc in locations:
            resources = loc.get("resources")
            if isinstance(resources, dict):
                for res, amount in resources.items():
                    if isinstance(amount, (int, float)) and amount <= 2:
                        economic_issues.append(f"{res} shortage in {loc['name']}")

        active_scenarios = await gq.get_active_scenarios()

        result = await self._tensions_agent.generate_json(
            world_day=world_day,
            hostile_relationships=hostile[:10],
            factions=faction_data,
            recent_deaths=recent_deaths,
            economic_issues=economic_issues[:5],
            unfulfilled_goals=unfulfilled[:10],
            active_arcs=active_scenarios,
        )

        tensions = result.get("tensions", [])
        log.info("tensions_analyzed", count=len(tensions), world_day=world_day)
        return tensions

    async def generate_arc(
        self,
        tension: dict,
        gq,
        world_day: int,
        active_arcs: list[dict],
    ) -> dict | None:
        """Generate a story arc from a specific tension.

        Returns scenario dict ready for gq.create_scenario(), or None if generation fails.
        """
        # Resolve NPC names to full data
        all_npcs = await gq.get_all_npcs()
        npc_name_map = {n["name"].lower(): n for n in all_npcs}
        involved_npcs = []
        involved_npc_ids = []
        for name in tension.get("involved_npc_names", []):
            npc = npc_name_map.get(name.lower())
            if npc:
                involved_npcs.append(npc)
                involved_npc_ids.append(npc["id"])

        result = await self._arc_agent.generate_json(
            tension=tension,
            world_day=world_day,
            involved_npcs=involved_npcs,
            active_arcs=active_arcs,
        )

        if not result or not result.get("title"):
            return None

        # Normalize into scenario format
        phases = []
        for i, phase in enumerate(result.get("phases", [])):
            # Resolve NPC name directives to IDs
            npc_directives = {}
            for npc_name, directive in phase.get("npc_directives", {}).items():
                npc = npc_name_map.get(npc_name.lower())
                if npc:
                    npc_directives[npc["id"]] = directive

            phases.append({
                "phase_id": f"ph-{uuid.uuid4().hex[:8]}",
                "name": phase.get("name", f"Phase {i + 1}"),
                "description": phase.get("description", ""),
                "trigger_day": world_day + phase.get("trigger_day_offset", i * 2),
                "events_to_inject": phase.get("events_to_inject", []),
                "npc_directives": npc_directives,
                "completed": False,
            })

        # Also resolve involved NPC names from arc result
        for name in result.get("involved_npc_names", []):
            npc = npc_name_map.get(name.lower())
            if npc and npc["id"] not in involved_npc_ids:
                involved_npc_ids.append(npc["id"])

        scenario = {
            "id": f"sc-{uuid.uuid4().hex[:8]}",
            "title": result["title"],
            "description": result.get("description", ""),
            "scenario_type": result.get("scenario_type", "main"),
            "start_day": world_day,
            "current_phase_index": 0,
            "tension_level": result.get("tension_level", "rising"),
            "involved_npc_ids": involved_npc_ids,
            "phases": phases,
        }

        log.info("arc_generated", title=scenario["title"], phases=len(phases),
                 npcs=len(involved_npc_ids))
        return scenario

    def should_generate_arc(self, tensions: list[dict], active_arcs: list[dict]) -> dict | None:
        """Decide which tension (if any) should become a new story arc.

        Rules:
        - Don't create if there are already 3+ active arcs
        - Prefer high/critical severity tensions
        - Don't create arcs for tensions already covered by active arcs
        """
        if len(active_arcs) >= 3:
            return None

        # Sort by severity
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_tensions = sorted(
            tensions,
            key=lambda t: severity_order.get(t.get("severity", "low"), 0),
            reverse=True,
        )

        for tension in sorted_tensions:
            if tension.get("severity") in ("high", "critical"):
                return tension
            if tension.get("severity") == "medium" and len(active_arcs) < 2:
                return tension

        return None


narrator_agent = NarratorAgent()
