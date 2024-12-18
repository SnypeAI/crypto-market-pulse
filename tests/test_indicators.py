import pytest
from src.utils.indicators import calculate_rsi

def test_rsi_calculation():
    prices = [10, 12, 11, 13, 15, 14, 16]
    rsi = calculate_rsi(prices)
    assert 0 <= rsi <= 100

def test_rsi_edge_cases():
    # Test flat prices
    flat_prices = [10] * 20
    assert calculate_rsi(flat_prices) == 100
    
    # Test strictly increasing
    up_prices = list(range(20))
    assert calculate_rsi(up_prices) > 70