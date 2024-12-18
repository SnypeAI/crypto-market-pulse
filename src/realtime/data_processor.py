from typing import Dict, List
from datetime import datetime
from collections import deque

class DataProcessor:
    def __init__(self, max_data_points: int = 1000):
        self.price_data: Dict[str, deque] = {}
        self.volume_data: Dict[str, deque] = {}
        self.order_book: Dict[str, Dict] = {}
        self.max_data_points = max_data_points

    def process_trade(self, symbol: str, data: Dict):
        if symbol not in self.price_data:
            self.price_data[symbol] = deque(maxlen=self.max_data_points)
            self.volume_data[symbol] = deque(maxlen=self.max_data_points)

        self.price_data[symbol].append({
            'timestamp': datetime.now(),
            'price': float(data['p']),
            'volume': float(data['q'])
        })

    def process_order_book(self, symbol: str, data: Dict):
        self.order_book[symbol] = {
            'bids': data['bids'],
            'asks': data['asks'],
            'timestamp': datetime.now()
        }

    def get_latest_price(self, symbol: str) -> float:
        if symbol in self.price_data and self.price_data[symbol]:
            return self.price_data[symbol][-1]['price']
        return 0.0

    def get_price_history(self, symbol: str) -> List[Dict]:
        if symbol in self.price_data:
            return list(self.price_data[symbol])
        return []

    def get_order_book(self, symbol: str) -> Dict:
        return self.order_book.get(symbol, {})