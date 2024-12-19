import asyncio
import json
from typing import Dict, Set, Optional
from datetime import datetime

from fastapi import WebSocket
from src.pipeline.realtime import RealtimePipeline

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "market": set(),
            "technical": set(),
            "predictions": set(),
            "all": set()
        }
        self.last_messages: Dict[str, dict] = {}
        self.pipeline: Optional[RealtimePipeline] = None

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel in self.active_connections:
            self.active_connections[channel].add(websocket)
            if channel in self.last_messages:
                await websocket.send_json(self.last_messages[channel])

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

    async def broadcast(self, message: dict, channel: str = "all"):
        if channel not in self.active_connections:
            return

        # Store last message
        self.last_messages[channel] = message

        # Send to all connected clients
        dead_connections = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                dead_connections.add(connection)
                print(f"Error broadcasting to client: {str(e)}")

        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead, channel)

    def start_pipeline(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Start the realtime data pipeline."""
        if not self.pipeline:
            self.pipeline = RealtimePipeline(api_key, api_secret)
            asyncio.create_task(self.pipeline.start())

    def stop_pipeline(self):
        """Stop the realtime data pipeline."""
        if self.pipeline:
            self.pipeline.stop()
            self.pipeline = None

manager = ConnectionManager()

async def connect_client(websocket: WebSocket, channel: str = "all"):
    await manager.connect(websocket, channel)
    try:
        while True:
            try:
                # Wait for client messages (if any)
                data = await websocket.receive_json()
                # Handle client messages if needed
            except Exception as e:
                print(f"Error receiving message: {str(e)}")
                break
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket, channel)

async def broadcast_updates(message: dict, channel: str = "all"):
    """Broadcast updates to all connected clients."""
    await manager.broadcast(message, channel)

def start_realtime_updates(api_key: Optional[str] = None, api_secret: Optional[str] = None):
    """Start the realtime update pipeline."""
    manager.start_pipeline(api_key, api_secret)

def stop_realtime_updates():
    """Stop the realtime update pipeline."""
    manager.stop_pipeline()