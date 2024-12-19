import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
from sklearn.model_selection import train_test_split

from src.db.models import CryptoPrice, TechnicalIndicators
from src.ml.predictor import MarketPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self):
        self.predictor = MarketPredictor()
        self.training_window = 60  # days of data for training
        self.prediction_horizon = 24  # hours to predict ahead

    def prepare_training_data(self, db: Session, symbol: str) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for model training."""
        # Get historical data
        cutoff = datetime.utcnow() - timedelta(days=self.training_window)
        query = db.query(
            CryptoPrice, TechnicalIndicators
        ).join(
            TechnicalIndicators,
            CryptoPrice.id == TechnicalIndicators.price_id
        ).filter(
            CryptoPrice.symbol == symbol,
            CryptoPrice.timestamp >= cutoff
        ).order_by(CryptoPrice.timestamp)

        # Convert to DataFrame
        rows = []
        for price, indicators in query.all():
            row = {
                'timestamp': price.timestamp,
                'open': price.open,
                'high': price.high,
                'low': price.low,
                'close': price.close,
                'volume': price.volume,
                'rsi': indicators.rsi,
                'macd': indicators.macd,
                'macd_signal': indicators.macd_signal,
                'macd_hist': indicators.macd_hist,
                'bb_upper': indicators.bb_upper,
                'bb_middle': indicators.bb_middle,
                'bb_lower': indicators.bb_lower,
                'atr': indicators.atr
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        df.set_index('timestamp', inplace=True)

        # Prepare features and target
        X, y = self.predictor.prepare_data(df)
        return X, y

    def train_model(self, db: Session, symbol: str) -> Dict:
        """Train the model for a specific symbol."""
        try:
            logger.info(f"Starting training for {symbol}")
            
            # Prepare data
            X, y = self.prepare_training_data(db, symbol)
            if len(X) < 100:  # Minimum data requirement
                raise ValueError(f"Insufficient data for {symbol}")

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )

            # Train model
            self.predictor.train(X_train, y_train)

            # Evaluate
            train_metrics = self.predictor.evaluate(X_train, y_train)
            test_metrics = self.predictor.evaluate(X_test, y_test)

            logger.info(f"Training completed for {symbol}")
            return {
                'symbol': symbol,
                'training_time': datetime.utcnow().isoformat(),
                'train_metrics': train_metrics,
                'test_metrics': test_metrics
            }

        except Exception as e:
            logger.error(f"Error training model for {symbol}: {str(e)}")
            raise

    def train_all_models(self, db: Session, symbols: List[str]) -> Dict[str, Dict]:
        """Train models for all specified symbols."""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.train_model(db, symbol)
            except Exception as e:
                logger.error(f"Failed to train model for {symbol}: {str(e)}")
                results[symbol] = {'error': str(e)}
        return results