import pandas as pd


class FeatureEngineer:
    def __init__(self):
        self.technical_features = [
            "rsi",
            "macd",
            "bollinger_bands",
            "atr",
            "volume_profile",
        ]

    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        # Add technical indicators
        df = self.add_technical_indicators(df)

        # Add temporal features
        df = self.add_temporal_features(df)

        # Add market regime features
        df = self.add_market_regime(df)

        return df