"""Scenario Director — generates and manages story arcs."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from app.agents.base import BaseAgent
from app.utils.logger import get_logger

log = get_logger("scenario_agent")


class ScenarioAgent:
    """Creates multi-day story arcs and advances them each tick."""

    def __init__(self):
        self._generate_agent = BaseAgent("scenario_generate.j2")
        self._advance_agent = BaseAgent("scenario_advance.j2")
        self._scenario_templates: list[dict] = []

    def load_scenario_pool(self, world_dir: Path) -> None:
        path = world_dir / "scenarios.json"
        if path.exists():
            self._scenario_templates = json.loads(path.read_text(encoding="utf-8"))
            log.info("scenario_pool_loaded", count=len(self._scenario_templates))

    async def generate_scenario(
        self,
        world_day: int,
        locations: list[dict],
        npcs: list[dict],
        recent_events: list[str],
        active_scenarios: list[dict],
    ) -> dict | None:
        """Generate a new story arc for the world."""
        # Build NPC summaries with tension info
        npc_summaries = []
        for npc in npcs:
            entry = {
                "name": npc.get("name", "unknown"),
                "occupation": npc.get("occupation", ""),
                "mood": npc.get("mood", "neutral"),
                "tensions": npc.get("tensions", ""),
            }
            npc_summaries.append(entry)

        result = await self._generate_agent.generate_json(
            world_day=world_day,
            locations=locations,
            npcs=npc_summaries,
            recent_events=recent_events,
            active_scenarios=active_scenarios,
            scenario_templates=self._scenario_templates,
        )

        if not result or "title" not in result:
            log.warning("scenario_generation_failed")
            return None

        # Clean unicode from title
        if result.get("title"):
            result["title"] = result["title"].encode("ascii", "ignore").decode("ascii").strip()

        # Normalize the scenario
        scenario = {
            "id": f"sc-{uuid.uuid4().hex[:8]}",
            "title": result["title"],
            "description": result.get("description", ""),
            "scenario_type": result.get("scenario_type", "main"),
            "start_day": world_day,
            "current_phase_index": 0,
            "tension_level": result.get("tension_level", "low"),
            "involved_npc_ids": result.get("involved_npc_ids", []),
            "phases": [],
        }

        # Normalize phases
        for i, phase in enumerate(result.get("phases", [])):
            scenario["phases"].append({
                "phase_id": phase.get("phase_id", f"phase-{i}"),
                "name": phase.get("name", f"Phase {i}"),
                "description": phase.get("description", ""),
                "trigger_day": phase.get("trigger_day", i),
                "events_to_inject": phase.get("events_to_inject", []),
                "npc_directives": phase.get("npc_directives", {}),
                "completed": False,
            })

        log.info("scenario_generated", title=scenario["title"], phases=len(scenario["phases"]))
        return scenario

    async def advance_scenario(
        self,
        scenario: dict,
        world_day: int,
        tick_events: list[dict],
        npc_actions: list[dict],
        interactions: list[dict],
        involved_npcs: list[dict],
    ) -> dict:
        """Decide how to advance an active scenario."""
        phases = scenario.get("phases", [])
        idx = scenario.get("current_phase_index", 0)
        current_phase = phases[idx] if idx < len(phases) else {"phase_id": "end", "name": "Finale", "description": "The story concludes."}
        next_phase = phases[idx + 1] if idx + 1 < len(phases) else None

        result = await self._advance_agent.generate_json(
            scenario=scenario,
            world_day=world_day,
            current_phase=current_phase,
            next_phase=next_phase,
            tick_events=tick_events,
            npc_actions=npc_actions,
            interactions=interactions,
            involved_npcs=involved_npcs,
        )

        if not result:
            return {"action": "stay", "events_to_inject": [], "npc_directives": {}}

        action = result.get("action", "stay")
        log.info(
            "scenario_advanced",
            title=scenario["title"],
            action=action,
            tension=result.get("tension_level", scenario["tension_level"]),
        )

        return {
            "action": action,
            "tension_level": result.get("tension_level", scenario.get("tension_level", "low")),
            "narrative_update": result.get("narrative_update", ""),
            "events_to_inject": result.get("events_to_inject", []),
            "npc_directives": result.get("npc_directives", {}),
        }


scenario_agent = ScenarioAgent()
