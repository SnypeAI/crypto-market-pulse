import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from src.data.fetcher import CryptoDataFetcher
from src.db.models import CryptoPrice, TechnicalIndicators
from src.ml.feature_engineering import FeatureEngineer
from src.db.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self):
        self.fetcher = CryptoDataFetcher()
        self.engineer = FeatureEngineer()
        self.symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT',
            'SOL/USDT', 'ADA/USDT', 'DOGE/USDT', 'AVAX/USDT'
        ]

    async def update_market_data(self):
        """Fetch and store latest market data for all symbols."""
        try:
            data = await self.fetcher.fetch_multiple_symbols(self.symbols)
            with SessionLocal() as db:
                for symbol, df in data.items():
                    if df.empty:
                        logger.warning(f"No data received for {symbol}")
                        continue

                    # Add technical indicators
                    df = self.engineer.add_technical_indicators(df)
                    
                    # Store price data
                    for index, row in df.iterrows():
                        price = CryptoPrice(
                            symbol=symbol,
                            timestamp=index,
                            open=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=row['volume']
                        )
                        db.add(price)
                        db.flush()  # Get the price_id

                        # Store technical indicators
                        indicators = TechnicalIndicators(
                            price_id=price.id,
                            rsi=row['rsi'],
                            macd=row['macd'],
                            macd_signal=row['macd_signal'],
                            macd_hist=row['macd_diff'],
                            bb_upper=row['bb_high'],
                            bb_middle=row['bb_mid'],
                            bb_lower=row['bb_low'],
                            atr=row['atr']
                        )
                        db.add(indicators)

                    db.commit()
                    logger.info(f"Updated data for {symbol}")

        except Exception as e:
            logger.error(f"Error in update_market_data: {str(e)}")
            raise

    async def run_continuous_updates(self, interval_minutes: int = 5):
        """Continuously update market data at specified intervals."""
        while True:
            try:
                await self.update_market_data()
                logger.info(f"Waiting {interval_minutes} minutes until next update")
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"Error in continuous updates: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    @staticmethod
    def get_latest_data(db: Session, symbol: str, limit: int = 1000) -> List[CryptoPrice]:
        """Get the latest data for a symbol from the database."""
        return db.query(CryptoPrice).filter(
            CryptoPrice.symbol == symbol
        ).order_by(
            CryptoPrice.timestamp.desc()
        ).limit(limit).all()

    @staticmethod
    async def cleanup_old_data(db: Session, days: int = 30):
        """Remove data older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        db.query(CryptoPrice).filter(
            CryptoPrice.timestamp < cutoff
        ).delete()
        db.commit()