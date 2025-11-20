"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logger import setup_logging, get_logger
from src.config.settings import get_settings
from src.services.scheduler_service import SchedulerService

# Import route modules
from src.api.routes import predictions, training, monitoring, scheduler, portfolio

# Setup
setup_logging()
logger = get_logger(__name__)
settings = get_settings()

# Global scheduler service
scheduler_service_instance = None

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

# Include routers
app.include_router(predictions.router)
app.include_router(training.router)
app.include_router(monitoring.router)
app.include_router(scheduler.router)
app.include_router(portfolio.router)


# Basic routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Stock Trading Decision Support API", "status": "online"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.2.0"}


# Lifecycle events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    global scheduler_service_instance

    logger.info("Starting up application")

    # Initialize scheduler if auto-retraining is enabled
    try:
        # Default symbols to monitor
        default_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "VCB.VN",
            "FPT.VN",
        ]

        scheduler_service_instance = SchedulerService(
            symbols=default_symbols,
            retraining_interval_months=3,
            market_check_enabled=True,
            market_check_interval_hours=24,
            market_drop_threshold=5.0,
        )

        # Set scheduler service reference in scheduler router
        scheduler.set_scheduler_service(scheduler_service_instance)

        # Start scheduler automatically
        # Comment this out if you want to start it manually via API
        # scheduler_service_instance.start()

        logger.info("Scheduler initialized (not started automatically)")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down application")

    if scheduler_service_instance and scheduler_service_instance.scheduler.running:
        scheduler_service_instance.stop()
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
