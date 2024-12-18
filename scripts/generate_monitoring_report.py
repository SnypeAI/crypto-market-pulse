import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class MonitoringReportGenerator:
    def __init__(self):
        self.metrics_dir = Path('metrics')
        self.alerts_dir = Path('alerts')
        self.reports_dir = Path('reports/monitoring')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self):
        # Load latest metrics
        metrics_files = sorted(self.metrics_dir.glob('metrics_*.json'))[-1]
        with open(metrics_files, 'r') as f:
            self.metrics = json.load(f)
        
        # Load latest alerts
        alerts_files = sorted(self.alerts_dir.glob('alerts_*.json'))[-1]
        with open(alerts_files, 'r') as f:
            self.alerts = json.load(f)
    
    def _plot_accuracy_trend(self, plots_dir):
        plt.figure(figsize=(12, 6))
        for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']:
            if symbol in self.metrics['accuracy']:
                accuracies = [1 - d['error'] for d in self.metrics['accuracy'][symbol]]
                plt.plot(accuracies, label=symbol)
        
        plt.title('Model Accuracy Trend')
        plt.xlabel('Predictions')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        plt.savefig(plots_dir / 'accuracy_trend.png')
        plt.close()
    
    def _plot_alert_distribution(self, plots_dir):
        alert_types = [alert['type'] for alert in self.alerts]
        plt.figure(figsize=(10, 6))
        sns.countplot(x=alert_types)
        plt.title('Alert Distribution by Type')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / 'alert_distribution.png')
        plt.close()
    
    def _plot_drift_heatmap(self, plots_dir):
        drift_data = {}
        for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']:
            if symbol in self.metrics['model_drift']:
                drift_data[symbol] = self.metrics['model_drift'][symbol]['average_error']
        
        plt.figure(figsize=(8, 2))
        sns.heatmap(
            pd.DataFrame([drift_data]).T,
            cmap='RdYlGn_r',
            annot=True,
            fmt='.2%'
        )
        plt.title('Model Drift Heatmap')
        plt.tight_layout()
        plt.savefig(plots_dir / 'drift_heatmap.png')
        plt.close()
    
    def _get_symbol_accuracy(self, symbol):
        if symbol in self.metrics['accuracy']:
            recent_errors = [d['error'] for d in self.metrics['accuracy'][symbol][-100:]]
            return 1 - sum(recent_errors) / len(recent_errors)
        return 0.0

def main():
    generator = MonitoringReportGenerator()
    generator.load_data()
    generator.generate_report()

if __name__ == '__main__':
    main()