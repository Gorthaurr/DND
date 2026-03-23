"""Tests for CombatAgent -- combat orchestration with real dice engine."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.agents.combat_agent import (
    AttackOutcome,
    Combatant,
    CombatAgent,
    EncounterResult,
)
from app.dnd.combat_narrator import CombatResult


# ── Fixtures ──

@pytest.fixture
def agent():
    return CombatAgent()


def _make_player(**overrides) -> dict:
    base = {
        "id": "player-1",
        "name": "Aldric",
        "level": 5,
        "ability_scores": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 13, "CHA": 8},
        "current_hp": 44,
        "max_hp": 44,
        "ac": 18,
        "weapon_ids": ["longsword"],
        "armor_id": "chain-mail",
        "has_shield": True,
        "class_id": "fighter",
    }
    base.update(overrides)
    return base


def _make_npc(npc_id="npc-goblin-1", name="Goblin", hp=7, **overrides) -> dict:
    base = {
        "id": npc_id,
        "npc_id": npc_id,
        "name": name,
        "level": 1,
        "ability_scores": {"STR": 8, "DEX": 14, "CON": 10, "INT": 10, "WIS": 8, "CHA": 8},
        "current_hp": hp,
        "max_hp": hp,
        "ac": 13,
        "weapon_ids": ["scimitar"],
        "armor_id": "leather",
        "has_shield": True,
        "class_id": "commoner",
    }
    base.update(overrides)
    return base


def _make_strong_npc(npc_id="npc-ogre-1", name="Ogre", hp=59) -> dict:
    return _make_npc(
        npc_id=npc_id,
        name=name,
        hp=hp,
        level=5,
        ability_scores={"STR": 19, "DEX": 8, "CON": 16, "INT": 5, "WIS": 7, "CHA": 7},
        ac=11,
        weapon_ids=["greatclub"],
        armor_id=None,
        has_shield=False,
    )


# ── test_build_combatant ──

class TestBuildCombatant:
    def test_maps_player_data_correctly(self, agent):
        data = _make_player()
        c = agent.build_combatant(data, is_player=True)

        assert isinstance(c, Combatant)
        assert c.id == "player-1"
        assert c.name == "Aldric"
        assert c.is_player is True
        assert c.level == 5
        assert c.current_hp == 44
        assert c.max_hp == 44
        assert c.ac == 18
        assert c.weapon_ids == ["longsword"]
        assert c.armor_id == "chain-mail"
        assert c.has_shield is True
        assert c.class_id == "fighter"
        assert c.alive is True

    def test_maps_npc_data_correctly(self, agent):
        data = _make_npc()
        c = agent.build_combatant(data, is_player=False)

        assert c.id == "npc-goblin-1"
        assert c.name == "Goblin"
        assert c.is_player is False
        assert c.level == 1
        assert c.current_hp == 7

    def test_defaults_for_missing_fields(self, agent):
        c = agent.build_combatant({"id": "x", "name": "Peasant"}, is_player=False)

        assert c.level == 1
        assert c.current_hp == 10
        assert c.max_hp == 10
        assert c.ac == 10
        assert c.weapon_ids == []
        assert c.armor_id is None
        assert c.has_shield is False
        assert c.class_id == "commoner"

    def test_uses_npc_id_fallback(self, agent):
        c = agent.build_combatant({"npc_id": "npc-123", "name": "Bandit"}, is_player=False)
        assert c.id == "npc-123"


# ── test_roll_initiative ──

class TestRollInitiative:
    def test_returns_sorted_descending(self, agent):
        combatants = [
            agent.build_combatant(_make_player(), is_player=True),
            agent.build_combatant(_make_npc(), is_player=False),
            agent.build_combatant(_make_npc("npc-2", "Goblin 2"), is_player=False),
        ]
        result = agent.roll_initiative(combatants)

        assert len(result) == 3
        # Verify sorted descending by initiative
        for i in range(len(result) - 1):
            assert result[i].initiative >= result[i + 1].initiative

    def test_initiative_values_are_set(self, agent):
        combatants = [
            agent.build_combatant(_make_player(), is_player=True),
        ]
        agent.roll_initiative(combatants)
        # d20 range is 1-20, DEX mod for 12 is +1, so total is 2-21
        assert 2 <= combatants[0].initiative <= 21


# ── test_resolve_single_attack ──

class TestResolveSingleAttack:
    def test_returns_attack_outcome(self, agent):
        attacker = agent.build_combatant(_make_player(), is_player=True)
        defender = agent.build_combatant(_make_npc(hp=7), is_player=False)

        outcome = agent._resolve_single_attack(attacker, defender)

        assert isinstance(outcome, AttackOutcome)
        assert outcome.attacker_id == "player-1"
        assert outcome.attacker_name == "Aldric"
        assert outcome.defender_id == "npc-goblin-1"
        assert outcome.defender_name == "Goblin"
        assert isinstance(outcome.combat_result, CombatResult)
        assert outcome.damage_dealt >= 0
        assert outcome.defender_hp_after >= 0

    def test_damage_reduces_defender_hp(self, agent):
        attacker = agent.build_combatant(_make_player(), is_player=True)
        defender = agent.build_combatant(_make_npc(hp=100), is_player=False)

        outcome = agent._resolve_single_attack(attacker, defender)

        if outcome.damage_dealt > 0:
            assert defender.current_hp == 100 - outcome.damage_dealt
        else:
            assert defender.current_hp == 100

    def test_kill_sets_alive_false(self, agent):
        """Attack a 1 HP target multiple times until it dies."""
        attacker = agent.build_combatant(_make_player(), is_player=True)
        defender = agent.build_combatant(_make_npc(hp=1, ac=1), is_player=False)

        # With AC 1, almost guaranteed hit; 1 HP means any damage kills
        for _ in range(20):  # retry to handle rare misses
            defender.current_hp = 1
            defender.alive = True
            outcome = agent._resolve_single_attack(attacker, defender)
            if outcome.defender_killed:
                assert defender.alive is False
                assert defender.current_hp == 0
                return

        # If we get here after 20 tries with AC 1, something is wrong
        pytest.fail("Could not kill AC 1 target in 20 attempts")


# ── test_resolve_combat_player_wins ──

class TestResolveCombatPlayerWins:
    def test_player_kills_weak_npc(self, agent):
        """Player (level 5 fighter) vs goblin with 1 HP and AC 1 -- should win."""
        player = _make_player()
        npc = _make_npc(hp=1, ac=1)  # Extremely easy target

        # Run combat multiple times to account for randomness
        for _ in range(20):
            # Reset NPC HP for each attempt
            npc["current_hp"] = 1
            result = agent.resolve_combat(player, [npc])

            assert isinstance(result, EncounterResult)
            assert len(result.attacks) > 0
            assert len(result.initiative_order) == 2

            if result.npcs_killed:
                assert "npc-goblin-1" in result.npcs_killed
                return

        pytest.fail("Player could not kill 1 HP, AC 1 goblin in 20 encounters")


# ── test_resolve_combat_player_dies ──

class TestResolveCombatPlayerDies:
    def test_player_dies_against_overwhelming_force(self, agent):
        """Player with 1 HP vs 3 strong ogres -- should die."""
        player = _make_player(current_hp=1, ac=1)  # 1 HP, no armor
        ogres = [
            _make_strong_npc(f"ogre-{i}", f"Ogre {i}") for i in range(3)
        ]

        for _ in range(20):
            player["current_hp"] = 1
            result = agent.resolve_combat(player, ogres)

            assert isinstance(result, EncounterResult)
            if result.player_killed:
                assert result.player_hp_change < 0
                return

        pytest.fail("Player with 1 HP did not die vs 3 ogres in 20 encounters")


# ── test_resolve_combat_multiple_npcs ──

class TestResolveCombatMultipleNPCs:
    def test_three_npcs_all_participate(self, agent):
        player = _make_player()
        npcs = [
            _make_npc(f"npc-{i}", f"Goblin {i}") for i in range(3)
        ]

        result = agent.resolve_combat(player, npcs)

        assert isinstance(result, EncounterResult)
        assert len(result.initiative_order) == 4  # 1 player + 3 NPCs
        # At least player attacks + some NPCs attack
        assert len(result.attacks) >= 1
        assert len(result.combat_log) == len(result.attacks)

    def test_hostile_npcs_join_fight(self, agent):
        player = _make_player()
        targets = [_make_npc("npc-1", "Target")]
        hostiles = [_make_npc("npc-2", "Hostile Guard")]

        result = agent.resolve_combat(player, targets, hostile_npcs=hostiles)

        assert len(result.initiative_order) == 3  # player + target + hostile


# ── test_unarmed_combat ──

class TestUnarmedCombat:
    def test_unarmed_attack_works(self, agent):
        player = _make_player(weapon_ids=[])  # No weapons
        npc = _make_npc(hp=100, weapon_ids=[])  # No weapons, lots of HP

        result = agent.resolve_combat(player, [npc])

        assert isinstance(result, EncounterResult)
        assert len(result.attacks) >= 1
        # Unarmed does 1d1 + STR mod damage (guaranteed at least 0 on miss)
        for attack in result.attacks:
            assert isinstance(attack.combat_result, CombatResult)


# ── test_parse_combat_intent ──

class TestParseCombatIntent:
    @pytest.mark.asyncio
    async def test_combat_action_parsed(self, agent):
        mock_response = {
            "is_combat": True,
            "targets": [{"npc_id": "npc-goblin-1", "npc_name": "Goblin"}],
            "player_has_advantage": True,
            "player_has_disadvantage": False,
            "npcs_join_fight": [],
            "context": "Player attacks the goblin by surprise",
        }

        with patch.object(
            agent._intent_agent, "generate_json", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await agent.parse_combat_intent(
                player_action="I attack the goblin with my sword!",
                present_npcs=[{"npc_id": "npc-goblin-1", "name": "Goblin", "occupation": "raider"}],
                player={"name": "Aldric", "level": 5, "weapon_ids": ["longsword"]},
            )

        assert result["is_combat"] is True
        assert len(result["targets"]) == 1
        assert result["targets"][0]["npc_id"] == "npc-goblin-1"
        assert result["player_has_advantage"] is True
        assert result["context"] != ""

    @pytest.mark.asyncio
    async def test_defaults_filled_for_missing_keys(self, agent):
        """LLM returns partial response -- defaults should fill in."""
        mock_response = {"is_combat": True, "targets": [{"npc_id": "x", "npc_name": "Y"}]}

        with patch.object(
            agent._intent_agent, "generate_json", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await agent.parse_combat_intent(
                player_action="stab",
                present_npcs=[],
                player={"name": "X"},
            )

        assert result["player_has_advantage"] is False
        assert result["player_has_disadvantage"] is False
        assert result["npcs_join_fight"] == []
        assert result["context"] == ""


# ── test_non_combat_action ──

class TestNonCombatAction:
    @pytest.mark.asyncio
    async def test_talk_is_not_combat(self, agent):
        mock_response = {
            "is_combat": False,
            "targets": [],
            "player_has_advantage": False,
            "player_has_disadvantage": False,
            "npcs_join_fight": [],
            "context": "Player wants to have a conversation",
        }

        with patch.object(
            agent._intent_agent, "generate_json", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await agent.parse_combat_intent(
                player_action="I walk up to Goran and ask about the missing shipment.",
                present_npcs=[{"npc_id": "npc-goran", "name": "Goran", "occupation": "merchant"}],
                player={"name": "Aldric", "level": 5},
            )

        assert result["is_combat"] is False
        assert result["targets"] == []

    @pytest.mark.asyncio
    async def test_trade_is_not_combat(self, agent):
        mock_response = {
            "is_combat": False,
            "targets": [],
            "player_has_advantage": False,
            "player_has_disadvantage": False,
            "npcs_join_fight": [],
            "context": "Player wants to buy items",
        }

        with patch.object(
            agent._intent_agent, "generate_json", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await agent.parse_combat_intent(
                player_action="I'd like to buy a health potion from the shopkeeper.",
                present_npcs=[{"npc_id": "npc-shop", "name": "Elara", "occupation": "shopkeeper"}],
                player={"name": "Aldric", "level": 5},
            )

        assert result["is_combat"] is False


# ── test_combatant_as_attack_dict ──

class TestCombatantAsAttackDict:
    def test_conversion_format(self, agent):
        c = agent.build_combatant(_make_player(), is_player=True)
        d = agent._combatant_as_attack_dict(c)

        assert d["name"] == "Aldric"
        assert d["level"] == 5
        assert d["ability_scores"]["STR"] == 16
        assert d["armor_id"] == "chain-mail"
        assert d["has_shield"] is True
        assert d["weapon_ids"] == ["longsword"]


# ── test_encounter_result_structure ──

class TestEncounterResultStructure:
    def test_basic_encounter_has_all_fields(self, agent):
        player = _make_player()
        npc = _make_npc()

        result = agent.resolve_combat(player, [npc])

        assert isinstance(result.attacks, list)
        assert isinstance(result.combat_log, list)
        assert isinstance(result.all_rolls, list)
        assert isinstance(result.initiative_order, list)
        assert isinstance(result.npcs_killed, list)
        assert isinstance(result.npcs_damaged, dict)
        assert isinstance(result.player_hp_change, int)
        assert isinstance(result.player_killed, bool)

    def test_initiative_order_has_correct_keys(self, agent):
        player = _make_player()
        npc = _make_npc()

        result = agent.resolve_combat(player, [npc])

        for entry in result.initiative_order:
            assert "id" in entry
            assert "name" in entry
            assert "initiative" in entry
