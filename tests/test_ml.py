import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.ml.predictor import MarketPredictor
from src.ml.feature_engineering import FeatureEngineer

@pytest.fixture
def sample_market_data():
    # Generate sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    data = pd.DataFrame({
        'close': np.random.normal(42000, 1000, 100),
        'volume': np.random.normal(1000, 100, 100),
        'rsi': np.random.uniform(0, 100, 100),
        'macd': np.random.normal(0, 1, 100),
        'atr': np.random.uniform(100, 500, 100)
    }, index=dates)
    return data

@pytest.fixture
def feature_engineer():
    return FeatureEngineer()

@pytest.fixture
def market_predictor():
    return MarketPredictor()

def test_feature_engineering(feature_engineer, sample_market_data):
    df = feature_engineer.create_features(sample_market_data)
    
    # Check if all expected features are present
    assert 'rsi' in df.columns
    assert 'macd' in df.columns
    assert 'bb_upper' in df.columns
    assert 'bb_lower' in df.columns
    assert 'volatility' in df.columns
    assert 'trend' in df.columns

def test_rsi_calculation(feature_engineer):
    prices = pd.Series([10, 12, 11, 13, 15, 14, 16])
    rsi = feature_engineer.calculate_rsi(prices)
    
    assert not rsi.isna().all()
    assert (rsi >= 0).all() and (rsi <= 100).all()

def test_bollinger_bands(feature_engineer):
    prices = pd.Series(np.random.normal(100, 10, 50))
    bb = feature_engineer.calculate_bollinger_bands(prices)
    
    assert (bb['upper'] >= bb['middle']).all()
    assert (bb['lower'] <= bb['middle']).all()

def test_market_predictor_initialization(market_predictor):
    assert market_predictor.rf_model is not None
    assert market_predictor.lstm_model is not None

def test_data_preparation(market_predictor, sample_market_data):
    X, y = market_predictor.prepare_data(sample_market_data)
    
    assert X.shape[1] == 60  # lookback period
    assert X.shape[2] == 5   # number of features
    assert len(y) == len(X)

def test_model_prediction(market_predictor, sample_market_data):
    # Train the model first
    market_predictor.train(sample_market_data)
    
    # Make prediction
    prediction = market_predictor.predict(sample_market_data)
    
    assert 'price' in prediction
    assert 'lstm_confidence' in prediction
    assert 'rf_confidence' in prediction
    assert isinstance(prediction['price'], (float, np.float32, np.float64))

def test_temporal_features(feature_engineer, sample_market_data):
    df = feature_engineer.add_temporal_features(sample_market_data)
    
    assert 'hour' in df.columns
    assert 'day_of_week' in df.columns
    assert 'month' in df.columns
    
    assert (df['hour'] >= 0).all() and (df['hour'] < 24).all()
    assert (df['day_of_week'] >= 0).all() and (df['day_of_week'] < 7).all()
    assert (df['month'] >= 1).all() and (df['month'] <= 12).all()