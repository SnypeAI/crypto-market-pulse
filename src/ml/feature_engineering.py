import pandas as pd
import numpy as np
from typing import Dict, List

class FeatureEngineer:
    def __init__(self):
        self.technical_features = [
            'rsi',
            'macd',
            'bollinger_bands',
            'atr',
            'volume_profile'
        ]
        self.sentiment_features = [
            'social_score',
            'news_sentiment',
            'market_fear'
        ]
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # Add technical indicators
        df = self.add_technical_indicators(df)
        
        # Add time-based features
        df = self.add_temporal_features(df)
        
        # Add market regime features
        df = self.add_market_regime(df)
        
        return df
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'])
        
        # MACD
        macd_data = self.calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        
        # Bollinger Bands
        bb = self.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb['upper']
        df['bb_lower'] = bb['lower']
        df['bb_middle'] = bb['middle']
        
        return df
    
    def add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df['hour'] = pd.to_datetime(df.index).hour
        df['day_of_week'] = pd.to_datetime(df.index).dayofweek
        df['month'] = pd.to_datetime(df.index).month
        
        return df
    
    def add_market_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        # Volatility regime
        df['volatility'] = df['close'].pct_change().rolling(window=20).std()
        
        # Trend regime
        df['trend'] = np.where(
            df['close'] > df['close'].rolling(window=50).mean(),
            1,  # Uptrend
            -1  # Downtrend
        )
        
        return df
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, pd.Series]:
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': macd - signal
        }
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        window: int = 20,
        num_std: float = 2
    ) -> Dict[str, pd.Series]:
        middle = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        
        return {
            'upper': middle + (std * num_std),
            'lower': middle - (std * num_std),
            'middle': middle
        }