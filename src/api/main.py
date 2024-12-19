from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException, WebSocket
from sqlalchemy.orm import Session

from src.api.websocket import broadcast_updates, handle_websocket
from src.db.database import get_db
from src.pipeline.data_pipeline import DataPipeline
from src.pipeline.training_pipeline import TrainingPipeline

app = FastAPI(title="Crypto Market Pulse API")
data_pipeline = DataPipeline()
training_pipeline = TrainingPipeline()


@app.get("/markets/{symbol}/prediction")
async def get_prediction(symbol: str, db: Session = Depends(get_db)):
    """Get price prediction for a specific symbol."""
    try:
        latest_data = data_pipeline.get_latest_data(db, symbol, limit=100)
        if not latest_data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        # Convert to format needed for prediction
        df = pd.DataFrame(
            [
                {
                    "timestamp": d.timestamp,
                    "open": d.open,
                    "high": d.high,
                    "low": d.low,
                    "close": d.close,
                    "volume": d.volume,
                }
                for d in latest_data
            ]
        )

        prediction = training_pipeline.predictor.predict(df)
        return prediction

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/markets/available")
def get_available_markets():
    """Get list of available market symbols."""
    return {"symbols": data_pipeline.symbols}


@app.get("/markets/{symbol}/data")
def get_market_data(symbol: str, limit: int = 100, db: Session = Depends(get_db)):
    """Get historical market data for a symbol."""
    data = data_pipeline.get_latest_data(db, symbol, limit)
    return {"data": data}


@app.post("/training/start")
async def start_training(symbols: List[str], db: Session = Depends(get_db)):
    """Start training models for specified symbols."""
    try:
        results = await training_pipeline.train_all_models(db, symbols)
        return {"training_results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """WebSocket endpoint for real-time updates."""
    await handle_websocket(websocket, channel)
