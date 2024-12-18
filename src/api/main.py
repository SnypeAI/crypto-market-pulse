from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import numpy as np

from src.ml.predictor import MarketPredictor
from src.monitoring.metrics_collector import MetricsCollector

app = FastAPI(title="Crypto Market Pulse API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
predictor = MarketPredictor()
metrics = MetricsCollector()

# Models
class PredictionRequest(BaseModel):
    symbol: str
    historical_data: Dict[str, List[float]]

class PredictionResponse(BaseModel):
    symbol: str
    predicted_price: float
    confidence: float
    timestamp: str

@app.get("/")
async def read_root():
    return {"status": "online", "service": "Crypto Market Pulse API"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        # Make prediction
        prediction = predictor.predict(request.historical_data)
        
        response = {
            "symbol": request.symbol,
            "predicted_price": float(prediction['price']),
            "confidence": float((prediction['lstm_confidence'] + prediction['rf_confidence']) / 2),
            "timestamp": datetime.now().isoformat()
        }
        
        # Record prediction
        metrics.record_prediction(request.symbol, prediction)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/{symbol}")
async def get_metrics(symbol: str):
    try:
        return metrics.get_model_performance(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{symbol}")
async def get_analysis(symbol: str):
    try:
        # Get latest metrics
        performance = metrics.get_model_performance(symbol)
        
        # Add technical indicators
        indicators = {
            "rsi": np.random.uniform(30, 70),  # Placeholder
            "macd": np.random.uniform(-2, 2),  # Placeholder
            "volume": np.random.uniform(1e9, 1e10)  # Placeholder
        }
        
        return {
            "performance": performance,
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))