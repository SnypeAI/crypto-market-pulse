from typing import Dict

import numpy as np
import pandas as pd
import ta


class FeatureEngineer:
    def __init__(self):
        self.technical_features = [
            "rsi",
            "macd",
            "bollinger_bands",
            "atr",
            "volume_profile",
        ]

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe."""
        df = self._add_rsi(df)
        df = self._add_macd(df)
        df = self._add_bollinger_bands(df)
        df = self._add_atr(df)
        return df

    def _add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=period).rsi()
        return df

    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        macd = ta.trend.MACD(
            close=df["close"], window_slow=26, window_fast=12, window_sign=9
        )
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_diff"] = macd.macd_diff()
        return df

    def _add_bollinger_bands(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        bollinger = ta.volatility.BollingerBands(close=df["close"], window=window)
        df["bb_high"] = bollinger.bollinger_hband()
        df["bb_mid"] = bollinger.bollinger_mavg()
        df["bb_low"] = bollinger.bollinger_lband()
        return df

    def _add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        df["atr"] = ta.volatility.AverageTrueRange(
            high=df["high"], low=df["low"], close=df["close"], window=period
        ).average_true_range()
        return df

    def add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        df["hour"] = df.index.hour
        df["day_of_week"] = df.index.dayofweek
        df["month"] = df.index.month
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        return df

    def add_market_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market regime classification."""
        # Volatility-based regime classification
        volatility = df["close"].pct_change().rolling(window=30).std()
        df["volatility_regime"] = pd.qcut(
            volatility, q=3, labels=["low", "medium", "high"]
        )

        # Trend based on SMA
        df["sma_50"] = df["close"].rolling(window=50).mean()
        df["trend_regime"] = np.where(
            df["close"] > df["sma_50"], "uptrend", "downtrend"
        )

        return df
