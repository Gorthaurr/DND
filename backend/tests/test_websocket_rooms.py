"""Tests for WebSocket room management."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.api.websocket import RoomConnectionManager


class TestRoomConnectionManager:
    def test_empty_room_not_online(self):
        m = RoomConnectionManager()
        assert not m.is_room_online("room-1")

    def test_get_online_users_empty(self):
        m = RoomConnectionManager()
        assert m.get_online_users("room-1") == []

    @pytest.mark.asyncio
    async def test_connect_and_online(self):
        m = RoomConnectionManager()
        ws = AsyncMock()
        await m.connect(ws, "room-1", "user-1")
        assert m.is_room_online("room-1")
        assert "user-1" in m.get_online_users("room-1")

    @pytest.mark.asyncio
    async def test_disconnect(self):
        m = RoomConnectionManager()
        ws = AsyncMock()
        await m.connect(ws, "room-1", "user-1")
        await m.disconnect("room-1", "user-1")
        assert not m.is_room_online("room-1")

    @pytest.mark.asyncio
    async def test_broadcast_to_room(self):
        m = RoomConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await m.connect(ws1, "room-1", "user-1")
        await m.connect(ws2, "room-1", "user-2")
        await m.broadcast_to_room("room-1", {"type": "test"})
        ws1.send_json.assert_called_with({"type": "test"})
        ws2.send_json.assert_called_with({"type": "test"})

    @pytest.mark.asyncio
    async def test_broadcast_with_exclude(self):
        m = RoomConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await m.connect(ws1, "room-1", "user-1")
        await m.connect(ws2, "room-1", "user-2")
        # Reset mocks after connect (connect broadcasts player_joined)
        ws1.send_json.reset_mock()
        ws2.send_json.reset_mock()
        await m.broadcast_to_room("room-1", {"type": "test"}, exclude="user-1")
        ws1.send_json.assert_not_called()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_player(self):
        m = RoomConnectionManager()
        ws = AsyncMock()
        await m.connect(ws, "room-1", "user-1")
        await m.send_to_player("room-1", "user-1", {"msg": "hi"})
        ws.send_json.assert_called_with({"msg": "hi"})

    @pytest.mark.asyncio
    async def test_send_to_nonexistent_player(self):
        m = RoomConnectionManager()
        # Should not crash
        await m.send_to_player("room-1", "ghost", {"msg": "hi"})

    @pytest.mark.asyncio
    async def test_broadcast_removes_dead_connections(self):
        m = RoomConnectionManager()
        ws_alive = AsyncMock()
        ws_dead = AsyncMock()
        ws_dead.send_json.side_effect = Exception("connection lost")
        await m.connect(ws_alive, "room-1", "alive")
        await m.connect(ws_dead, "room-1", "dead")
        await m.broadcast_to_room("room-1", {"type": "test"})
        # Dead connection should be removed
        assert "dead" not in m.get_online_users("room-1")
        assert "alive" in m.get_online_users("room-1")

    @pytest.mark.asyncio
    async def test_multiple_rooms_isolated(self):
        m = RoomConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await m.connect(ws1, "room-1", "user-1")
        await m.connect(ws2, "room-2", "user-2")
        await m.broadcast_to_room("room-1", {"type": "test"})
        ws1.send_json.assert_called()
        ws2.send_json.assert_not_called()

    @pytest.mark.asyncio
    async def test_disconnect_last_user_removes_room(self):
        m = RoomConnectionManager()
        ws = AsyncMock()
        await m.connect(ws, "room-1", "user-1")
        await m.disconnect("room-1", "user-1")
        assert "room-1" not in m._rooms
