from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

from .websocket import handle_websocket, broadcast_updates
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

@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(broadcast_updates)

@app.get("/")
async def read_root():
    return {"status": "online", "service": "Crypto Market Pulse API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)

@app.websocket("/ws/{channel}")
async def channel_websocket_endpoint(websocket: WebSocket, channel: str):
    await handle_websocket(websocket, channel)