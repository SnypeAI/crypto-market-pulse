from celery import Celery
from celery.schedules import crontab
import pandas as pd
from sqlalchemy import create_engine
from src.pipeline.data_pipeline import DataPipeline
from src.pipeline.training_pipeline import TrainingPipeline
from src.db.database import get_db
from src.api.websocket import broadcast_updates

app = Celery('tasks')
app.config_from_object('src.celeryconfig')

data_pipeline = DataPipeline()
training_pipeline = TrainingPipeline()

@app.task
def update_market_data():
    """Fetch latest market data and broadcast updates."""
    try:
        # Get fresh market data
        data = data_pipeline.update_market_data()
        
        # Get predictions for each symbol
        predictions = {}
        with get_db() as db:
            for symbol in data_pipeline.symbols:
                pred = training_pipeline.get_prediction(db, symbol)
                predictions[symbol] = pred
        
        # Broadcast updates via WebSocket
        broadcast_updates({
            'type': 'market_update',
            'data': data,
            'predictions': predictions
        })
        
        return True
    except Exception as e:
        print(f"Error in update_market_data: {str(e)}")
        return False

@app.task
def retrain_models():
    """Retrain all models with latest data."""
    try:
        with get_db() as db:
            results = training_pipeline.train_all_models(db, data_pipeline.symbols)
        return results
    except Exception as e:
        print(f"Error in retrain_models: {str(e)}")
        return False

# Schedule tasks
app.conf.beat_schedule = {
    'update-market-data': {
        'task': 'src.tasks.update_market_data',
        'schedule': 60.0,  # Every minute
    },
    'retrain-models': {
        'task': 'src.tasks.retrain_models',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}