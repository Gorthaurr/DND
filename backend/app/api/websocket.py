"""WebSocket endpoint for real-time game updates."""

import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils.logger import get_logger

log = get_logger("websocket")

ws_router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        log.info("ws_connected", total=len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)
        log.info("ws_disconnected", total=len(self._connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


manager = ConnectionManager()


@ws_router.websocket("/ws/game")
async def game_websocket(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                # Handle client messages (heartbeat, etc.)
                if msg.get("type") == "ping":
                    await ws.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(ws)
