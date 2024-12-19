import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.api.websocket import broadcast_updates
from src.data.fetcher import CryptoDataFetcher
from src.db.database import SessionLocal
from src.db.models import CryptoPrice, TechnicalIndicators
from src.ml.feature_engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimePipeline:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.fetcher = CryptoDataFetcher(api_key, api_secret)
        self.predictor = MarketPredictor()
        self.feature_engineer = FeatureEngineer()
        self.symbols = [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT",
            "XRP/USDT",
            "SOL/USDT",
            "ADA/USDT",
            "DOGE/USDT",
            "AVAX/USDT",
        ]
        self.last_update = {}
        self.running = False

    async def start(self):
        """Start the realtime pipeline."""
        self.running = True
        while self.running:
            try:
                await self.process_update()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in realtime pipeline: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop the realtime pipeline."""
        self.running = False

    async def process_update(self):
        """Process a single update cycle."""
        # Fetch all data
        data = await self.fetcher.fetch_all_data(self.symbols)

        # Process each symbol
        updates = {}
        for symbol, symbol_data in data.items():
            if symbol_data["ohlcv"].empty:
                continue

            # Add technical indicators
            df = self.feature_engineer.add_technical_indicators(symbol_data["ohlcv"])

            # Store in database
            with SessionLocal() as db:
                self._store_data(db, symbol, df)

            # Generate predictions
            try:
                prediction = self.predictor.predict(df)
                latest_price = float(symbol_data["ticker"]["last"])
                updates[symbol] = {
                    "price": latest_price,
                    "volume": float(symbol_data["ticker"]["volume"]),
                    "change": float(symbol_data["ticker"]["change"]),
                    "prediction": prediction,
                    "technical": {
                        "rsi": float(df["rsi"].iloc[-1]),
                        "macd": float(df["macd"].iloc[-1]),
                        "bb_upper": float(df["bb_high"].iloc[-1]),
                        "bb_lower": float(df["bb_low"].iloc[-1]),
                        "atr": float(df["atr"].iloc[-1]),
                    },
                    "market_depth": {
                        "bids": symbol_data["market_depth"].get("bids", [])[:5],
                        "asks": symbol_data["market_depth"].get("asks", [])[:5],
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.error(f"Error generating prediction for {symbol}: {str(e)}")

        # Broadcast updates
        if updates:
            await broadcast_updates(
                {
                    "type": "market_update",
                    "data": updates,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def _store_data(self, db, symbol: str, df):
        """Store data in the database."""
        try:
            latest = df.iloc[-1]
            price = CryptoPrice(
                symbol=symbol,
                timestamp=latest.name,
                open=float(latest["open"]),
                high=float(latest["high"]),
                low=float(latest["low"]),
                close=float(latest["close"]),
                volume=float(latest["volume"]),
            )
            db.add(price)
            db.flush()

            # Store technical indicators
            indicators = TechnicalIndicators(
                price_id=price.id,
                rsi=float(latest["rsi"]),
                macd=float(latest["macd"]),
                macd_signal=float(latest["macd_signal"]),
                macd_hist=float(latest["macd_diff"]),
                bb_upper=float(latest["bb_high"]),
                bb_middle=float(latest["bb_mid"]),
                bb_lower=float(latest["bb_low"]),
                atr=float(latest["atr"]),
            )
            db.add(indicators)
            db.commit()

        except Exception as e:
            logger.error(f"Error storing data for {symbol}: {str(e)}")
            db.rollback()
