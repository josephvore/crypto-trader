from __future__ import annotations

from typing import Any

from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active.discard(websocket)

    async def broadcast(self, event: str, payload: dict[str, Any]) -> None:
        data = {"event": event, "payload": payload}
        to_remove: list[WebSocket] = []
        for ws in list(self.active):
            try:
                await ws.send_json(data)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.active.discard(ws)
