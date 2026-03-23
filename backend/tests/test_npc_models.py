"""Tests for NPC data models."""

import pytest
from pydantic import ValidationError

from app.models.npc import NPC, NPCContext, NPCDecision, NPCRelationship


class TestNPCRelationship:
    def test_valid_relationship(self):
        r = NPCRelationship(npc_id="npc-1", name="Bob", sentiment=0.5, reason="friends")
        assert r.sentiment == 0.5

    def test_sentiment_bounds(self):
        # pydantic should enforce -1.0 to 1.0
        with pytest.raises(ValidationError):
            NPCRelationship(npc_id="x", name="x", sentiment=1.5, reason="x")
        with pytest.raises(ValidationError):
            NPCRelationship(npc_id="x", name="x", sentiment=-1.5, reason="x")


class TestNPCDecision:
    def test_basic_decision(self):
        d = NPCDecision(action="work", reasoning="nothing to do")
        assert d.action == "work"
        assert d.target is None
        assert d.mood_change == "same"

    def test_full_decision(self):
        d = NPCDecision(
            action="fight", target="Goblin", dialogue="Prepare to die!",
            reasoning="protecting village", mood_change="worse",
            consequence="Goblin injured",
        )
        assert d.target == "Goblin"
        assert d.consequence == "Goblin injured"


class TestNPCContext:
    def test_minimal_context(self):
        ctx = NPCContext(
            npc_id="npc-1", name="Test", personality="Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10",
            backstory="A test", goals=["survive"], mood="neutral", occupation="guard",
            age=30, location_name="Square", location_description="Town square",
            nearby_npcs=[], relationships=[], recent_memories=[], recent_events=[],
            world_day=1,
        )
        assert ctx.npc_id == "npc-1"

    def test_new_fields_defaults(self):
        ctx = NPCContext(
            npc_id="npc-1", name="Test", personality="", backstory="", goals=[],
            mood="neutral", occupation="guard", age=30,
            location_name="X", location_description="X",
            nearby_npcs=[], relationships=[], recent_memories=[], recent_events=[],
            world_day=1,
        )
        assert ctx.season is None
        assert ctx.weather is None
        assert ctx.local_shortages == []
        assert ctx.faction_directive is None
        assert ctx.trust_baseline == 0.0
        assert ctx.speech_instructions is None
        assert ctx.biography is None

    def test_new_fields_set(self):
        ctx = NPCContext(
            npc_id="npc-1", name="Test", personality="", backstory="", goals=[],
            mood="neutral", occupation="guard", age=30,
            location_name="X", location_description="X",
            nearby_npcs=[], relationships=[], recent_memories=[], recent_events=[],
            world_day=1,
            season="winter", weather="snow", location_condition="frozen",
            local_shortages=["food"], faction_directive="Guard the gate",
            trust_baseline=-0.5, mood_baseline=0.3,
            biography="Born in a small village...",
            speech_instructions="- Be blunt\n- No apologies",
        )
        assert ctx.season == "winter"
        assert ctx.local_shortages == ["food"]
        assert ctx.trust_baseline == -0.5
        assert ctx.biography == "Born in a small village..."


class TestNPCModel:
    def test_npc_defaults(self):
        npc = NPC(
            id="npc-1", name="Test", personality="", backstory="",
            goals=[], mood="neutral", occupation="guard", age=30,
        )
        assert npc.alive is True
        assert npc.level == 1
        assert npc.gold == 0
        assert npc.trust_baseline == 0.0
        assert npc.biography == ""

    def test_npc_with_baselines(self):
        npc = NPC(
            id="npc-1", name="Test", personality="", backstory="",
            goals=[], mood="angry", occupation="thief", age=25,
            trust_baseline=-0.5, aggression_baseline=0.3,
        )
        assert npc.trust_baseline == -0.5
        assert npc.aggression_baseline == 0.3
