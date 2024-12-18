from data_collector import DataCollector
from analyzer import MarketAnalyzer
from reporter import ReportGenerator
from notifier import AlertNotifier

class CryptoAnalysisPipeline:
    def __init__(self):
        self.collector = DataCollector()
        self.analyzer = MarketAnalyzer()
        self.reporter = ReportGenerator()
        self.notifier = AlertNotifier()

    def run(self):
        # Collect data
        market_data = self.collector.fetch_all_data()
        
        # Analyze
        analysis = self.analyzer.analyze(market_data)
        
        # Generate reports
        self.reporter.create_report(analysis)
        
        # Check alerts
        alerts = self.analyzer.check_alerts(analysis)
        if alerts:
            self.notifier.send_alerts(alerts)

def main():
    pipeline = CryptoAnalysisPipeline()
    pipeline.run()

if __name__ == '__main__':
    main()