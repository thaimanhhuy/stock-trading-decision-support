"""Scheduler service for automatic model retraining."""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.services.retraining_service import RetrainingService
from src.services.market_monitor import MarketMonitor
from src.utils.logger import LoggerMixin


class SchedulerService(LoggerMixin):
    """Service for scheduling automatic model retraining."""

    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        retraining_interval_months: int = 3,
        market_check_enabled: bool = True,
        market_check_interval_hours: int = 24,
        market_drop_threshold: float = 5.0,
        timezone: str = "UTC",
    ):
        """Initialize scheduler service.

        Args:
            symbols: List of stock symbols to monitor and retrain
            retraining_interval_months: Interval for scheduled retraining (in months)
            market_check_enabled: Whether to enable market event monitoring
            market_check_interval_hours: How often to check for market events
            market_drop_threshold: Market drop percentage threshold for retraining
            timezone: Timezone for scheduling (default: UTC)
        """
        self.symbols = symbols or []
        self.retraining_interval_months = retraining_interval_months
        self.market_check_enabled = market_check_enabled
        self.market_check_interval_hours = market_check_interval_hours
        self.market_drop_threshold = market_drop_threshold

        # Initialize services
        self.retraining_service = RetrainingService()
        self.market_monitor = MarketMonitor()

        # Initialize scheduler
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self._setup_jobs()

        self.logger.info(
            f"Scheduler initialized with {len(self.symbols)} symbols, "
            f"retraining every {retraining_interval_months} months"
        )

    def _setup_jobs(self):
        """Set up scheduled jobs."""
        # Schedule periodic retraining check (runs daily at 2 AM)
        self.scheduler.add_job(
            func=self._scheduled_retraining_check,
            trigger=CronTrigger(hour=2, minute=0),
            id="scheduled_retraining",
            name="Scheduled Retraining Check",
            replace_existing=True,
        )
        self.logger.info("Added scheduled retraining job (daily at 2 AM)")

        # Schedule market monitoring if enabled
        if self.market_check_enabled:
            self.scheduler.add_job(
                func=self._market_event_check,
                trigger=IntervalTrigger(hours=self.market_check_interval_hours),
                id="market_event_check",
                name="Market Event Check",
                replace_existing=True,
            )
            self.logger.info(
                f"Added market event check job (every {self.market_check_interval_hours} hours)"
            )

    def _scheduled_retraining_check(self):
        """Check if any models need scheduled retraining."""
        self.logger.info("Running scheduled retraining check")

        symbols_to_retrain = []

        for symbol in self.symbols:
            if self.retraining_service.should_retrain_scheduled(
                symbol, self.retraining_interval_months
            ):
                symbols_to_retrain.append(symbol)

        if symbols_to_retrain:
            self.logger.info(
                f"Scheduled retraining needed for {len(symbols_to_retrain)} symbols: "
                f"{', '.join(symbols_to_retrain)}"
            )
            results = self.retraining_service.retrain_multiple(
                symbols_to_retrain, trigger="scheduled"
            )

            successful = sum(1 for r in results if r["status"] == "success")
            self.logger.info(
                f"Scheduled retraining complete: {successful}/{len(symbols_to_retrain)} successful"
            )
        else:
            self.logger.info("No scheduled retraining needed at this time")

    def _market_event_check(self):
        """Check for market drop events and trigger retraining if needed."""
        self.logger.info("Running market event check")

        # Check all markets
        check_result = self.market_monitor.check_all_markets(
            threshold_percentage=self.market_drop_threshold, lookback_days=5
        )

        if check_result["any_events_detected"]:
            self.logger.warning(
                f"Market drop events detected in: {', '.join(check_result['markets_with_events'])}"
            )

            # Retrain models for affected markets
            for market in check_result["markets_with_events"]:
                market_symbols = self.market_monitor.get_symbols_for_market(market)

                # Filter to only include symbols we're tracking
                symbols_to_retrain = [s for s in market_symbols if s in self.symbols]

                if symbols_to_retrain:
                    self.logger.info(
                        f"Triggering market event retraining for {len(symbols_to_retrain)} "
                        f"{market} symbols"
                    )

                    results = self.retraining_service.retrain_multiple(
                        symbols_to_retrain, trigger="market_event"
                    )

                    successful = sum(1 for r in results if r["status"] == "success")
                    self.logger.info(
                        f"Market event retraining complete for {market}: "
                        f"{successful}/{len(symbols_to_retrain)} successful"
                    )
        else:
            self.logger.info("No significant market events detected")

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Scheduler started")

            # Run initial checks
            self.logger.info("Running initial checks...")
            self._scheduled_retraining_check()
            if self.market_check_enabled:
                self._market_event_check()
        else:
            self.logger.warning("Scheduler is already running")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Scheduler stopped")
        else:
            self.logger.warning("Scheduler is not running")

    def pause(self):
        """Pause the scheduler."""
        if self.scheduler.running:
            self.scheduler.pause()
            self.logger.info("Scheduler paused")
        else:
            self.logger.warning("Scheduler is not running")

    def resume(self):
        """Resume the scheduler."""
        if self.scheduler.running:
            self.scheduler.resume()
            self.logger.info("Scheduler resumed")
        else:
            self.logger.warning("Scheduler is not running")

    def add_symbol(self, symbol: str):
        """Add a symbol to the monitoring list.

        Args:
            symbol: Stock symbol to add
        """
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.logger.info(f"Added symbol {symbol} to monitoring list")
        else:
            self.logger.warning(f"Symbol {symbol} is already being monitored")

    def remove_symbol(self, symbol: str):
        """Remove a symbol from the monitoring list.

        Args:
            symbol: Stock symbol to remove
        """
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            self.logger.info(f"Removed symbol {symbol} from monitoring list")
        else:
            self.logger.warning(f"Symbol {symbol} is not in monitoring list")

    def get_status(self) -> dict:
        """Get scheduler status.

        Returns:
            Dictionary with scheduler status information
        """
        jobs = self.scheduler.get_jobs()

        return {
            "running": self.scheduler.running,
            "symbols_monitored": len(self.symbols),
            "symbols": self.symbols,
            "retraining_interval_months": self.retraining_interval_months,
            "market_check_enabled": self.market_check_enabled,
            "market_drop_threshold": self.market_drop_threshold,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat()
                    if job.next_run_time
                    else None,
                }
                for job in jobs
            ],
        }

    def trigger_scheduled_retraining_now(self):
        """Manually trigger scheduled retraining check now."""
        self.logger.info("Manually triggering scheduled retraining check")
        self._scheduled_retraining_check()

    def trigger_market_check_now(self):
        """Manually trigger market event check now."""
        self.logger.info("Manually triggering market event check")
        self._market_event_check()
