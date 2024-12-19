from datetime import datetime, timedelta
from typing import Dict, List

import ccxt
import pandas as pd


class CryptoDataFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 1000) -> pd.DataFrame:
        """Fetch OHLCV data for a symbol."""
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

    async def fetch_multiple_symbols(self, symbols: List[str], timeframe: str = '1h') -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols."""
        results = {}
        for symbol in symbols:
            results[symbol] = await self.fetch_ohlcv(symbol, timeframe)
        return results