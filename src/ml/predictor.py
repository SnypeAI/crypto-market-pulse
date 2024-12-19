import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential


class MarketPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.lstm_model = self._build_lstm()

    def _build_lstm(self):
        model = Sequential(
            [
                LSTM(50, return_sequences=True, input_shape=(60, 5)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model

    def prepare_data(self, data, lookback=60):
        features = np.column_stack(
            [data["close"], data["volume"], data["rsi"], data["macd"], data["atr"]]
        )

        scaled_features = self.scaler.fit_transform(features)

        X, y = [], []
        for i in range(len(data) - lookback):
            X.append(scaled_features[i:i + lookback])
            y.append(scaled_features[i + lookback, 0])

        return np.array(X), np.array(y)

    def train(self, data):
        X, y = self.prepare_data(data)

        # Train LSTM
        self.lstm_model.fit(
            X, y, epochs=50, batch_size=32, validation_split=0.1, verbose=0
        )

        # Train Random Forest
        X_rf = X.reshape(X.shape[0], -1)
        self.rf_model.fit(X_rf, y)

    def predict(self, data):
        X, _ = self.prepare_data(data)

        # Get predictions from both models
        lstm_pred = self.lstm_model.predict(X[-1:])
        rf_pred = self.rf_model.predict(X[-1:].reshape(1, -1))

        # Ensemble prediction (weighted average)
        prediction = 0.6 * lstm_pred + 0.4 * rf_pred

        # Inverse transform
        original_scale = self.scaler.inverse_transform(
            np.hstack([prediction, np.zeros((1, 4))])
        )

        return {
            "price": original_scale[0, 0],
            "lstm_confidence": self._calculate_confidence(lstm_pred),
            "rf_confidence": self._calculate_confidence(rf_pred),
        }

    def _calculate_confidence(self, prediction):
        # Calculate confidence based on model's recent performance
        return 0.85  # Placeholder for now