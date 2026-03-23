"""Combat orchestrator -- LLM for intent only, dice for math."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.base import BaseAgent
from app.dnd.combat_narrator import CombatResult, resolve_attack
from app.dnd.dice import ability_modifier, roll_d20
from app.utils.logger import get_logger

log = get_logger("combat_agent")


@dataclass
class Combatant:
    """A participant in combat (player or NPC)."""

    id: str
    name: str
    is_player: bool
    level: int
    ability_scores: dict  # {"STR": 16, "DEX": 12, ...}
    current_hp: int
    max_hp: int
    ac: int
    weapon_ids: list[str] = field(default_factory=list)
    armor_id: str | None = None
    has_shield: bool = False
    class_id: str = "commoner"
    initiative: int = 0
    alive: bool = True


@dataclass
class AttackOutcome:
    """Result of a single attack between two combatants."""

    attacker_id: str
    attacker_name: str
    defender_id: str
    defender_name: str
    combat_result: CombatResult
    damage_dealt: int
    defender_hp_after: int
    defender_killed: bool


@dataclass
class EncounterResult:
    """Full result of a multi-round combat encounter."""

    attacks: list[AttackOutcome] = field(default_factory=list)
    combat_log: list[str] = field(default_factory=list)
    player_hp_change: int = 0
    player_killed: bool = False
    npcs_killed: list[str] = field(default_factory=list)
    npcs_damaged: dict[str, int] = field(default_factory=dict)
    all_rolls: list[dict] = field(default_factory=list)
    initiative_order: list[dict] = field(default_factory=list)


class CombatAgent:
    """Orchestrates combat encounters.

    Uses LLM only for interpreting player intent (is this combat? who is targeted?).
    All mechanical resolution uses the D&D rules engine (dice, AC, attack rolls).
    """

    def __init__(self) -> None:
        self._intent_agent = BaseAgent("combat_intent.j2")

    async def parse_combat_intent(
        self,
        player_action: str,
        present_npcs: list[dict],
        player: dict,
    ) -> dict:
        """Use LLM to determine combat intent from player's free-text action.

        Returns dict with keys:
            is_combat (bool), targets (list[{npc_id, npc_name}]),
            player_has_advantage (bool), player_has_disadvantage (bool),
            npcs_join_fight (list[{npc_id, npc_name}]),
            context (str)
        """
        result = await self._intent_agent.generate_json(
            temperature=0.2,
            player_action=player_action,
            present_npcs=present_npcs,
            player=player,
        )
        # Ensure required keys with defaults
        result.setdefault("is_combat", False)
        result.setdefault("targets", [])
        result.setdefault("player_has_advantage", False)
        result.setdefault("player_has_disadvantage", False)
        result.setdefault("npcs_join_fight", [])
        result.setdefault("context", "")
        return result

    @staticmethod
    def build_combatant(data: dict, is_player: bool) -> Combatant:
        """Build a Combatant from a Neo4j node dict or similar data."""
        abilities = data.get("ability_scores", {})
        return Combatant(
            id=data.get("id", data.get("npc_id", "unknown")),
            name=data.get("name", "Unknown"),
            is_player=is_player,
            level=data.get("level", 1),
            ability_scores=abilities,
            current_hp=data.get("current_hp", data.get("max_hp", 10)),
            max_hp=data.get("max_hp", 10),
            ac=data.get("ac", 10),
            weapon_ids=data.get("weapon_ids", []),
            armor_id=data.get("armor_id"),
            has_shield=data.get("has_shield", False),
            class_id=data.get("class_id", "commoner"),
        )

    @staticmethod
    def roll_initiative(combatants: list[Combatant]) -> list[Combatant]:
        """Roll initiative for each combatant: d20 + DEX mod, sort descending."""
        for c in combatants:
            dex_mod = ability_modifier(c.ability_scores.get("DEX", 10))
            init_roll = roll_d20(modifier=dex_mod)
            c.initiative = init_roll.total
        return sorted(combatants, key=lambda x: x.initiative, reverse=True)

    @staticmethod
    def _combatant_as_attack_dict(c: Combatant) -> dict:
        """Convert Combatant to the dict format expected by resolve_attack()."""
        return {
            "name": c.name,
            "level": c.level,
            "ability_scores": c.ability_scores,
            "armor_id": c.armor_id,
            "has_shield": c.has_shield,
            "weapon_ids": c.weapon_ids,
        }

    def _resolve_single_attack(
        self,
        attacker: Combatant,
        defender: Combatant,
    ) -> AttackOutcome:
        """Resolve one attack using combat_narrator.resolve_attack().

        Applies damage to defender and checks for death.
        """
        atk_dict = self._combatant_as_attack_dict(attacker)
        def_dict = self._combatant_as_attack_dict(defender)

        result: CombatResult = resolve_attack(atk_dict, def_dict)

        damage = abs(result.defender_hp_change)
        defender.current_hp = max(0, defender.current_hp + result.defender_hp_change)
        killed = defender.current_hp <= 0
        if killed:
            defender.alive = False

        return AttackOutcome(
            attacker_id=attacker.id,
            attacker_name=attacker.name,
            defender_id=defender.id,
            defender_name=defender.name,
            combat_result=result,
            damage_dealt=damage,
            defender_hp_after=defender.current_hp,
            defender_killed=killed,
        )

    def resolve_combat(
        self,
        player_data: dict,
        target_npcs: list[dict],
        hostile_npcs: list[dict] | None = None,
    ) -> EncounterResult:
        """Resolve a full combat encounter.

        1. Build combatants from data dicts.
        2. Roll initiative for all participants.
        3. Each combatant attacks in initiative order (one round).
           - Player attacks the first target NPC.
           - Each NPC attacks the player.
        4. Apply HP changes, check deaths.
        5. Return structured EncounterResult.
        """
        encounter = EncounterResult()

        # Build player combatant
        player = self.build_combatant(player_data, is_player=True)

        # Build NPC combatants (targets + hostiles)
        npc_combatants: list[Combatant] = []
        for npc_data in target_npcs:
            npc_combatants.append(self.build_combatant(npc_data, is_player=False))
        for npc_data in (hostile_npcs or []):
            npc_combatants.append(self.build_combatant(npc_data, is_player=False))

        # Roll initiative
        all_combatants = [player] + npc_combatants
        ordered = self.roll_initiative(all_combatants)

        encounter.initiative_order = [
            {"id": c.id, "name": c.name, "initiative": c.initiative}
            for c in ordered
        ]

        player_hp_before = player.current_hp

        # One round of combat: each combatant attacks in initiative order
        for combatant in ordered:
            if not combatant.alive:
                continue

            if combatant.is_player:
                # Player attacks the first alive target
                target = next(
                    (n for n in npc_combatants if n.alive),
                    None,
                )
                if target is None:
                    continue
                outcome = self._resolve_single_attack(combatant, target)
            else:
                # NPC attacks the player
                if not player.alive:
                    continue
                outcome = self._resolve_single_attack(combatant, player)

            encounter.attacks.append(outcome)
            encounter.combat_log.append(outcome.combat_result.narrative)
            encounter.all_rolls.extend(outcome.combat_result.rolls)

            if outcome.defender_killed:
                if outcome.defender_id == player.id:
                    encounter.player_killed = True
                else:
                    encounter.npcs_killed.append(outcome.defender_id)

            if outcome.damage_dealt > 0 and outcome.defender_id != player.id:
                encounter.npcs_damaged[outcome.defender_id] = (
                    encounter.npcs_damaged.get(outcome.defender_id, 0)
                    + outcome.damage_dealt
                )

        encounter.player_hp_change = player.current_hp - player_hp_before

        log.info(
            "combat_resolved",
            attacks=len(encounter.attacks),
            player_hp_change=encounter.player_hp_change,
            npcs_killed=encounter.npcs_killed,
        )

        return encounter


combat_agent = CombatAgent()
