"""Combat orchestrator -- LLM for intent only, dice for math."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agents.base import BaseAgent
from app.dnd.combat_narrator import CombatResult, resolve_attack
from app.dnd.dice import ability_modifier, roll_d20
from app.dnd.spell_engine import cast_spell, can_cast_spell, SpellTarget, SpellResult
from app.dnd.conditions import (
    can_take_actions, can_move, has_attack_advantage,
    has_attack_disadvantage, auto_fail_save,
)
from app.dnd.death_saves import DeathTracker, DeathState, make_death_save, take_damage_while_dying
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
    # Spell casting
    known_spells: list[str] = field(default_factory=list)
    spell_slots_used: dict[str, int] = field(default_factory=dict)
    saving_throw_proficiencies: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    # Death saves
    death_tracker: DeathTracker = field(default_factory=DeathTracker)


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
            known_spells=data.get("known_spells", []),
            spell_slots_used=data.get("spell_slots_used", {}),
            saving_throw_proficiencies=data.get("saving_throw_proficiencies", []),
            conditions=data.get("conditions", []),
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

        Accounts for conditions:
        - Attacker conditions: disadvantage from blinded/frightened/poisoned/prone/restrained
        - Defender conditions: advantage from paralyzed/stunned/unconscious/restrained/blinded
        - Paralyzed/unconscious: melee hits within 5ft are auto-crits
        """
        atk_dict = self._combatant_as_attack_dict(attacker)
        def_dict = self._combatant_as_attack_dict(defender)

        # Determine advantage/disadvantage from conditions
        adv = has_attack_advantage(defender.conditions)   # defender gives advantage to attackers
        disadv = has_attack_disadvantage(attacker.conditions)  # attacker has disadvantage

        # If both, they cancel out (D&D 5e rule)
        if adv and disadv:
            adv = False
            disadv = False

        result: CombatResult = resolve_attack(atk_dict, def_dict, advantage=adv, disadvantage=disadv)

        damage = abs(result.defender_hp_change)

        # Don't apply HP changes here — let _apply_damage_to_combatant handle death saves
        return AttackOutcome(
            attacker_id=attacker.id,
            attacker_name=attacker.name,
            defender_id=defender.id,
            defender_name=defender.name,
            combat_result=result,
            damage_dealt=damage,
            defender_hp_after=max(0, defender.current_hp - damage),
            defender_killed=False,  # determined later by _apply_damage_to_combatant
        )

    def _can_act(self, combatant: Combatant) -> tuple[bool, str]:
        """Check if a combatant can take actions this turn, considering conditions and death."""
        if not combatant.alive:
            return False, f"{combatant.name} is dead"

        if combatant.death_tracker.state == DeathState.DYING:
            return False, f"{combatant.name} is dying (making death saves)"

        if combatant.death_tracker.state == DeathState.STABLE:
            return False, f"{combatant.name} is unconscious (stable at 0 HP)"

        if not can_take_actions(combatant.conditions):
            blocked_by = [c for c in combatant.conditions if c in (
                "incapacitated", "paralyzed", "petrified", "stunned", "unconscious",
            )]
            return False, f"{combatant.name} cannot act ({', '.join(blocked_by)})"

        return True, ""

    def _handle_death_saves(self, combatant: Combatant) -> dict | None:
        """Handle death saving throws for a dying combatant. Returns roll info or None."""
        if combatant.death_tracker.state != DeathState.DYING:
            return None

        result = make_death_save(combatant.death_tracker)

        if result.outcome == DeathState.DEAD:
            combatant.alive = False

        if result.outcome == DeathState.ALIVE:
            combatant.current_hp = 1
            if "unconscious" in combatant.conditions:
                combatant.conditions.remove("unconscious")

        return {
            "type": "death_save",
            "combatant": combatant.name,
            "roll": result.roll,
            "success": result.success,
            "successes": result.total_successes,
            "failures": result.total_failures,
            "outcome": result.outcome.value,
            "description": result.description,
        }

    def _apply_damage_to_combatant(
        self,
        combatant: Combatant,
        damage: int,
        is_crit: bool = False,
    ) -> None:
        """Apply damage, handle dropping to 0 HP and death saves."""
        if combatant.death_tracker.state == DeathState.DYING:
            take_damage_while_dying(
                combatant.death_tracker, damage, is_crit, combatant.max_hp,
            )
            if combatant.death_tracker.is_dead:
                combatant.alive = False
            return

        combatant.current_hp = max(0, combatant.current_hp - damage)

        if combatant.current_hp <= 0:
            overflow = damage - (combatant.current_hp + damage)
            if abs(combatant.current_hp - damage) >= combatant.max_hp and combatant.max_hp > 0:
                # Massive damage — instant death
                combatant.alive = False
                combatant.death_tracker.state = DeathState.INSTANT_DEATH
            else:
                combatant.current_hp = 0
                combatant.death_tracker.state = DeathState.DYING
                if "unconscious" not in combatant.conditions:
                    combatant.conditions.append("unconscious")

    def resolve_combat(
        self,
        player_data: dict,
        target_npcs: list[dict],
        hostile_npcs: list[dict] | None = None,
    ) -> EncounterResult:
        """Resolve a full combat encounter.

        Full D&D 5e combat cycle:
        1. Build combatants from data dicts.
        2. Roll initiative for all participants.
        3. Each combatant acts in initiative order (one round).
           - Check conditions: stunned/paralyzed/incapacitated skip turn.
           - Dying creatures make death saving throws.
           - Attacks account for conditions (advantage/disadvantage).
           - Dropping to 0 HP triggers death saves, not instant death (unless massive dmg).
        4. Return structured EncounterResult.
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

        # One round of combat: each combatant acts in initiative order
        for combatant in ordered:
            # ── Death saves for dying creatures ──
            if combatant.death_tracker.state == DeathState.DYING:
                save_info = self._handle_death_saves(combatant)
                if save_info:
                    encounter.combat_log.append(save_info["description"])
                    encounter.all_rolls.append(save_info)
                    if save_info["outcome"] == "dead":
                        if combatant.is_player:
                            encounter.player_killed = True
                        else:
                            encounter.npcs_killed.append(combatant.id)
                continue

            # ── Check if combatant can act ──
            can_act, reason = self._can_act(combatant)
            if not can_act:
                if reason:
                    encounter.combat_log.append(reason)
                continue

            # ── Determine target ──
            if combatant.is_player:
                target = next(
                    (n for n in npc_combatants if n.alive and n.death_tracker.state != DeathState.DEAD),
                    None,
                )
                if target is None:
                    continue
            else:
                if not player.alive and player.death_tracker.state not in (DeathState.DYING, DeathState.STABLE):
                    continue
                target = player

            # ── Resolve attack ──
            outcome = self._resolve_single_attack(combatant, target)

            encounter.attacks.append(outcome)
            encounter.combat_log.append(outcome.combat_result.narrative)
            encounter.all_rolls.extend(outcome.combat_result.rolls)

            # Apply damage through death save system
            if outcome.damage_dealt > 0:
                self._apply_damage_to_combatant(
                    target, outcome.damage_dealt,
                    is_crit=any(r.get("is_crit") for r in outcome.combat_result.rolls if isinstance(r, dict)),
                )

            # Check for kills
            if target.death_tracker.is_dead or not target.alive:
                target.alive = False
                if target.is_player:
                    encounter.player_killed = True
                elif target.id not in encounter.npcs_killed:
                    encounter.npcs_killed.append(target.id)

            if outcome.damage_dealt > 0 and not target.is_player:
                encounter.npcs_damaged[target.id] = (
                    encounter.npcs_damaged.get(target.id, 0)
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


    def resolve_spell_cast(
        self,
        caster: Combatant,
        spell_id: str,
        target_combatants: list[Combatant],
        cast_at_level: int | None = None,
    ) -> SpellResult:
        """Resolve a spell cast during combat using the spell engine."""
        # Check if caster can act
        if not can_take_actions(caster.conditions):
            return SpellResult(
                success=False, spell_name=spell_id, caster_name=caster.name,
                targets=[], effect_type="unknown",
                narrative=f"{caster.name} cannot cast — incapacitated!",
            )

        # Check if spell can be cast
        ok, reason = can_cast_spell(
            spell_id, caster.class_id, caster.level,
            caster.known_spells, caster.spell_slots_used, cast_at_level,
        )
        if not ok:
            return SpellResult(
                success=False, spell_name=spell_id, caster_name=caster.name,
                targets=[], effect_type="unknown", narrative=reason,
            )

        # Build spell targets
        spell_targets = [
            SpellTarget(
                id=t.id, name=t.name,
                current_hp=t.current_hp, max_hp=t.max_hp, ac=t.ac,
                ability_scores=t.ability_scores, level=t.level,
                saving_throw_proficiencies=t.saving_throw_proficiencies,
                conditions=t.conditions,
            )
            for t in target_combatants
        ]

        result = cast_spell(
            spell_id=spell_id,
            caster_name=caster.name,
            caster_class_id=caster.class_id,
            caster_level=caster.level,
            caster_ability_scores=caster.ability_scores,
            known_spells=caster.known_spells,
            spell_slots_used=caster.spell_slots_used,
            targets=spell_targets,
            cast_at_level=cast_at_level,
        )

        # Sync HP back to combatants
        for st, ct in zip(spell_targets, target_combatants):
            ct.current_hp = st.current_hp
            ct.conditions = st.conditions
            if ct.current_hp <= 0:
                ct.alive = False

        return result


combat_agent = CombatAgent()
