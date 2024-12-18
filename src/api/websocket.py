from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

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
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead, channel)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket, channel: str = 'all'):
    await manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get('type') == 'heartbeat':
                    await websocket.send_json({'type': 'heartbeat', 'status': 'ok'})
                else:
                    # Handle other message types
                    await handle_message(websocket, message, channel)
            except json.JSONDecodeError:
                await websocket.send_json({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)

async def handle_message(websocket: WebSocket, message: dict, channel: str):
    # Handle different message types
    message_type = message.get('type')
    
    if message_type == 'subscribe':
        # Handle subscription request
        new_channel = message.get('channel')
        if new_channel in manager.active_connections:
            manager.disconnect(websocket, channel)
            await manager.connect(websocket, new_channel)
            await websocket.send_json({
                'type': 'subscribed',
                'channel': new_channel
            })
    
    elif message_type == 'unsubscribe':
        # Handle unsubscribe request
        manager.disconnect(websocket, channel)
        await manager.connect(websocket, 'all')
        await websocket.send_json({
            'type': 'unsubscribed',
            'channel': channel
        })

async def broadcast_updates(interval: int = 1):
    """Background task to broadcast updates to connected clients"""
    while True:
        try:
            # Get market data
            market_data = get_market_data()
            await manager.broadcast({
                'type': 'market',
                'data': market_data
            }, 'market')

            # Get technical data
            technical_data = get_technical_data()
            await manager.broadcast({
                'type': 'technical',
                'data': technical_data
            }, 'technical')

            # Get performance data
            performance_data = get_performance_data()
            await manager.broadcast({
                'type': 'performance',
                'data': performance_data
            }, 'performance')

        except Exception as e:
            print(f"Error in broadcast_updates: {str(e)}")

        await asyncio.sleep(interval)

def get_market_data():
    # Implement market data gathering
    return {}

def get_technical_data():
    # Implement technical data gathering
    return {}

def get_performance_data():
    # Implement performance data gathering
    return {}
