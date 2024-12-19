import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ModelAlertSystem:
    def __init__(self):
        self.alerts = []
        self.thresholds = {"accuracy": 0.95, "drift": 0.05, "confidence": 0.8}

    def check_accuracy(self, symbol: str, accuracy: float) -> bool:
        if accuracy < self.thresholds["accuracy"]:
            self.create_alert(
                symbol, "ACCURACY", f"Model accuracy below threshold: {accuracy:.2%}"
            )
            return True
        return False

    def check_drift(self, symbol: str, drift: float) -> bool:
        if drift > self.thresholds["drift"]:
            self.create_alert(symbol, "DRIFT", f"Model drift detected: {drift:.2%}")
            return True
        return False

    def check_confidence(self, symbol: str, prediction: Dict) -> bool:
        if prediction["confidence"] < self.thresholds["confidence"]:
            self.create_alert(
                symbol,
                "CONFIDENCE",
                f'Low prediction confidence: {prediction["confidence"]:.2%}',
            )
            return True
        return False

    def create_alert(self, symbol: str, alert_type: str, message: str):
        self.alerts.append(
            {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "type": alert_type,
                "message": message,
            }
        )

    def get_active_alerts(self) -> List[Dict]:
        return self.alerts[-100:]  # Return last 100 alerts

    def save_alerts(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        alerts_dir = Path("alerts")
        alerts_dir.mkdir(exist_ok=True)

        with open(alerts_dir / f"alerts_{timestamp}.json", "w") as f:
            json.dump(self.alerts, f, indent=2)

    def load_alerts(self, file_path: str):
        with open(file_path, "r") as f:
            self.alerts = json.load(f)
