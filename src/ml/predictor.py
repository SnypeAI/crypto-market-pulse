import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from typing import Dict, List, Tuple, Optional

class MarketPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.lstm_model = self._build_lstm()
        self.lookback = 60  # 60 minutes of historical data
        self.prediction_horizon = 24  # Predict 24 hours ahead

    def _build_lstm(self) -> Sequential:
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.lookback, 5)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(self.prediction_horizon)
        ])
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        return model

    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        features = np.column_stack([
            data['close'],
            data['volume'],
            data['rsi'],
            data['macd'],
            data['atr']
        ])

        scaled_features = self.scaler.fit_transform(features)
        X, y = [], []

        for i in range(len(data) - self.lookback - self.prediction_horizon + 1):
            X.append(scaled_features[i:i+self.lookback])
            y.append(scaled_features[i+self.lookback:i+self.lookback+self.prediction_horizon, 0])

        return np.array(X), np.array(y)

    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        # Train LSTM
        lstm_history = self.lstm_model.fit(
            X, y,
            epochs=50,
            batch_size=32,
            validation_split=0.1,
            verbose=0
        )

        # Train Random Forest
        X_rf = X.reshape(X.shape[0], -1)
        y_rf = y[:, 0]  # Use only first prediction point for RF
        self.rf_model.fit(X_rf, y_rf)

        return {
            'lstm_loss': lstm_history.history['loss'][-1],
            'lstm_val_loss': lstm_history.history['val_loss'][-1],
            'rf_score': self.rf_model.score(X_rf, y_rf)
        }

    def predict(self, data: pd.DataFrame) -> Dict:
        X, _ = self.prepare_data(data.iloc[-self.lookback:])
        if X.size == 0:
            raise ValueError("Insufficient data for prediction")

        # Get predictions from both models
        lstm_pred = self.lstm_model.predict(X[-1:], verbose=0)
        rf_pred = self.rf_model.predict(X[-1:].reshape(1, -1))

        # Inverse transform predictions
        lstm_pred_scaled = np.zeros((1, features.shape[1]))
        lstm_pred_scaled[:, 0] = lstm_pred[0, 0]
        rf_pred_scaled = np.zeros((1, features.shape[1]))
        rf_pred_scaled[:, 0] = rf_pred[0]

        lstm_price = self.scaler.inverse_transform(lstm_pred_scaled)[0, 0]
        rf_price = self.scaler.inverse_transform(rf_pred_scaled)[0, 0]

        # Ensemble prediction (weighted average)
        final_price = 0.6 * lstm_price + 0.4 * rf_price

        # Calculate confidence metrics
        lstm_conf = self._calculate_lstm_confidence(lstm_pred)
        rf_conf = self._calculate_rf_confidence(rf_pred)

        return {
            'price': final_price,
            'confidence': 0.6 * lstm_conf + 0.4 * rf_conf,
            'horizon': f"{self.prediction_horizon}h",
            'predictions': {
                'lstm': lstm_price,
                'rf': rf_price
            },
            'confidence_scores': {
                'lstm': lstm_conf,
                'rf': rf_conf
            }
        }

    def _calculate_lstm_confidence(self, pred: np.ndarray) -> float:
        # Calculate confidence based on prediction variance
        return float(1.0 / (1.0 + np.std(pred)))

    def _calculate_rf_confidence(self, pred: float) -> float:
        # Use RF's internal uncertainty estimation
        return float(1.0 - self.rf_model.predict_proba(X_rf)[:, 1].std())

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        lstm_pred = self.lstm_model.predict(X)
        rf_pred = self.rf_model.predict(X.reshape(X.shape[0], -1))

        metrics = {
            'lstm_mse': float(np.mean((lstm_pred[:, 0] - y[:, 0]) ** 2)),
            'lstm_mae': float(np.mean(np.abs(lstm_pred[:, 0] - y[:, 0]))),
            'rf_mse': float(np.mean((rf_pred - y[:, 0]) ** 2)),
            'rf_mae': float(np.mean(np.abs(rf_pred - y[:, 0])))
        }

        return metrics