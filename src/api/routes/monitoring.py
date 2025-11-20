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
