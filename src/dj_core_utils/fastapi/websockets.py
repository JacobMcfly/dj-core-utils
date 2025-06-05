from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, message: dict):
        for connection in self.connections:
            await connection.send_json(message)


manager = WebSocketManager()
