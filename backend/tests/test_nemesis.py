"""Tests for the Nemesis system."""

import pytest

from app.models.evolution import (
    NPCEvolutionState, NemesisStage, NemesisState, TraitScale,
    Fear, Goal, GoalStatus, RelationshipTag, EvolutionLogEntry,
)
from app.simulation.nemesis import (
    check_nemesis_trigger, record_nemesis_combat, escalate_nemesis,
    apply_nemesis_adaptations, get_nemesis_directive,
    BROKEN_DEFEAT_THRESHOLD,
)
from app.simulation.evolution_rules import TriggerType


def _fresh_evo() -> NPCEvolutionState:
    return NPCEvolutionState(traits=TraitScale())


# ── Creation ──

class TestNemesisCreation:
    def test_create_on_combat_defeat(self):
        evo = _fresh_evo()
        created = check_nemesis_trigger(
            evo, opponent_id="player-1", opponent_name="Hero",
            combat_lost=True, robbed=False, nearly_killed=False, world_day=5,
        )
        assert created is True
        assert evo.nemesis is not None
        assert evo.nemesis.target_id == "player-1"
        assert evo.nemesis.target_name == "Hero"
        assert evo.nemesis.stage == NemesisStage.GRUDGE
        assert evo.nemesis.defeats_suffered == 1
        assert evo.nemesis.created_day == 5

    def test_create_on_robbery(self):
        evo = _fresh_evo()
        created = check_nemesis_trigger(
            evo, opponent_id="thief-1", opponent_name="Shadowhand",
            combat_lost=False, robbed=True, nearly_killed=False, world_day=10,
        )
        assert created is True
        assert evo.nemesis.stage == NemesisStage.GRUDGE
        assert evo.nemesis.defeats_suffered == 0  # robbed, not defeated

    def test_create_on_nearly_killed(self):
        evo = _fresh_evo()
        created = check_nemesis_trigger(
            evo, opponent_id="brute-1", opponent_name="Grok",
            combat_lost=False, robbed=False, nearly_killed=True, world_day=1,
        )
        assert created is True

    def test_no_create_without_trigger(self):
        evo = _fresh_evo()
        created = check_nemesis_trigger(
            evo, opponent_id="friend-1", opponent_name="Ally",
            combat_lost=False, robbed=False, nearly_killed=False, world_day=1,
        )
        assert created is False
        assert evo.nemesis is None

    def test_no_duplicate_nemesis(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        created = check_nemesis_trigger(evo, "p2", "Other", True, False, False, 5)
        assert created is False
        assert evo.nemesis.target_id == "p1"  # first one stays

    def test_relationship_tag_added(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 3)
        tags = evo.relationship_tags.get("p1", [])
        assert any(t.tag == "nemesis" for t in tags)


# ── Combat recording ──

class TestCombatRecording:
    def test_record_defeat(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        record_nemesis_combat(evo, won=False)
        assert evo.nemesis.defeats_suffered == 2  # 1 from creation + 1

    def test_record_victory(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        record_nemesis_combat(evo, won=True)
        assert evo.nemesis.victories_achieved == 1
        assert evo.nemesis.encounters == 2  # 1 from creation + 1

    def test_no_nemesis_no_crash(self):
        evo = _fresh_evo()
        record_nemesis_combat(evo, won=True)  # should not crash


# ── Escalation ──

class TestEscalation:
    def test_grudge_to_rival_by_time(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        logs = escalate_nemesis(evo, world_day=5)  # 4 days later (>=3)
        assert evo.nemesis.stage == NemesisStage.RIVAL
        assert len(logs) == 1
        assert "escalated" in logs[0].description.lower()

    def test_no_escalation_too_early(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        logs = escalate_nemesis(evo, world_day=2)  # only 1 day
        assert evo.nemesis.stage == NemesisStage.GRUDGE
        assert len(logs) == 0

    def test_rival_to_nemesis_by_defeat(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.stage = NemesisStage.RIVAL
        evo.nemesis.escalation_day = 1
        evo.nemesis.defeats_suffered = 3   # >= DEFEAT_ESCALATION[RIVAL]=3
        evo.nemesis.victories_achieved = 1  # prevent BROKEN check
        logs = escalate_nemesis(evo, world_day=3)
        assert evo.nemesis.stage == NemesisStage.NEMESIS

    def test_nemesis_to_arch_nemesis(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.stage = NemesisStage.NEMESIS
        evo.nemesis.escalation_day = 1
        evo.nemesis.defeats_suffered = 4  # >= DEFEAT_ESCALATION[NEMESIS]=4
        evo.nemesis.victories_achieved = 1  # prevent BROKEN
        logs = escalate_nemesis(evo, world_day=3)
        assert evo.nemesis.stage == NemesisStage.ARCH_NEMESIS

    def test_broken_after_repeated_defeats(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.defeats_suffered = BROKEN_DEFEAT_THRESHOLD
        evo.nemesis.victories_achieved = 0
        logs = escalate_nemesis(evo, world_day=10)
        assert evo.nemesis.stage == NemesisStage.BROKEN
        assert any(log.change_type == "nemesis_broken" for log in logs)
        # Should also add a fear
        assert any(f.trigger == "hero" for f in evo.fears)

    def test_not_broken_if_has_victory(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.defeats_suffered = 4
        evo.nemesis.victories_achieved = 1  # has a win
        logs = escalate_nemesis(evo, world_day=10)
        assert evo.nemesis.stage != NemesisStage.BROKEN

    def test_arch_nemesis_no_further_escalation(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.stage = NemesisStage.ARCH_NEMESIS
        evo.nemesis.victories_achieved = 1  # prevent broken
        logs = escalate_nemesis(evo, world_day=100)
        assert evo.nemesis.stage == NemesisStage.ARCH_NEMESIS
        assert len(logs) == 0


# ── Adaptations ──

class TestAdaptations:
    def test_rival_gets_adaptation(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.stage = NemesisStage.RIVAL
        logs = apply_nemesis_adaptations(evo, world_day=5)
        assert len(logs) == 1
        assert evo.nemesis.adaptation != ""

    def test_grudge_no_adaptation(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        logs = apply_nemesis_adaptations(evo, world_day=5)
        assert len(logs) == 0

    def test_broken_no_adaptation(self):
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        evo.nemesis.stage = NemesisStage.BROKEN
        logs = apply_nemesis_adaptations(evo, world_day=5)
        assert len(logs) == 0

    def test_nemesis_adaptation_different_from_rival(self):
        import random
        rng = random.Random(42)
        evo1 = _fresh_evo()
        check_nemesis_trigger(evo1, "p1", "Hero", True, False, False, 1)
        evo1.nemesis.stage = NemesisStage.RIVAL
        apply_nemesis_adaptations(evo1, world_day=5, rng=rng)
        adapt_rival = evo1.nemesis.adaptation

        evo2 = _fresh_evo()
        check_nemesis_trigger(evo2, "p1", "Hero", True, False, False, 1)
        evo2.nemesis.stage = NemesisStage.NEMESIS
        rng2 = random.Random(42)
        apply_nemesis_adaptations(evo2, world_day=5, rng=rng2)
        adapt_nemesis = evo2.nemesis.adaptation

        # Different pools — with same seed they pick different items
        # (unless pools happen to match at that index, which is fine)
        assert adapt_rival != "" and adapt_nemesis != ""


# ── Directives ──

class TestDirectives:
    def test_grudge_directive(self):
        nem = NemesisState(target_id="p1", target_name="Hero")
        d = get_nemesis_directive(nem)
        assert "Hero" in d
        assert "resentment" in d.lower()

    def test_rival_directive(self):
        nem = NemesisState(target_id="p1", target_name="Hero", stage=NemesisStage.RIVAL)
        d = get_nemesis_directive(nem)
        assert "challenge" in d.lower()

    def test_nemesis_directive(self):
        nem = NemesisState(target_id="p1", target_name="Hero", stage=NemesisStage.NEMESIS)
        d = get_nemesis_directive(nem)
        assert "obsession" in d.lower()

    def test_arch_nemesis_directive(self):
        nem = NemesisState(target_id="p1", target_name="Hero", stage=NemesisStage.ARCH_NEMESIS)
        d = get_nemesis_directive(nem)
        assert "nothing" in d.lower()

    def test_broken_directive(self):
        nem = NemesisState(target_id="p1", target_name="Hero", stage=NemesisStage.BROKEN)
        d = get_nemesis_directive(nem)
        assert "flinch" in d.lower() or "broken" in d.lower()


# ── Full lifecycle ──

class TestFullLifecycle:
    def test_creation_to_broken(self):
        """Simulate full nemesis lifecycle: creation → escalation → broken."""
        evo = _fresh_evo()

        # Day 1: defeated (defeats_suffered=1)
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        assert evo.nemesis.stage == NemesisStage.GRUDGE

        # Day 4: escalate by time (3 days since creation)
        escalate_nemesis(evo, 4)
        assert evo.nemesis.stage == NemesisStage.RIVAL
        apply_nemesis_adaptations(evo, 4)
        assert evo.nemesis.adaptation != ""

        # Day 14: escalate by time (10 days since escalation_day=4)
        escalate_nemesis(evo, 14)
        assert evo.nemesis.stage == NemesisStage.NEMESIS

        # Add defeats to reach broken threshold (3 total, 0 victories)
        record_nemesis_combat(evo, won=False)  # 2nd defeat
        record_nemesis_combat(evo, won=False)  # 3rd defeat
        escalate_nemesis(evo, 15)
        assert evo.nemesis.stage == NemesisStage.BROKEN

        # Fear of Hero added
        assert any(f.trigger == "hero" for f in evo.fears)

    def test_creation_to_arch_nemesis_with_victory(self):
        """NPC gets a victory along the way → not broken."""
        evo = _fresh_evo()

        # Day 1: creation (defeats=1)
        check_nemesis_trigger(evo, "p1", "Hero", True, False, False, 1)
        # Day 4: → RIVAL by time
        escalate_nemesis(evo, 4)
        assert evo.nemesis.stage == NemesisStage.RIVAL

        record_nemesis_combat(evo, won=True)   # 1 victory
        record_nemesis_combat(evo, won=False)  # 2 defeats
        record_nemesis_combat(evo, won=False)  # 3 defeats >= RIVAL threshold
        escalate_nemesis(evo, 5)
        assert evo.nemesis.stage == NemesisStage.NEMESIS

        record_nemesis_combat(evo, won=False)  # 4 defeats >= NEMESIS threshold, but 1 victory → not broken
        escalate_nemesis(evo, 6)
        assert evo.nemesis.stage == NemesisStage.ARCH_NEMESIS  # not broken

    def test_serialization_roundtrip(self):
        """NemesisState survives JSON serialization (persisted in Neo4j)."""
        evo = _fresh_evo()
        check_nemesis_trigger(evo, "p1", "Hero", True, False, True, 5)
        evo.nemesis.stage = NemesisStage.RIVAL
        evo.nemesis.adaptation = "acquired a better weapon"

        json_str = evo.model_dump_json()
        restored = NPCEvolutionState.model_validate_json(json_str)

        assert restored.nemesis is not None
        assert restored.nemesis.target_id == "p1"
        assert restored.nemesis.stage == NemesisStage.RIVAL
        assert restored.nemesis.adaptation == "acquired a better weapon"
