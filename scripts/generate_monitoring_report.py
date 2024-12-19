from datetime import datetime
from pathlib import Path
from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.report_generator import MonitoringReportGenerator

def main():
    metrics = MetricsCollector()
    generator = MonitoringReportGenerator()
    
    # Load metrics
    try:
        metrics_files = sorted(Path('metrics').glob('metrics_*.json'))
        if metrics_files:
            metrics.load_metrics(str(metrics_files[-1]))
    except Exception as e:
        print(f"Error loading metrics: {str(e)}")
        return
    
    # Generate report
    try:
        generator.generate_report(metrics)
        print("Monitoring report generated successfully")
    except Exception as e:
        print(f"Error generating report: {str(e)}")

if __name__ == '__main__':
    main()