"""Environment Engine — seasons, weather, natural disasters, ecological chains.

Deterministic model (no LLM). The world is no longer static:
- Seasons cycle every 30 days
- Weather affects production, travel, and mood
- Storms can cause floods, droughts kill crops
- Ecological chains: overuse → depletion → cascading effects
"""

from __future__ import annotations

import json
import random

from app.utils.logger import get_logger

log = get_logger("environment")


# ── Season & Weather ──────────────────────────────────────────

SEASON_LENGTH = 30  # days per season

SEASONS = ["spring", "summer", "autumn", "winter"]

WEATHER_WEIGHTS: dict[str, dict[str, float]] = {
    "spring": {"clear": 0.4, "rain": 0.35, "storm": 0.1, "fog": 0.15},
    "summer": {"clear": 0.5, "rain": 0.15, "drought": 0.2, "storm": 0.1, "fog": 0.05},
    "autumn": {"clear": 0.3, "rain": 0.35, "storm": 0.2, "fog": 0.15},
    "winter": {"clear": 0.2, "snow": 0.45, "storm": 0.2, "fog": 0.15},
}

# Weather effects on the world
WEATHER_EFFECTS = {
    "storm": {"travel_penalty": 0.5, "mood_effect": "fearful", "flood_chance": 0.15},
    "drought": {"food_penalty": 0.5, "fire_chance": 0.05},
    "snow": {"travel_penalty": 0.3, "food_penalty": 0.2},
    "rain": {"travel_penalty": 0.1, "food_bonus": 0.1},
    "fog": {"travel_penalty": 0.2},
    "clear": {},
}

# Location conditions and their recovery time
CONDITION_RECOVERY = {
    "flooded": 3,   # days to recover to normal
    "burned": 5,
    "frozen": 2,    # thaws faster
}


class EnvironmentEngine:
    """Manages seasons, weather, and environmental effects."""

    def get_season(self, world_day: int) -> str:
        """Get current season based on world day."""
        season_index = (world_day // SEASON_LENGTH) % len(SEASONS)
        return SEASONS[season_index]

    def get_weather(self, season: str) -> str:
        """Generate weather for the day (weighted random by season)."""
        weights = WEATHER_WEIGHTS.get(season, WEATHER_WEIGHTS["spring"])
        options = list(weights.keys())
        probs = list(weights.values())
        return random.choices(options, weights=probs, k=1)[0]

    async def tick(self, gq, world_day: int) -> list[dict]:
        """Process one environmental tick. Returns list of env events."""
        season = self.get_season(world_day)
        weather = self.get_weather(season)
        events: list[dict] = []

        # Update world state
        await gq.update_world_state({"season": season, "weather": weather})

        # Season change event
        if world_day % SEASON_LENGTH == 1 and world_day > 1:
            events.append({
                "description": f"The season has changed to {season}. The land transforms.",
                "type": "natural",
                "severity": "low",
            })

        # Weather effects
        effects = WEATHER_EFFECTS.get(weather, {})
        locations = await gq.get_all_locations()

        for loc in locations:
            loc_condition = loc.get("condition", "normal")
            loc_type = loc.get("type", "").lower()
            updates: dict = {}

            # ── Recovery: damaged locations heal over time ──
            if loc_condition != "normal":
                recovery_days = CONDITION_RECOVERY.get(loc_condition, 3)
                condition_day = loc.get("condition_since_day", 0)
                if world_day - condition_day >= recovery_days:
                    updates["condition"] = "normal"
                    updates["accessibility"] = 1.0
                    events.append({
                        "description": f"{loc['name']} has recovered from {loc_condition} conditions.",
                        "type": "natural",
                        "severity": "low",
                        "location_id": loc["id"],
                    })

            # ── Storm effects ──
            if weather == "storm":
                flood_chance = effects.get("flood_chance", 0)
                if loc_type in ("riverside", "coastal", "port", "bridge") and random.random() < flood_chance:
                    updates["condition"] = "flooded"
                    updates["accessibility"] = 0.2
                    updates["condition_since_day"] = world_day
                    events.append({
                        "description": f"Flooding at {loc['name']}! The area is nearly impassable.",
                        "type": "natural",
                        "severity": "high",
                        "location_id": loc["id"],
                    })

            # ── Drought effects ──
            if weather == "drought":
                if loc_type in ("farm", "field", "garden"):
                    events.append({
                        "description": f"Drought withers crops at {loc['name']}. Food production halved.",
                        "type": "natural",
                        "severity": "medium",
                        "location_id": loc["id"],
                    })
                if random.random() < effects.get("fire_chance", 0):
                    if loc_type in ("forest", "field", "farm"):
                        updates["condition"] = "burned"
                        updates["accessibility"] = 0.5
                        updates["condition_since_day"] = world_day
                        events.append({
                            "description": f"Wildfire breaks out near {loc['name']}!",
                            "type": "natural",
                            "severity": "high",
                            "location_id": loc["id"],
                        })

            # ── Snow/frozen effects ──
            if weather == "snow" and season == "winter":
                if loc_type in ("mountain", "pass", "bridge") and random.random() < 0.2:
                    updates["condition"] = "frozen"
                    updates["accessibility"] = 0.3
                    updates["condition_since_day"] = world_day
                    events.append({
                        "description": f"{loc['name']} is frozen and difficult to traverse.",
                        "type": "natural",
                        "severity": "medium",
                        "location_id": loc["id"],
                    })

            # ── Travel accessibility based on weather ──
            travel_penalty = effects.get("travel_penalty", 0)
            if travel_penalty and loc_condition == "normal":
                new_access = round(1.0 - travel_penalty, 2)
                if new_access != loc.get("accessibility", 1.0):
                    updates["accessibility"] = new_access

            # Apply updates
            if updates:
                await gq.update_location(loc["id"], updates)

        # General weather event
        if weather in ("storm", "drought", "snow"):
            events.append({
                "description": f"The day brings {weather}. Travel is harder, spirits are low.",
                "type": "natural",
                "severity": "low",
            })

        log.info("environment_tick", day=world_day, season=season, weather=weather,
                 events=len(events))
        return events, season, weather


environment_engine = EnvironmentEngine()
