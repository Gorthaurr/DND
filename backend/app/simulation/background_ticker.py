"""Background Ticker — lightweight world simulation without LLM.

Runs while players are offline. NPCs follow schedule_engine routines,
environment and economy update, but no LLM calls are made.
This is the "async simulation" that makes the world feel alive between sessions.
"""

from __future__ import annotations

import random

from app.graph.queries import GraphQueries
from app.utils.logger import get_logger

log = get_logger("background_ticker")


class BackgroundTicker:
    """Lightweight tick for offline worlds. Zero LLM calls."""

    async def tick(self, gq: GraphQueries, world_day: int | None = None) -> dict:
        """Execute one background tick.

        Returns summary of what happened.
        """
        from app.models.memory import add_memory, init_memory_db
        from app.simulation.environment import environment_engine
        from app.simulation.economy import economy_engine
        from app.simulation.schedule import schedule_engine
        from app.simulation.evolution import evolution_engine

        init_memory_db()

        # Increment day
        if world_day is None:
            world_day = await gq.increment_world_day()

        day_phases = ["dawn", "morning", "afternoon", "evening", "night"]
        phase = day_phases[world_day % len(day_phases)]

        log.info("background_tick_start", day=world_day, world_id=gq.world_id)

        # ── 1. Environment (no LLM) ──
        env_result = await environment_engine.tick(gq, world_day)
        env_events, season, weather = env_result

        # ── 2. Economy (no LLM) ──
        all_npcs = await gq.get_all_npcs()
        economy_events = await economy_engine.tick(gq, world_day, all_npcs)

        # ── 3. NPC decisions via schedule engine (no LLM) ──
        npc_actions = []
        # At night, 60% sleep
        if phase in ("night", "dawn"):
            active_npcs = [n for n in all_npcs if random.random() > 0.4]
        else:
            active_npcs = all_npcs

        for npc in active_npcs:
            sched = schedule_engine.get_activity(npc, phase, world_day)
            action = sched["action"]
            desc = sched["activity_desc"]

            npc_actions.append({
                "npc_id": npc["id"],
                "npc_name": npc["name"],
                "action": action,
            })

            await gq.update_npc(npc["id"], {"current_activity": desc})
            add_memory(npc["id"], f"Day {world_day}: {desc}.", day=world_day, importance=0.3)

            # Simple evolution for routine actions
            event_types = evolution_engine.classify_action_outcome(action, None)
            if event_types:
                await evolution_engine.apply_shifts(gq, npc["id"], npc, event_types)

        # ── 4. Simple same-location interactions (rule-based, no LLM) ──
        interactions = await self._simple_interactions(gq, active_npcs, world_day)

        # ── 5. Memory decay ──
        from app.agents.memory_architect import memory_architect
        for npc in active_npcs[:10]:  # limit to avoid slowdown
            memory_architect.decay_memories(npc["id"], world_day)

        result = {
            "day": world_day,
            "season": season,
            "weather": weather,
            "mode": "background",
            "npc_actions": len(npc_actions),
            "interactions": len(interactions),
            "events": len(env_events) + len(economy_events),
        }

        log.info("background_tick_done", **result)
        return result

    async def _simple_interactions(
        self, gq: GraphQueries, npcs: list[dict], world_day: int,
    ) -> list[dict]:
        """Rule-based NPC interactions without LLM.

        If two NPCs are at the same location with strong feelings,
        apply simple sentiment changes.
        """
        from app.models.memory import add_memory

        locations: dict[str, list[dict]] = {}
        for npc in npcs:
            loc = await gq.get_npc_location(npc["id"])
            if loc:
                locations.setdefault(loc["id"], []).append(npc)

        interactions = []
        for loc_id, npcs_here in locations.items():
            if len(npcs_here) < 2:
                continue
            # Pick up to 3 random pairs
            for _ in range(min(3, len(npcs_here) // 2)):
                pair = random.sample(npcs_here, 2)
                a, b = pair[0], pair[1]

                # Simple interaction: just note they met
                add_memory(a["id"],
                           f"Day {world_day}: Spent time near {b['name']}.",
                           day=world_day, importance=0.2)
                add_memory(b["id"],
                           f"Day {world_day}: Spent time near {a['name']}.",
                           day=world_day, importance=0.2)

                interactions.append({
                    "a": a["name"], "b": b["name"],
                    "type": "proximity",
                })

        return interactions


background_ticker = BackgroundTicker()
