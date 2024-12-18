import numpy as np
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import json

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'predictions': [],
            'accuracy': {},
            'model_drift': {},
            'feature_importance': {}
        }
        self.threshold_alerts = {
            'accuracy': 0.95,  # 95% accuracy required
            'drift': 0.05,     # 5% drift tolerance
            'confidence': 0.8   # 80% minimum confidence
        }
    
    def record_prediction(self, symbol: str, prediction: Dict):
        timestamp = datetime.now().isoformat()
        
        self.metrics['predictions'].append({
            'symbol': symbol,
            'timestamp': timestamp,
            'predicted': prediction['price'],
            'confidence': prediction['confidence'],
            'model_version': prediction.get('model_version', '1.0.0')
        })
    
    def update_accuracy(self, symbol: str, actual: float, predicted: float):
        error = abs(actual - predicted) / actual
        
        if symbol not in self.metrics['accuracy']:
            self.metrics['accuracy'][symbol] = []
        
        self.metrics['accuracy'][symbol].append({
            'timestamp': datetime.now().isoformat(),
            'error': float(error),
            'actual': float(actual),
            'predicted': float(predicted)
        })
    
    def check_model_drift(self, symbol: str, recent_predictions: List[Dict]) -> bool:
        if not recent_predictions:
            return False
        
        errors = [abs(p['actual'] - p['predicted']) / p['actual'] 
                 for p in recent_predictions]
        
        avg_error = np.mean(errors)
        drift_detected = avg_error > self.threshold_alerts['drift']
        
        self.metrics['model_drift'][symbol] = {
            'timestamp': datetime.now().isoformat(),
            'average_error': float(avg_error),
            'drift_detected': drift_detected
        }
        
        return drift_detected
    
    def save_metrics(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        metrics_dir = Path('metrics')
        metrics_dir.mkdir(exist_ok=True)
        
        with open(metrics_dir / f'metrics_{timestamp}.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)