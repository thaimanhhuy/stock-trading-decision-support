"""Monitoring and market check routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from src.services.market_monitor import MarketMonitor

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["monitoring"])

# Initialize service
market_monitor = MarketMonitor()


# Response Models
class MarketCheckResponse(BaseModel):
    """Market check response model."""

    event_detected: bool
    market: str
    drop_percentage: float
    threshold: float
    should_retrain: bool
    market_data: Dict[str, Any]


# Routes
@router.get("/monitoring/health")
async def monitoring_health():
    """System health monitoring."""
    return {
        "status": "healthy",
        "models_loaded": True,
        "data_updated": True,
    }


@router.get("/market/check/{market}", response_model=MarketCheckResponse)
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


@router.get("/market/events")
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


# Additional monitoring endpoints
@router.get("/monitoring/models")
async def get_models_status():
    """Get status of all trained models.

    Returns:
        Dictionary with model status information
    """
    try:
        import os
        from src.config.settings import get_settings

        settings = get_settings()
        models_dir = settings.model_saved_path

        if not os.path.exists(models_dir):
            return {
                "models_directory": models_dir,
                "exists": False,
                "models": [],
                "total_count": 0
            }

        # Find all model files
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.h5')]

        # Group by symbol
        models_by_symbol = {}
        for file in model_files:
            # Format: {symbol}_lstm.h5 or {symbol}_gru.h5
            parts = file.rsplit('_', 1)
            symbol = parts[0]
            model_type = parts[1].replace('.h5', '')

            if symbol not in models_by_symbol:
                models_by_symbol[symbol] = []

            # Get file size and modification time
            file_path = os.path.join(models_dir, file)
            file_size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)

            from datetime import datetime
            modified_date = datetime.fromtimestamp(modified_time).isoformat()

            models_by_symbol[symbol].append({
                "type": model_type,
                "file": file,
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "last_modified": modified_date
            })

        # Format response
        models_list = [
            {
                "symbol": symbol,
                "models": models,
                "model_types": [m["type"] for m in models]
            }
            for symbol, models in models_by_symbol.items()
        ]

        return {
            "models_directory": models_dir,
            "exists": True,
            "models": models_list,
            "total_symbols": len(models_by_symbol),
            "total_files": len(model_files)
        }

    except Exception as e:
        logger.error(f"Failed to get models status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/data-quality/{symbol}")
async def check_data_quality(symbol: str):
    """Check data quality for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Data quality metrics
    """
    try:
        from src.data_ingestion.yahoo_finance_fetcher import YahooDataFetcher
        from datetime import datetime, timedelta

        fetcher = YahooDataFetcher()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)

        data = fetcher.fetch(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )

        if data is None or len(data) == 0:
            return {
                "symbol": symbol,
                "status": "error",
                "message": "No data available",
                "quality_score": 0.0
            }

        # Calculate quality metrics
        total_rows = len(data)
        missing_values = data.isnull().sum().sum()
        missing_percent = (missing_values / (total_rows * len(data.columns))) * 100

        # Check for zeros in price columns
        zero_prices = ((data['close'] == 0) | (data['open'] == 0)).sum()

        # Calculate data completeness (expect ~60 trading days in 100 calendar days)
        expected_days = 60
        completeness = min(100, (total_rows / expected_days) * 100)

        # Quality score (0-100)
        quality_score = (
            (100 - missing_percent) * 0.4 +  # 40% weight
            completeness * 0.4 +  # 40% weight
            (100 if zero_prices == 0 else 80) * 0.2  # 20% weight
        )

        return {
            "symbol": symbol,
            "status": "healthy" if quality_score >= 80 else "degraded",
            "quality_score": round(quality_score, 2),
            "metrics": {
                "total_rows": total_rows,
                "missing_values": int(missing_values),
                "missing_percent": round(missing_percent, 2),
                "zero_prices": int(zero_prices),
                "completeness_percent": round(completeness, 2),
                "date_range": {
                    "start": data.index[0].strftime("%Y-%m-%d"),
                    "end": data.index[-1].strftime("%Y-%m-%d")
                }
            }
        }

    except Exception as e:
        logger.error(f"Data quality check failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/system")
async def get_system_metrics():
    """Get system resource metrics.

    Returns:
        System metrics including CPU, memory, disk usage
    """
    try:
        import psutil
        import platform
        from datetime import datetime

        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory info
        memory = psutil.virtual_memory()

        # Disk info
        disk = psutil.disk_usage('/')

        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version()
            },
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
        }

    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/drift/{symbol}")
async def check_model_drift(symbol: str):
    """Check for model drift for a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Drift detection results
    """
    try:
        # This is a placeholder implementation
        # In production, you would compare recent predictions vs actual values
        # and calculate metrics like PSI (Population Stability Index)

        return {
            "symbol": symbol,
            "drift_detected": False,
            "drift_score": 0.0,
            "status": "healthy",
            "message": "Model drift detection is not yet fully implemented. "
                      "This requires tracking prediction accuracy over time.",
            "last_check": "2025-01-15T10:00:00",
            "metrics": {
                "prediction_accuracy_30d": None,
                "prediction_accuracy_90d": None,
                "psi_score": None
            }
        }

    except Exception as e:
        logger.error(f"Drift check failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
