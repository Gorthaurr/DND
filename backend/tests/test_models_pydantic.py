"""Tests for Pydantic models (character, player, quest, scenario, world, schemas)."""

from app.models.player import Player, PlayerAction, DialogueRequest
from app.models.quest import Quest, QuestObjective
from app.models.scenario import Scenario, ScenarioPhase
from app.models.world import WorldState, WorldLogEntry, Location, WorldMap
from app.api.schemas import (
    ActionRequest, ActionResponse, DialogueResponse,
    WorldStateResponse, LookResponse, TickResponse,
    NPCInfoResponse, NPCObserveResponse,
)


class TestPlayerModels:
    def test_player_defaults(self):
        p = Player()
        assert p.id == "player-1"
        assert p.gold == 50

    def test_player_action(self):
        a = PlayerAction(action="attack goblin")
        assert a.action == "attack goblin"

    def test_dialogue_request(self):
        d = DialogueRequest(npc_id="npc-1", message="Hello")
        assert d.npc_id == "npc-1"


class TestQuestModels:
    def test_quest_objective(self):
        o = QuestObjective(description="Kill the dragon")
        assert not o.completed

    def test_quest_defaults(self):
        q = Quest(id="q-1", title="Dragon Hunt", description="Hunt the dragon")
        assert q.status == "available"
        assert q.difficulty == "medium"
        assert q.reward_gold == 0

    def test_quest_with_objectives(self):
        q = Quest(
            id="q-1", title="Test", description="Test",
            objectives=[QuestObjective(description="Step 1")],
            reward_gold=100,
        )
        assert len(q.objectives) == 1


class TestScenarioModels:
    def test_scenario_phase(self):
        p = ScenarioPhase(
            phase_id="ph-1", name="Inciting Incident",
            description="Something happens", trigger_day=5,
        )
        assert not p.completed
        assert p.npc_directives == {}

    def test_scenario_defaults(self):
        s = Scenario(id="sc-1", title="The Dark Pact", description="Evil rises")
        assert s.active is True
        assert s.tension_level == "low"
        assert s.current_phase_index == 0

    def test_scenario_with_phases(self):
        s = Scenario(
            id="sc-1", title="Test", description="Test",
            phases=[ScenarioPhase(phase_id="p1", name="P1", description="D", trigger_day=1)],
            involved_npc_ids=["npc-1", "npc-2"],
        )
        assert len(s.phases) == 1
        assert len(s.involved_npc_ids) == 2


class TestWorldModels:
    def test_world_state_defaults(self):
        w = WorldState()
        assert w.day == 1
        assert not w.tick_running

    def test_world_log_entry(self):
        e = WorldLogEntry(day=5, summary="Peaceful day")
        assert e.events == []

    def test_location(self):
        l = Location(id="loc-1", name="Tavern", type="tavern", description="Cozy")
        assert l.name == "Tavern"

    def test_world_map(self):
        m = WorldMap(
            locations=[Location(id="l1", name="A", type="t", description="d")],
            connections=[{"from": "l1", "to": "l2"}],
        )
        assert len(m.locations) == 1


class TestSchemas:
    def test_action_request(self):
        r = ActionRequest(action="attack goblin")
        assert r.action == "attack goblin"

    def test_action_response(self):
        r = ActionResponse(narration="You swing your sword.")
        assert r.npcs_involved == []

    def test_dialogue_response(self):
        r = DialogueResponse(npc_name="Finn", dialogue="Hello!", mood="content")
        assert r.npc_name == "Finn"

    def test_world_state_response(self):
        r = WorldStateResponse(
            day=1, player_location={"id": "l1"}, player_gold=50,
            player_inventory=[],
        )
        assert r.player_hp == 10

    def test_look_response(self):
        r = LookResponse(location={"id": "l1"}, npcs=[], items=[], exits=[])
        assert r.npcs == []

    def test_tick_response(self):
        r = TickResponse(day=5, events=[], npc_actions=[], interactions=[])
        assert r.active_scenarios == []

    def test_npc_info_response(self):
        r = NPCInfoResponse(id="n1", name="Bob", occupation="guard", mood="neutral", description="A guard")
        assert r.name == "Bob"

    def test_npc_observe_response(self):
        r = NPCObserveResponse(
            id="n1", name="Bob", personality="O:5", backstory="born",
            goals=["survive"], mood="neutral", occupation="guard", age=30,
            location={"id": "l1", "name": "Square"},
            relationships=[], recent_memories=[],
        )
        assert r.alive is True
        assert r.relationships == []
