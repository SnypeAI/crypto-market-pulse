import asyncio
import json
from typing import Callable, Dict

import websockets


class WebSocketClient:
    def __init__(self):
        self.connections: Dict[str, websockets.WebSocketClientProtocol] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.running = False

    async def connect(self, url: str, symbol: str):
        try:
            websocket = await websockets.connect(url)
            self.connections[symbol] = websocket
            return True
        except Exception as e:
            print(f"Connection error for {symbol}: {str(e)}")
            return False

    async def subscribe(self, symbol: str, channel: str):
        if symbol in self.connections:
            subscription = {
                "method": "SUBSCRIBE",
                "params": [f"{symbol}@{channel}"],
                "id": 1,
            }
            await self.connections[symbol].send(json.dumps(subscription))

    def add_callback(self, symbol: str, callback: Callable):
        self.callbacks[symbol] = callback

    async def start(self):
        self.running = True
        tasks = [self.listen(symbol) for symbol in self.connections]
        await asyncio.gather(*tasks)

    async def listen(self, symbol: str):
        while self.running:
            try:
                if symbol in self.connections:
                    message = await self.connections[symbol].recv()
                    data = json.loads(message)

                    if symbol in self.callbacks:
                        await self.callbacks[symbol](data)
            except Exception as e:
                print(f"Error in listener for {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Retry delay

    async def stop(self):
        self.running = False
        for symbol, conn in self.connections.items():
            await conn.close()
        self.connections.clear()
