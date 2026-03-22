"""Scenario lifecycle management — extracted from ticker.py."""

from __future__ import annotations

from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("scenario_mgr")


async def run_scenario_lifecycle(
    gq: GraphQueries,
    world_day: int,
    all_npcs: list[dict],
    locations: list[dict],
    recent_event_descs: list[str],
) -> tuple[dict[str, str], list[dict], list[dict]]:
    """
    Check/advance/create scenarios.
    Returns: (npc_directives, injected_events, scenario_infos)
    """
    from app.agents.scenario_agent import scenario_agent
    from app.config import settings

    scenario_agent.load_scenario_pool(settings.worlds_dir / "medieval_village")
    active_scenarios = await gq.get_active_scenarios()
    scenario_directives: dict[str, str] = {}
    scenario_injected_events: list[dict] = []
    scenario_infos: list[dict] = []

    # Advance existing scenarios
    for sc in active_scenarios:
        try:
            involved_npcs = [n for n in all_npcs if n["id"] in sc.get("involved_npc_ids", [])]
            advance = await scenario_agent.advance_scenario(
                scenario=sc,
                world_day=world_day,
                tick_events=[{"type": e.get("type", ""), "description": e.get("description", "")} for e in []],
                npc_actions=[],
                interactions=[],
                involved_npcs=involved_npcs,
            )

            action = advance.get("action", "stay")
            if action == "advance":
                new_idx = sc.get("current_phase_index", 0) + 1
                phases = sc.get("phases", [])
                if new_idx < len(phases):
                    await gq.update_scenario(sc["id"], {
                        "current_phase_index": new_idx,
                        "tension_level": advance.get("tension_level", sc["tension_level"]),
                    })
                else:
                    await gq.deactivate_scenario(sc["id"])
            elif action == "resolve":
                await gq.deactivate_scenario(sc["id"])
            elif action == "twist":
                await gq.update_scenario(sc["id"], {
                    "tension_level": advance.get("tension_level", sc["tension_level"]),
                })

            for evt in advance.get("events_to_inject", []):
                evt.setdefault("type", "scenario")
                scenario_injected_events.append(evt)

            for npc_id, directive in advance.get("npc_directives", {}).items():
                scenario_directives[npc_id] = directive

            phases = sc.get("phases", [])
            idx = sc.get("current_phase_index", 0)
            phase_name = phases[idx]["name"] if idx < len(phases) else "Finale"
            scenario_infos.append({
                "title": sc["title"],
                "description": sc["description"],
                "phase_name": phase_name,
                "tension_level": advance.get("tension_level", sc.get("tension_level", "low")),
                "narrative_update": advance.get("narrative_update", ""),
            })

        except Exception as e:
            log.error("scenario_advance_failed", title=sc.get("title"), error=str(e))

    # Generate new scenario if no main active
    has_main = any(sc.get("scenario_type") == "main" for sc in active_scenarios)
    if not has_main:
        try:
            new_sc = await scenario_agent.generate_scenario(
                world_day=world_day,
                locations=[dict(l) for l in locations],
                npcs=[dict(n) for n in all_npcs],
                recent_events=recent_event_descs,
                active_scenarios=active_scenarios,
            )
            if new_sc:
                await gq.create_scenario(new_sc)
                phases = new_sc.get("phases", [])
                if phases:
                    for evt in phases[0].get("events_to_inject", []):
                        evt.setdefault("type", "scenario")
                        scenario_injected_events.append(evt)
                    for npc_id, directive in phases[0].get("npc_directives", {}).items():
                        scenario_directives[npc_id] = directive

                scenario_infos.append({
                    "title": new_sc["title"],
                    "description": new_sc["description"],
                    "phase_name": phases[0]["name"] if phases else "Beginning",
                    "tension_level": new_sc.get("tension_level", "low"),
                    "narrative_update": f"A new story begins: {new_sc['title']}",
                })

                # Generate quest from scenario
                try:
                    from app.agents.dm_agent import dm_agent
                    import uuid
                    quest_data = await dm_agent.generate_scenario_quest(
                        scenario_title=new_sc["title"],
                        scenario_description=new_sc["description"],
                        phase_name=phases[0]["name"] if phases else "Beginning",
                        npcs=[{"name": n.get("name", ""), "occupation": n.get("occupation", ""), "mood": n.get("mood", "")} for n in all_npcs[:10]],
                        recent_events=recent_event_descs[-5:],
                    )
                    if quest_data:
                        quest_data["id"] = f"quest-{uuid.uuid4().hex[:8]}"
                        quest_data["scenario_id"] = new_sc["id"]
                        quest_data["status"] = "available"
                        await gq.create_quest(quest_data)
                except Exception as e:
                    log.error("quest_generation_failed", error=str(e))

        except Exception as e:
            log.error("scenario_generation_failed", error=str(e))

    return scenario_directives, scenario_injected_events, scenario_infos
