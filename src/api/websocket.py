from fastapi import WebSocket
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            'market': set(),
            'technical': set(),
            'performance': set(),
            'all': set()
        }

    async def connect(self, websocket: WebSocket, channel: str = 'all'):
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = 'all'):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

    async def broadcast(self, message: dict, channel: str = 'all'):
        if channel in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    dead_connections.add(connection)
                    print(f"Error broadcasting message: {str(e)}")
            
            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead, channel)

manager = ConnectionManager()