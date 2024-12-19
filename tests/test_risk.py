from src.utils.risk import assess_market_risk, calculate_volatility


def test_volatility_calculation():
    prices = [100, 105, 98, 103, 101]
    vol = calculate_volatility(prices)
    assert vol >= 0


def test_risk_assessment():
    data = {"prices": [100, 105, 98, 103, 101], "volume": 1000000, "sentiment": 0.7}
    risk = assess_market_risk(data)
    assert "volatility_risk" in risk
    assert "volume_risk" in risk
    assert "sentiment_risk" in risk
