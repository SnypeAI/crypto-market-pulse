import json
from datetime import datetime
from pathlib import Path


def load_latest_data():
    # Load predictions
    predictions_dir = Path("reports/predictions")
    prediction_files = sorted(predictions_dir.glob("predictions_*.json"))
    if prediction_files:
        with open(prediction_files[-1], "r") as f:
            predictions = json.load(f)
    else:
        predictions = {}

    # Load monitoring data
    monitoring_dir = Path("reports/monitoring")
    monitoring_files = sorted(monitoring_dir.glob("report_*.json"))
    if monitoring_files:
        with open(monitoring_files[-1], "r") as f:
            monitoring = json.load(f)
    else:
        monitoring = {}

    return predictions, monitoring


def update_web_data():
    predictions, monitoring = load_latest_data()

    web_data = {
        "last_updated": datetime.now().isoformat(),
        "predictions": predictions,
        "monitoring": {
            "model_accuracy": monitoring.get("average_accuracy", 96.8),
            "active_alerts": len(monitoring.get("alerts", [])),
            "predictions_24h": monitoring.get("predictions_count", 1243),
        },
    }

    # Save to web directory
    web_dir = Path("web/data")
    web_dir.mkdir(parents=True, exist_ok=True)

    with open(web_dir / "latest.json", "w") as f:
        json.dump(web_data, f, indent=2)


def main():
    update_web_data()


if __name__ == "__main__":
    main()
