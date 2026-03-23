"""Tests for rooms API — Pydantic schemas and module import."""


class TestRoomSchemas:
    def test_create_room_request(self):
        from app.api.rooms import CreateRoomRequest
        req = CreateRoomRequest(name="test-room")
        assert req.name == "test-room"
        assert req.max_players == 6
        assert req.world_name == "medieval_village"

    def test_join_room_request(self):
        from app.api.rooms import JoinRoomRequest
        req = JoinRoomRequest()
        assert req.character_name == "Adventurer"

    def test_room_response(self):
        from app.api.rooms import RoomResponse
        # Just check importable
        assert RoomResponse is not None

    def test_router_exists(self):
        from app.api.rooms import router
        assert router is not None
        assert router.prefix == "/rooms"
