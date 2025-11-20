"""Scheduler control routes."""

from fastapi import APIRouter, HTTPException
from src.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/scheduler", tags=["scheduler"])

# Global scheduler service reference
# This will be set from main.py during startup
scheduler_service: Optional[object] = None


def set_scheduler_service(service):
    """Set the scheduler service reference.

    Args:
        service: SchedulerService instance
    """
    global scheduler_service
    scheduler_service = service


# Routes
@router.get("/status")
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


@router.post("/start")
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


@router.post("/stop")
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


@router.post("/trigger-retraining")
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


@router.post("/trigger-market-check")
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
