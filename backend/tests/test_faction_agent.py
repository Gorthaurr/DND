"""Tests for Faction Agent — collective faction decisions."""

from app.agents.faction_agent import FactionAgent


class TestGenerateMemberDirectives:
    def setup_method(self):
        self.agent = FactionAgent()
        self.members = [
            {"id": "npc-1", "name": "Guard", "occupation": "guard", "faction_role": "warrior"},
            {"id": "npc-2", "name": "Chief", "occupation": "chief", "faction_role": "leader"},
            {"id": "npc-3", "name": "Scout", "occupation": "ranger", "faction_role": "spy"},
            {"id": "npc-4", "name": "Smith", "occupation": "blacksmith", "faction_role": "member"},
        ]

    def test_raid_warrior_directive(self):
        directives = self.agent.generate_member_directives("raid", self.members)
        assert "npc-1" in directives
        assert "combat" in directives["npc-1"].lower() or "weapon" in directives["npc-1"].lower()

    def test_raid_leader_directive(self):
        directives = self.agent.generate_member_directives("raid", self.members)
        assert "plan" in directives["npc-2"].lower() or "coordinate" in directives["npc-2"].lower()

    def test_raid_spy_directive(self):
        directives = self.agent.generate_member_directives("raid", self.members)
        assert "scout" in directives["npc-3"].lower() or "weakness" in directives["npc-3"].lower()

    def test_defend_all_patrol(self):
        directives = self.agent.generate_member_directives("defend", self.members)
        for npc_id, d in directives.items():
            d_lower = d.lower()
            assert any(kw in d_lower for kw in (
                "guard", "protect", "patrol", "ready", "stockpile", "watch",
                "rally", "reinforce", "defend", "fortif", "close",
            )), f"Unexpected defend directive for {npc_id}: {d}"

    def test_trade_strategy(self):
        directives = self.agent.generate_member_directives("trade", self.members)
        assert "trade" in directives["npc-1"].lower() or "escort" in directives["npc-1"].lower()

    def test_expand_strategy(self):
        directives = self.agent.generate_member_directives("expand", self.members)
        assert "recruit" in directives["npc-2"].lower() or "influence" in directives["npc-2"].lower()

    def test_all_members_get_directives(self):
        for strategy in ["expand", "defend", "diplomacy", "raid", "trade"]:
            directives = self.agent.generate_member_directives(strategy, self.members)
            assert len(directives) == len(self.members)

    def test_unknown_role_gets_default(self):
        members = [{"id": "npc-x", "name": "Nobody", "occupation": "peasant", "faction_role": "unknown_role"}]
        directives = self.agent.generate_member_directives("raid", members)
        assert "npc-x" in directives


class TestFallbackStrategy:
    def test_fallback_returns_directives(self):
        agent = FactionAgent()
        faction = {"strategy": "defend", "goals": ["protect village"]}
        members = [{"id": "npc-1", "name": "Guard", "faction_role": "warrior"}]
        result = agent._fallback_strategy(faction, members)
        assert result["strategy"] == "defend"
        assert "npc-1" in result["directives"]
