"""Economy Engine — simple supply/demand model for emergent economic behavior.

No LLM required. Tracks resources per location, adjusts prices based on
supply/demand, generates economic events (shortage, boom, inflation).
Creates emergent behavior: blacksmith without iron can't work → gets angry → seeks supplier.
"""

from __future__ import annotations

import json
import random

from app.utils.logger import get_logger

log = get_logger("economy")


# ── Constants ─────────────────────────────────────────────────

BASE_PRICES = {
    "food": 2, "iron": 5, "wood": 3, "herbs": 4,
    "cloth": 3, "stone": 4, "leather": 3, "ale": 2,
}

DAILY_CONSUMPTION = {"food": 0.5}  # per NPC per day at location

PRODUCTION_BY_OCCUPATION = {
    "farmer": {"food": +3},
    "blacksmith": {"iron": -1, "equipment": +1},
    "woodcutter": {"wood": +2},
    "herbalist": {"herbs": +2},
    "hunter": {"food": +1, "leather": +1},
    "brewer": {"ale": +2, "food": -1},
    "miner": {"iron": +2, "stone": +1},
    "weaver": {"cloth": +2},
    "tanner": {"leather": +1},
    "carpenter": {"wood": -1, "furniture": +1},
    "baker": {"food": +2},
    "merchant": {},  # trades, doesn't produce
    "guard": {},
    "priest": {},
}

SHORTAGE_THRESHOLD = 3   # below this = shortage event
SURPLUS_THRESHOLD = 30   # above this = surplus/boom event


class EconomyEngine:
    """Simple supply/demand economy without LLM."""

    async def tick(self, gq, world_day: int, all_npcs: list[dict]) -> list[dict]:
        """Process one economic tick. Returns list of economic events."""
        locations = await gq.get_all_locations()
        events: list[dict] = []

        for loc in locations:
            # Get current resources (stored as JSON string in Neo4j)
            resources = loc.get("resources")
            if isinstance(resources, str):
                try:
                    resources = json.loads(resources)
                except (json.JSONDecodeError, TypeError):
                    resources = {}
            elif not isinstance(resources, dict):
                resources = {}

            # Initialize default resources for new locations
            if not resources:
                resources = {"food": 15, "wood": 10, "iron": 5}

            # Get NPCs at this location
            npcs_here = await gq.get_npcs_at_location(loc["id"])

            # ── Production ──
            for npc in npcs_here:
                occ = npc.get("occupation", "").lower()
                production = PRODUCTION_BY_OCCUPATION.get(occ, {})
                for resource, delta in production.items():
                    if resource in resources:
                        resources[resource] = max(0, resources.get(resource, 0) + delta)
                    elif delta > 0:
                        resources[resource] = delta

            # ── Consumption ──
            npc_count = len(npcs_here)
            for resource, per_npc in DAILY_CONSUMPTION.items():
                consumed = per_npc * npc_count
                resources[resource] = max(0, resources.get(resource, 0) - consumed)

            # ── Price calculation ──
            prices = {}
            for resource, base in BASE_PRICES.items():
                supply = resources.get(resource, 0)
                demand = npc_count * DAILY_CONSUMPTION.get(resource, 0.2)
                if demand > 0:
                    ratio = supply / (demand * 10)  # normalize
                    price_multiplier = max(0.5, min(3.0, 2.0 - ratio))
                else:
                    price_multiplier = 1.0
                prices[resource] = round(base * price_multiplier)

            # ── Economic events ──
            for resource, amount in resources.items():
                if amount <= SHORTAGE_THRESHOLD and resource in BASE_PRICES:
                    events.append({
                        "description": f"Shortage of {resource} in {loc['name']}! Prices rising.",
                        "type": "trade",
                        "severity": "medium" if amount > 0 else "high",
                        "location_id": loc["id"],
                    })
                elif amount >= SURPLUS_THRESHOLD and resource in BASE_PRICES:
                    events.append({
                        "description": f"Surplus of {resource} in {loc['name']} — trade boom!",
                        "type": "trade",
                        "severity": "low",
                        "location_id": loc["id"],
                    })

            # ── Random trade event (5% chance per location) ──
            if random.random() < 0.05:
                events.append({
                    "description": f"A traveling merchant arrives at {loc['name']} with exotic goods.",
                    "type": "trade",
                    "severity": "low",
                    "location_id": loc["id"],
                })

            # ── Update location in graph ──
            await gq.update_location(loc["id"], {
                "resources": json.dumps(resources),
                "prices": json.dumps(prices),
                "prosperity": self._calc_prosperity(resources, npc_count),
            })

        if events:
            log.info("economy_tick", events=len(events), day=world_day)
        return events

    def _calc_prosperity(self, resources: dict, npc_count: int) -> float:
        """Calculate location prosperity (0-1) from resources and population."""
        if npc_count == 0:
            return 0.3
        food = resources.get("food", 0)
        food_per_npc = food / max(1, npc_count)
        # prosperity: 0.2 (starving) to 0.9 (abundant)
        return round(min(0.9, max(0.2, 0.3 + food_per_npc * 0.05)), 2)

    def get_shortages(self, location: dict) -> list[str]:
        """Get resources in shortage at a location."""
        resources = location.get("resources")
        if isinstance(resources, str):
            try:
                resources = json.loads(resources)
            except (json.JSONDecodeError, TypeError):
                return []
        if not isinstance(resources, dict):
            return []
        return [r for r, amount in resources.items()
                if isinstance(amount, (int, float)) and amount <= SHORTAGE_THRESHOLD
                and r in BASE_PRICES]


economy_engine = EconomyEngine()
