import pytest
from datetime import datetime, timedelta
from src.utils.sentiment_enhanced import EnhancedSentimentAnalyzer
from src.utils.sentiment_aggregator import SentimentAggregator

@pytest.fixture
def sample_texts():
    return [
        'Bitcoin is looking very bullish today!',
        'Market sentiment is bearish after the recent dump',
        'Holding strong, time to hodl',
        'Normal market conditions today'
    ]

@pytest.fixture
def sample_data_sources():
    now = datetime.now()
    return [
        {'text': 'Bullish market!', 'timestamp': now - timedelta(hours=1)},
        {'text': 'Bearish signals', 'timestamp': now - timedelta(hours=6)},
        {'text': 'Strong uptrend', 'timestamp': now - timedelta(hours=12)}
    ]

def test_sentiment_analysis(sample_texts):
    analyzer = EnhancedSentimentAnalyzer()
    results = analyzer.analyze_batch(sample_texts)
    
    assert len(results) == len(sample_texts)
    assert all('compound' in r for r in results)
    assert all('custom_score' in r for r in results)

def test_custom_terms():
    analyzer = EnhancedSentimentAnalyzer()
    result = analyzer.analyze_text('Very bullish on Bitcoin')
    assert result['custom_score'] > 0
    
    result = analyzer.analyze_text('Market looking bearish')
    assert result['custom_score'] < 0

def test_sentiment_aggregation(sample_data_sources):
    analyzer = EnhancedSentimentAnalyzer()
    aggregator = SentimentAggregator(analyzer)
    
    results = aggregator.aggregate_sentiment(sample_data_sources)
    
    assert '1h' in results
    assert '24h' in results
    assert all('overall_sentiment' in data for data in results.values())

def test_trend_analysis(sample_data_sources):
    analyzer = EnhancedSentimentAnalyzer()
    aggregator = SentimentAggregator(analyzer)
    
    aggregated_data = aggregator.aggregate_sentiment(sample_data_sources)
    trends = aggregator.get_trend_analysis(aggregated_data)
    
    assert all(timeframe in trends for timeframe in ['1h', '4h', '12h', '24h'])
    assert all('direction' in data for data in trends.values())
    assert all('strength' in data for data in trends.values())
    assert all('confidence' in data for data in trends.values())