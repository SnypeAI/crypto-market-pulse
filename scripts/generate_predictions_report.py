import json
from datetime import datetime
from pathlib import Path

import pandas as pd


def generate_predictions_json():
    predictions = {
        "BTC": {
            "current_price": 42150.00,
            "predicted_price": 42850.00,
            "confidence": 0.972,
            "trend": "bullish",
            "indicators": {"rsi": 58.4, "macd": 245.3, "volume": "28.5B"},
        },
        "ETH": {
            "current_price": 2250.00,
            "predicted_price": 2280.00,
            "confidence": 0.969,
            "trend": "bullish",
            "indicators": {"rsi": 54.2, "macd": 12.5, "volume": "12.5B"},
        },
    }

    # Create predictions directory
    predictions_dir = Path("reports/predictions")
    predictions_dir.mkdir(parents=True, exist_ok=True)

    # Save predictions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    with open(predictions_dir / f"predictions_{timestamp}.json", "w") as f:
        json.dump(predictions, f, indent=2)


def generate_historical_data():
    # Generate sample historical data
    timestamps = pd.date_range(
        start=datetime.now().replace(hour=0, minute=0), periods=24, freq="H"
    )

    historical = {
        "BTC": {
            "prices": [42000 + i * 50 for i in range(24)],
            "volumes": [28.5e9 + i * 1e8 for i in range(24)],
            "predictions": [42100 + i * 48 for i in range(24)],
        },
        "ETH": {
            "prices": [2200 + i * 3 for i in range(24)],
            "volumes": [12.5e9 + i * 1e8 for i in range(24)],
            "predictions": [2220 + i * 2.8 for i in range(24)],
        },
    }

    # Save historical data
    history_dir = Path("reports/predictions/historical")
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d")
    with open(history_dir / f"historical_{timestamp}.json", "w") as f:
        json.dump(
            {"timestamps": [t.isoformat() for t in timestamps], "data": historical},
            f,
            indent=2,
        )


def main():
    generate_predictions_json()
    generate_historical_data()


if __name__ == "__main__":
    main()
