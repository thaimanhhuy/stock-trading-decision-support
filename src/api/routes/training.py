"""Model training routes."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from src.utils.logger import get_logger
from src.services.retraining_service import RetrainingService

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/training", tags=["training"])

# Initialize service
retraining_service = RetrainingService()


# Request Models
class TrainingRequest(BaseModel):
    """Training request model."""

    symbol: str = Field(..., description="Stock symbol to train")
    models: str = Field(default="all", description="Models to train (comma-separated or 'all')")
    fetch_new_data: bool = Field(default=True, description="Whether to fetch new data")


class BatchTrainingRequest(BaseModel):
    """Batch training request model."""

    symbols: List[str] = Field(..., description="List of stock symbols to train")
    models: str = Field(default="all", description="Models to train")
    fetch_new_data: bool = Field(default=True, description="Whether to fetch new data")


# Response Models
class TrainingResponse(BaseModel):
    """Training response model."""

    status: str
    symbol: str
    trigger: str
    models_trained: Optional[List[str]] = None
    data_points: Optional[int] = None
    error: Optional[str] = None
    timestamp: str


# Routes
@router.post("/train", response_model=TrainingResponse)
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Manually trigger model training for a symbol.

    Args:
        request: Training request
        background_tasks: FastAPI background tasks

    Returns:
        Training response
    """
    try:
        logger.info(f"Manual training requested for {request.symbol}")

        # For long-running training, you might want to use background_tasks
        # For now, we'll run it synchronously
        result = retraining_service.retrain_model(
            symbol=request.symbol,
            trigger="manual",
            models=request.models,
            fetch_new_data=request.fetch_new_data,
        )

        return TrainingResponse(**result)

    except Exception as e:
        logger.error(f"Training request failed for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-train")
async def batch_train_models(request: BatchTrainingRequest):
    """Manually trigger batch model training for multiple symbols.

    Args:
        request: Batch training request

    Returns:
        List of training responses
    """
    try:
        logger.info(f"Batch training requested for {len(request.symbols)} symbols")

        results = retraining_service.retrain_multiple(
            symbols=request.symbols,
            trigger="manual",
            models=request.models,
            fetch_new_data=request.fetch_new_data,
        )

        return {
            "total": len(results),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Batch training request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{symbol}")
async def get_training_history(symbol: str, limit: int = 50):
    """Get training history for a symbol.

    Args:
        symbol: Stock symbol
        limit: Maximum number of records to return

    Returns:
        Training history
    """
    try:
        history = retraining_service.get_training_history(symbol, limit)
        return {"symbol": symbol, "history": history, "total": len(history)}
    except Exception as e:
        logger.error(f"Failed to get training history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_training_stats(symbol: Optional[str] = None):
    """Get training statistics.

    Args:
        symbol: Optional symbol to filter by

    Returns:
        Training statistics
    """
    try:
        stats = retraining_service.get_training_stats(symbol)
        return stats
    except Exception as e:
        logger.error(f"Failed to get training stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
