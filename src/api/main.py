"""FastAPI main application."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from src.utils.logger import setup_logging, get_logger
from src.config.settings import get_settings
from src.services.retraining_service import RetrainingService
from src.services.market_monitor import MarketMonitor
from src.services.scheduler_service import SchedulerService

# Setup
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

# Initialize services
retraining_service = RetrainingService()
market_monitor = MarketMonitor()
scheduler_service = None  # Will be initialized on startup

# Create app
app = FastAPI(
    title="Stock Trading Decision Support API",
    description="API for stock price predictions and trading signals",
    version="0.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class PredictionResponse(BaseModel):
    """Prediction response model."""

    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    timestamp: str


class SignalResponse(BaseModel):
    """Signal response model."""

    symbol: str
    signal: str
    strength: float
    target_price: float
    stop_loss: float
    take_profit: float


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


class TrainingResponse(BaseModel):
    """Training response model."""

    status: str
    symbol: str
    trigger: str
    models_trained: Optional[List[str]] = None
    data_points: Optional[int] = None
    error: Optional[str] = None
    timestamp: str


class MarketCheckResponse(BaseModel):
    """Market check response model."""

    event_detected: bool
    market: str
    drop_percentage: float
    threshold: float
    should_retrain: bool
    market_data: Dict[str, Any]


# Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Stock Trading Decision Support API", "status": "online"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/v1/predictions/{symbol}")
async def get_prediction(symbol: str) -> PredictionResponse:
    """Get price prediction for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Prediction response
    """
    try:
        # Placeholder implementation
        logger.info(f"Prediction requested for {symbol}")

        return PredictionResponse(
            symbol=symbol,
            current_price=150.0,
            predicted_price=155.0,
            confidence=0.75,
            timestamp="2024-01-01T00:00:00",
        )
    except Exception as e:
        logger.error(f"Prediction failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/signals/{symbol}")
async def get_signal(symbol: str) -> SignalResponse:
    """Get trading signal for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Signal response
    """
    try:
        logger.info(f"Signal requested for {symbol}")

        return SignalResponse(
            symbol=symbol,
            signal="buy",
            strength=0.8,
            target_price=155.0,
            stop_loss=145.0,
            take_profit=160.0,
        )
    except Exception as e:
        logger.error(f"Signal generation failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/monitoring/health")
async def monitoring_health():
    """System health monitoring."""
    return {
        "status": "healthy",
        "models_loaded": True,
        "data_updated": True,
    }


# Retraining endpoints
@app.post("/api/v1/training/train", response_model=TrainingResponse)
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


@app.post("/api/v1/training/batch-train")
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


@app.get("/api/v1/training/history/{symbol}")
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


@app.get("/api/v1/training/stats")
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


# Market monitoring endpoints
@app.get("/api/v1/market/check/{market}", response_model=MarketCheckResponse)
async def check_market(
    market: str, threshold: float = 5.0, lookback_days: int = 5
):
    """Check for market drop events.

    Args:
        market: Market region (us, vietnam)
        threshold: Drop threshold percentage
        lookback_days: Number of days to look back

    Returns:
        Market check result
    """
    try:
        result = market_monitor.check_market_drop_event(
            market, threshold, lookback_days
        )
        return MarketCheckResponse(**result)
    except Exception as e:
        logger.error(f"Market check failed for {market}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/market/events")
async def get_market_events(market: Optional[str] = None, limit: int = 50):
    """Get market event history.

    Args:
        market: Optional market to filter by
        limit: Maximum number of events

    Returns:
        Market events
    """
    try:
        events = market_monitor.get_market_events(market, limit)
        return {"events": events, "total": len(events)}
    except Exception as e:
        logger.error(f"Failed to get market events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Scheduler control endpoints
@app.get("/api/v1/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status.

    Returns:
        Scheduler status
    """
    try:
        if scheduler_service:
            return scheduler_service.get_status()
        else:
            return {"running": False, "message": "Scheduler not initialized"}
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scheduler/start")
async def start_scheduler():
    """Start the scheduler.

    Returns:
        Status message
    """
    try:
        if scheduler_service:
            scheduler_service.start()
            return {"status": "success", "message": "Scheduler started"}
        else:
            return {"status": "error", "message": "Scheduler not initialized"}
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler.

    Returns:
        Status message
    """
    try:
        if scheduler_service:
            scheduler_service.stop()
            return {"status": "success", "message": "Scheduler stopped"}
        else:
            return {"status": "error", "message": "Scheduler not initialized"}
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scheduler/trigger-retraining")
async def trigger_scheduled_retraining():
    """Manually trigger scheduled retraining check.

    Returns:
        Status message
    """
    try:
        if scheduler_service:
            scheduler_service.trigger_scheduled_retraining_now()
            return {
                "status": "success",
                "message": "Scheduled retraining check triggered",
            }
        else:
            return {"status": "error", "message": "Scheduler not initialized"}
    except Exception as e:
        logger.error(f"Failed to trigger scheduled retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scheduler/trigger-market-check")
async def trigger_market_check():
    """Manually trigger market event check.

    Returns:
        Status message
    """
    try:
        if scheduler_service:
            scheduler_service.trigger_market_check_now()
            return {"status": "success", "message": "Market event check triggered"}
        else:
            return {"status": "error", "message": "Scheduler not initialized"}
    except Exception as e:
        logger.error(f"Failed to trigger market check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    global scheduler_service

    logger.info("Starting up application")

    # Initialize scheduler if auto-retraining is enabled
    # This can be configured via settings
    try:
        # Default symbols to monitor
        default_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "VCB.VN",
            "FPT.VN",
        ]

        scheduler_service = SchedulerService(
            symbols=default_symbols,
            retraining_interval_months=3,
            market_check_enabled=True,
            market_check_interval_hours=24,
            market_drop_threshold=5.0,
        )

        # Start scheduler automatically
        # Comment this out if you want to start it manually via API
        # scheduler_service.start()

        logger.info("Scheduler initialized (not started automatically)")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application")

    if scheduler_service and scheduler_service.scheduler.running:
        scheduler_service.stop()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
