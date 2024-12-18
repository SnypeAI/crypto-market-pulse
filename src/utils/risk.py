def calculate_volatility(prices):
    returns = [(prices[i] - prices[i-1])/prices[i-1] 
              for i in range(1, len(prices))]
    return sum([r**2 for r in returns]) / len(returns)

def assess_market_risk(data):
    vol = calculate_volatility(data['prices'])
    volume = data['volume']
    sentiment = data['sentiment']
    
    return {
        'volatility_risk': vol,
        'volume_risk': volume,
        'sentiment_risk': sentiment
    }