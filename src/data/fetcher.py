import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import ccxt
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        if api_key and api_secret:
            self.binance_client = Client(api_key, api_secret)
        else:
            self.binance_client = None

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 1000) -> pd.DataFrame:
        """Fetch OHLCV data with error handling and retries."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {str(e)}")
            return pd.DataFrame()

    async def fetch_ticker(self, symbol: str) -> Dict:
        """Fetch current ticker data with error handling."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'change': ticker['percentage'],
                'timestamp': datetime.fromtimestamp(ticker['timestamp'] / 1000)
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}

    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """Fetch order book data with error handling."""
        try:
            order_book = await self.exchange.fetch_order_book(symbol, limit)
            return {
                'symbol': symbol,
                'bids': order_book['bids'],
                'asks': order_book['asks'],
                'timestamp': datetime.fromtimestamp(order_book['timestamp'] / 1000)
            }
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {str(e)}")
            return {}

    def fetch_market_depth(self, symbol: str) -> Dict:
        """Fetch market depth using Binance client if available."""
        if not self.binance_client:
            return {}

        try:
            depth = self.binance_client.get_order_book(symbol=symbol)
            return {
                'symbol': symbol,
                'bids': depth['bids'],
                'asks': depth['asks'],
                'timestamp': datetime.now()
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching market depth for {symbol}: {str(e)}")
            return {}

    async def fetch_all_data(self, symbols: List[str]) -> Dict:
        """Fetch all types of data for multiple symbols."""
        results = {}
        for symbol in symbols:
            results[symbol] = {
                'ohlcv': await self.fetch_ohlcv(symbol),
                'ticker': await self.fetch_ticker(symbol),
                'order_book': await self.fetch_order_book(symbol),
                'market_depth': self.fetch_market_depth(symbol)
            }
        return results