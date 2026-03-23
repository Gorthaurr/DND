"""Tests for personality-driven schedule engine."""

from app.simulation.schedule import ScheduleEngine


def _make_npc(personality="Big Five: O:5/10, C:5/10, E:5/10, A:5/10, N:5/10",
              mood="neutral", archetype="stoic", occupation="blacksmith", **overrides):
    npc = {
        "id": "test-npc", "name": "Test", "occupation": occupation,
        "personality": personality, "mood": mood, "archetype": archetype,
        "trust_baseline": 0.0, "mood_baseline": 0.0,
        "aggression_baseline": 0.0, "confidence_baseline": 0.0,
    }
    npc.update(overrides)
    return npc


class TestScheduleEngine:
    def setup_method(self):
        self.engine = ScheduleEngine()

    def test_stoic_morning_mostly_work(self):
        """High C stoic: morning = work in vast majority of cases (90%+ due to 10% random)."""
        npc = _make_npc(personality="Big Five: O:3/10, C:9/10, E:3/10, A:5/10, N:3/10")
        work_count = 0
        runs = 100
        for day in range(runs):
            result = self.engine.get_activity(npc, "morning", day)
            if result["action"] == "work":
                work_count += 1
        assert work_count >= 80, f"Expected mostly work, got {work_count}/100"

    def test_returns_dict_with_required_keys(self):
        npc = _make_npc()
        result = self.engine.get_activity(npc, "morning", 1)
        assert "action" in result
        assert "location_hint" in result
        assert "activity_desc" in result

    def test_work_desc_includes_occupation(self):
        npc = _make_npc(occupation="farmer")
        result = self.engine.get_activity(npc, "morning", 1)
        if result["action"] == "work":
            assert "farmer" in result["activity_desc"]

    def test_fearful_mood_avoids_social(self):
        """Fearful NPC prefers rest/pray over socializing."""
        npc = _make_npc(mood="fearful", archetype="gossip")
        actions = set()
        for day in range(50):
            r = self.engine.get_activity(npc, "evening", day)
            actions.add(r["action"])
        # Should see rest or pray at least sometimes
        assert "rest" in actions or "pray" in actions

    def test_distrustful_avoids_evening_socialize(self):
        """NPC with low trust_baseline avoids evening socializing."""
        npc = _make_npc(archetype="gossip", trust_baseline=-0.5)
        # Gossip normally socializes evening, but distrustful → rest
        actions = set()
        for day in range(30):
            r = self.engine.get_activity(npc, "evening", day)
            actions.add(r["action"])
        assert "rest" in actions

    def test_variety_over_multiple_days(self):
        """Schedule should produce some variety over many days."""
        npc = _make_npc()
        actions = set()
        for day in range(100):
            for phase in ["morning", "afternoon", "evening"]:
                r = self.engine.get_activity(npc, phase, day)
                actions.add(r["action"])
        # Should have at least 3 different actions over 300 rolls
        assert len(actions) >= 3

    def test_valid_action_returned(self):
        """All returned actions should be from the known set."""
        valid = {"work", "rest", "patrol", "forage", "pray", "socialize",
                 "train", "investigate", "study", "gather", "trade", "eat",
                 "advise", "preach", "help"}
        npc = _make_npc()
        for day in range(50):
            for phase in ["morning", "afternoon", "evening"]:
                r = self.engine.get_activity(npc, phase, day)
                assert r["action"] in valid, f"Unknown action: {r['action']}"
