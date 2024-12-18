from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict

class EnhancedSentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.custom_terms = {
            'bullish': 2.0,
            'bearish': -2.0,
            'moon': 1.5,
            'dump': -1.5,
            'hodl': 0.5
        }
        
    def analyze_text(self, text):
        # Combine VADER and TextBlob analysis
        vader_scores = self.vader.polarity_scores(text)
        blob = TextBlob(text)
        
        return {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'subjectivity': blob.sentiment.subjectivity,
            'custom_score': self._apply_custom_terms(text)
        }
    
    def analyze_batch(self, texts):
        return [self.analyze_text(text) for text in texts]
    
    def get_sentiment_summary(self, texts):
        analyses = self.analyze_batch(texts)
        
        return {
            'overall_sentiment': sum(a['compound'] for a in analyses) / len(analyses),
            'positive_ratio': sum(1 for a in analyses if a['compound'] > 0.05) / len(analyses),
            'negative_ratio': sum(1 for a in analyses if a['compound'] < -0.05) / len(analyses),
            'neutral_ratio': sum(1 for a in analyses if abs(a['compound']) <= 0.05) / len(analyses),
            'average_subjectivity': sum(a['subjectivity'] for a in analyses) / len(analyses)
        }
    
    def _apply_custom_terms(self, text):
        words = text.lower().split()
        score = 0.0
        for term, value in self.custom_terms.items():
            if term in words:
                score += value
        return score