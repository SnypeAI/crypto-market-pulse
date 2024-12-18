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
    
    def generate_report(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        report_path = self.reports_dir / f'report_{timestamp}.md'
        
        self.load_data()
        plots_dir = self.reports_dir / f'plots_{timestamp}'
        plots_dir.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write('# Model Performance Report\n\n')
            f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n\n')
            
            self._write_performance_summary(f)
            self._write_alerts_summary(f)
            self._write_drift_analysis(f)
            
            self._generate_visualizations(plots_dir)
    
    def _write_performance_summary(self, f):
        f.write('## Performance Summary\n\n')
        f.write('| Symbol | Accuracy | Predictions | Alerts |\n')
        f.write('|--------|-----------|-------------|---------|\n')
        
        for symbol in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']:
            accuracy = self._get_symbol_accuracy(symbol)
            predictions = len([p for p in self.metrics['predictions'] if p['symbol'] == symbol])
            alerts = len([a for a in self.alerts if a['symbol'] == symbol])
            
            f.write(f'| {symbol} | {accuracy:.2%} | {predictions} | {alerts} |\n')
    
    def _write_alerts_summary(self, f):
        f.write('\n## Recent Alerts\n\n')
        recent_alerts = self.alerts[-10:]  # Last 10 alerts
        
        for alert in recent_alerts:
            f.write(f"- **{alert['type']}** ({alert['symbol']}): {alert['message']}\n")
    
    def _write_drift_analysis(self, f):
        f.write('\n## Model Drift Analysis\n\n')
        for symbol in self.metrics['model_drift']:
            drift = self.metrics['model_drift'][symbol]
            f.write(f"### {symbol}\n")
            f.write(f"- Average Error: {drift['average_error']:.2%}\n")
            f.write(f"- Drift Detected: {drift['drift_detected']}\n\n")
    
    def _generate_visualizations(self, plots_dir):
        self._plot_accuracy_trend(plots_dir)
        self._plot_alert_distribution(plots_dir)
        self._plot_drift_heatmap(plots_dir)
    
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