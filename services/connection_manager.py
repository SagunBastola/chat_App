from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        # await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, receiver_id: int) -> bool:
        websocket = self.active_connections.get(receiver_id)
        if websocket:
            await websocket.send_json(message)
            return True
        return False

manager = ConnectionManager()