from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.db.database import get_db
from src.pipeline.data_pipeline import DataPipeline

router = APIRouter(prefix="/markets", tags=["markets"])
data_pipeline = DataPipeline()

@router.get("/symbols")
def get_symbols():
    """Get list of available trading symbols."""
    return {"symbols": data_pipeline.symbols}

@router.get("/{symbol}/indicators")
def get_technical_indicators(symbol: str, db: Session = Depends(get_db)):
    """Get latest technical indicators for a symbol."""
    try:
        # Implementation here
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
