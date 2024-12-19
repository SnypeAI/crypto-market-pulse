from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.custom_terms = {
            'bullish': 2.0,
            'bearish': -2.0,
            'moon': 1.5,
            'dump': -1.5,
            'hodl': 0.5
        }
        self.vader.lexicon.update(self.custom_terms)
    
    def analyze_text(self, text: str) -> Dict:
        blob = TextBlob(text)
        vader_scores = self.vader.polarity_scores(text)
        
        return {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'subjectivity': blob.sentiment.subjectivity,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        return [self.analyze_text(text) for text in texts]
    
    def get_weighted_sentiment(self, texts: List[str], weights: List[float] = None) -> float:
        if not texts:
            return 0.0
        
        if weights is None:
            weights = [1.0] * len(texts)
            
        if len(weights) != len(texts):
            raise ValueError("Number of weights must match number of texts")
        
        sentiments = [self.analyze_text(text)['compound'] for text in texts]
        weighted_sum = sum(s * w for s, w in zip(sentiments, weights))
        return weighted_sum / sum(weights)
    
    def get_sentiment_summary(self, texts: List[str]) -> Dict:
        if not texts:
            return {
                'overall': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 0.0,
                'average_subjectivity': 0.0
            }
        
        analyses = self.analyze_batch(texts)
        
        positive_count = sum(1 for a in analyses if a['compound'] > 0.05)
        negative_count = sum(1 for a in analyses if a['compound'] < -0.05)
        neutral_count = sum(1 for a in analyses if abs(a['compound']) <= 0.05)
        
        total = len(analyses)
        
        return {
            'overall': sum(a['compound'] for a in analyses) / total,
            'positive_ratio': positive_count / total,
            'negative_ratio': negative_count / total,
            'neutral_ratio': neutral_count / total,
            'average_subjectivity': sum(a['subjectivity'] for a in analyses) / total,
            'timestamp': datetime.now().isoformat()
        }