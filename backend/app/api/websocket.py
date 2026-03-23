"""WebSocket endpoint for real-time multiplayer game updates.

Supports rooms: each room has its own set of connected players.
Messages are broadcast per-room, with support for targeted player messages.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth.jwt import decode_token
from app.utils.logger import get_logger

log = get_logger("websocket")

ws_router = APIRouter()


class RoomConnectionManager:
    """Manages WebSocket connections organized by room."""

    def __init__(self):
        # {room_id: {user_id: WebSocket}}
        self._rooms: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, ws: WebSocket, room_id: str, user_id: str) -> None:
        await ws.accept()
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        self._rooms[room_id][user_id] = ws
        log.info("ws_connected", room=room_id, user=user_id,
                 room_size=len(self._rooms[room_id]))

        # Notify other room members
        await self.broadcast_to_room(room_id, {
            "type": "player_joined",
            "user_id": user_id,
        }, exclude=user_id)

    async def disconnect(self, room_id: str, user_id: str) -> None:
        if room_id in self._rooms:
            self._rooms[room_id].pop(user_id, None)
            if not self._rooms[room_id]:
                del self._rooms[room_id]
            else:
                await self.broadcast_to_room(room_id, {
                    "type": "player_left",
                    "user_id": user_id,
                })
        log.info("ws_disconnected", room=room_id, user=user_id)

    async def broadcast_to_room(
        self, room_id: str, message: dict[str, Any], exclude: str | None = None,
    ) -> None:
        """Send message to all players in a room."""
        room = self._rooms.get(room_id, {})
        dead = []
        for uid, ws in room.items():
            if uid == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(uid)
        for uid in dead:
            room.pop(uid, None)

    async def send_to_player(
        self, room_id: str, user_id: str, message: dict[str, Any],
    ) -> None:
        """Send message to a specific player."""
        ws = self._rooms.get(room_id, {}).get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self._rooms.get(room_id, {}).pop(user_id, None)

    def get_online_users(self, room_id: str) -> list[str]:
        """Get list of user IDs currently connected to a room."""
        return list(self._rooms.get(room_id, {}).keys())

    def is_room_online(self, room_id: str) -> bool:
        """Check if any players are online in a room."""
        return bool(self._rooms.get(room_id))


manager = RoomConnectionManager()


@ws_router.websocket("/ws/game/{room_id}")
async def game_websocket(ws: WebSocket, room_id: str, token: str = Query(...)):
    """WebSocket endpoint for a game room.

    Connect: ws://host/ws/game/{room_id}?token={jwt_token}
    """
    # Authenticate
    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001, reason="Invalid token")
        return

    user_id = payload.get("sub", "unknown")

    await manager.connect(ws, room_id, user_id)
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await ws.send_json({"type": "pong"})

                elif msg_type == "chat":
                    # Broadcast chat message to room
                    await manager.broadcast_to_room(room_id, {
                        "type": "chat",
                        "user_id": user_id,
                        "username": payload.get("username", "unknown"),
                        "message": msg.get("message", ""),
                    })

            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.disconnect(room_id, user_id)


# ── Legacy single-player endpoint (backward compat) ──

@ws_router.websocket("/ws/game")
async def legacy_game_websocket(ws: WebSocket):
    """Legacy single-player WebSocket (no auth, default room)."""
    await manager.connect(ws, "default", "player-1")
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.disconnect("default", "player-1")
