import asyncio
from typing import Dict, List
from datetime import datetime
from .websocket_client import WebSocketClient
from .data_processor import DataProcessor

class MarketMonitor:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.client = WebSocketClient()
        self.processor = DataProcessor()
        self.alerts = []

    async def start_monitoring(self):
        # Connect to WebSocket for each symbol
        for symbol in self.symbols:
            success = await self.client.connect(
                f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade",
                symbol
            )
            if success:
                await self.client.subscribe(symbol, 'trade')
                self.client.add_callback(symbol, self.handle_message)

        await self.client.start()

    async def handle_message(self, message: Dict):
        try:
            symbol = message.get('s')
            if symbol:
                self.processor.process_trade(symbol, message)
                await self.check_alerts(symbol)
        except Exception as e:
            print(f"Error processing message: {str(e)}")

    async def check_alerts(self, symbol: str):
        price = self.processor.get_latest_price(symbol)
        timestamp = datetime.now()

        # Example alert conditions
        if price > 0:
            last_prices = self.processor.get_price_history(symbol)[-5:]
            if len(last_prices) >= 5:
                avg_price = sum(p['price'] for p in last_prices) / len(last_prices)
                if price > avg_price * 1.02:  # 2% spike
                    self.alerts.append({
                        'symbol': symbol,
                        'type': 'PRICE_SPIKE',
                        'price': price,
                        'timestamp': timestamp
                    })

    async def stop_monitoring(self):
        await self.client.stop()