"""Tests for database models and graph queries structure."""

from app.db.models import Base, User, Room, RoomMember, WorldSnapshot
from app.graph.queries import GraphQueries


class TestDBModels:
    def test_user_table_name(self):
        assert User.__tablename__ == "users"

    def test_room_table_name(self):
        assert Room.__tablename__ == "rooms"

    def test_room_member_table_name(self):
        assert RoomMember.__tablename__ == "room_members"

    def test_world_snapshot_table_name(self):
        assert WorldSnapshot.__tablename__ == "world_snapshots"

    def test_base_metadata(self):
        tables = Base.metadata.tables
        assert "users" in tables
        assert "rooms" in tables
        assert "room_members" in tables
        assert "world_snapshots" in tables

    def test_user_columns(self):
        cols = {c.name for c in User.__table__.columns}
        assert "email" in cols
        assert "username" in cols
        assert "password_hash" in cols

    def test_room_columns(self):
        cols = {c.name for c in Room.__table__.columns}
        assert "world_id" in cols
        assert "owner_id" in cols
        assert "status" in cols
        assert "world_config" in cols


class TestGraphQueries:
    def test_world_id_default(self):
        from unittest.mock import MagicMock
        driver = MagicMock()
        gq = GraphQueries(driver)
        assert gq.world_id == "default"

    def test_world_id_custom(self):
        from unittest.mock import MagicMock
        driver = MagicMock()
        gq = GraphQueries(driver, world_id="my-world")
        assert gq.world_id == "my-world"

    def test_has_npc_methods(self):
        assert hasattr(GraphQueries, "create_npc")
        assert hasattr(GraphQueries, "get_npc")
        assert hasattr(GraphQueries, "update_npc")
        assert hasattr(GraphQueries, "kill_npc")

    def test_has_faction_methods(self):
        assert hasattr(GraphQueries, "get_all_factions")
        assert hasattr(GraphQueries, "get_faction_members")
        assert hasattr(GraphQueries, "update_faction")

    def test_has_location_methods(self):
        assert hasattr(GraphQueries, "update_location")
        assert hasattr(GraphQueries, "get_events_at_location")

    def test_has_world_state_methods(self):
        assert hasattr(GraphQueries, "update_world_state")
        assert hasattr(GraphQueries, "get_world_state")
