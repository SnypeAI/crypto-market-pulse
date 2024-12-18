from datetime import datetime, timedelta

class SentimentAggregator:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.timeframes = ['1h', '4h', '12h', '24h']
    
    def aggregate_sentiment(self, data_sources):
        results = {}
        for timeframe in self.timeframes:
            filtered_data = self._filter_by_timeframe(data_sources, timeframe)
            results[timeframe] = self.analyzer.get_sentiment_summary(filtered_data)
        return results
    
    def _filter_by_timeframe(self, data, timeframe):
        now = datetime.now()
        hours = int(timeframe.replace('h', ''))
        threshold = now - timedelta(hours=hours)
        
        return [d for d in data if d['timestamp'] > threshold]
    
    def get_trend_analysis(self, aggregated_data):
        trends = {}
        for timeframe, data in aggregated_data.items():
            trends[timeframe] = {
                'direction': 'bullish' if data['overall_sentiment'] > 0.1 else 'bearish' if data['overall_sentiment'] < -0.1 else 'neutral',
                'strength': abs(data['overall_sentiment']),
                'confidence': 1 - data['average_subjectivity']
            }
        return trends