from collections import defaultdict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[channel_id].add(websocket)

    def disconnect(self, channel_id: int, websocket: WebSocket):
        connections = self.active_connections.get(channel_id)

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            del self.active_connections[channel_id]

    async def broadcast(self, channel_id: int, message: dict):
        connections = self.active_connections.get(channel_id, set())

        for connection in connections.copy():
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(channel_id, connection)


websocket_manager = WebSocketManager()
