# API Documentation

## Endpoints

### GET /api/v1/market/summary
Returns current market summary including:
- Price data
- Volume information
- Technical indicators

### GET /api/v1/technical/{symbol}
Returns technical analysis for specific symbol:
- RSI
- MACD
- EMA values
- Volume profile

### GET /api/v1/sentiment
Returns market sentiment analysis:
- Overall market sentiment
- Social media metrics
- News sentiment

## Authentication
All API endpoints require API key authentication.

## Rate Limits
- 60 requests per minute for basic tier
- 300 requests per minute for premium tier