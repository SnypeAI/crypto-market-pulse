import pandas as pd
import json
from pathlib import Path
from src.ml.predictor import MarketPredictor
from src.ml.feature_engineering import FeatureEngineer

def load_data():
    data_path = Path('data/historical')
    symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
    data = {}
    
    for symbol in symbols:
        df = pd.read_csv(data_path / f'{symbol}_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        data[symbol] = df
    
    return data

def train_models():
    # Load and prepare data
    data = load_data()
    engineer = FeatureEngineer()
    predictors = {}
    metrics = {}
    
    for symbol, df in data.items():
        print(f'Training models for {symbol}...')
        
        # Feature engineering
        df_features = engineer.create_features(df)
        
        # Initialize and train predictor
        predictor = MarketPredictor()
        predictor.train(df_features)
        
        # Save trained model
        predictors[symbol] = predictor
        
        # Calculate and store metrics
        metrics[symbol] = evaluate_model(predictor, df_features)
    
    # Save models and metrics
    save_models(predictors)
    save_metrics(metrics)

def evaluate_model(predictor, data):
    predictions = []
    actuals = []
    
    # Get predictions for last 20% of data
    test_size = int(len(data) * 0.2)
    test_data = data.iloc[-test_size:]
    
    for i in range(len(test_data)):
        pred = predictor.predict(test_data.iloc[:i+60])  # 60 is lookback period
        predictions.append(pred['price'])
        actuals.append(test_data.iloc[i]['close'])
    
    # Calculate metrics
    mse = ((pd.Series(predictions) - pd.Series(actuals)) ** 2).mean()
    mae = abs(pd.Series(predictions) - pd.Series(actuals)).mean()
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'predictions': len(predictions)
    }

def save_models(predictors):
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    for symbol, predictor in predictors.items():
        predictor.lstm_model.save(models_dir / f'{symbol}_lstm.h5')
        # Save RF model using joblib or pickle

def save_metrics(metrics):
    metrics_file = Path('reports/model_metrics.json')
    metrics_file.parent.mkdir(exist_ok=True)
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

if __name__ == '__main__':
    train_models()