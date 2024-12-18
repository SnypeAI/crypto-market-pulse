import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from src.ml.predictor import MarketPredictor

def load_models():
    models_dir = Path('models')
    symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
    predictors = {}
    
    for symbol in symbols:
        predictor = MarketPredictor()
        predictor.lstm_model.load_weights(models_dir / f'{symbol}_lstm.h5')
        # Load RF model
        predictors[symbol] = predictor
    
    return predictors

def evaluate_predictions():
    predictors = load_models()
    evaluation = {}
    
    for symbol, predictor in predictors.items():
        print(f'Evaluating {symbol} predictions...')
        
        # Load recent data
        recent_data = pd.read_csv(f'data/recent/{symbol}_data.csv')
        
        # Make predictions
        predictions = []
        for i in range(min(10, len(recent_data))):
            pred = predictor.predict(recent_data.iloc[:i+60])
            predictions.append({
                'timestamp': recent_data.index[i],
                'actual': recent_data.iloc[i]['close'],
                'predicted': pred['price'],
                'confidence': (pred['lstm_confidence'] + pred['rf_confidence']) / 2
            })
        
        evaluation[symbol] = {
            'predictions': predictions,
            'accuracy': calculate_accuracy(predictions)
        }
    
    save_evaluation(evaluation)

def calculate_accuracy(predictions):
    if not predictions:
        return 0.0
    
    actuals = [p['actual'] for p in predictions]
    predicted = [p['predicted'] for p in predictions]
    
    mse = np.mean((np.array(actuals) - np.array(predicted)) ** 2)
    mae = np.mean(np.abs(np.array(actuals) - np.array(predicted)))
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'prediction_count': len(predictions)
    }

def save_evaluation(evaluation):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    eval_file = Path(f'reports/evaluations/evaluation_{timestamp}.json')
    eval_file.parent.mkdir(exist_ok=True)
    
    with open(eval_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

if __name__ == '__main__':
    evaluate_predictions()