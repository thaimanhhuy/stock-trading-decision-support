"""Model performance monitoring."""

from typing import Dict, List
from src.utils.logger import LoggerMixin


class PerformanceMonitor(LoggerMixin):
    """Monitor model performance over time."""

    def __init__(self, symbol: str, alert_threshold: float = -0.10):
        """Initialize performance monitor.

        Args:
            symbol: Stock symbol
            alert_threshold: Alert if performance drops below this
        """
        self.symbol = symbol
        self.alert_threshold = alert_threshold
        self.metrics_history: List[Dict] = []

    def track_metrics(self, metrics: Dict) -> None:
        """Track performance metrics.

        Args:
            metrics: Performance metrics dictionary
        """
        self.metrics_history.append(metrics)
        self.logger.info(f"Tracked metrics for {self.symbol}: {metrics}")

    def is_performance_degraded(self) -> bool:
        """Check if performance has degraded.

        Returns:
            True if performance degraded beyond threshold
        """
        if len(self.metrics_history) < 2:
            return False

        recent = self.metrics_history[-1].get("accuracy", 0)
        baseline = self.metrics_history[0].get("accuracy", 0)

        degradation = (recent - baseline) / baseline if baseline != 0 else 0

        if degradation < self.alert_threshold:
            self.logger.warning(f"Performance degraded by {degradation:.2%}")
            return True

        return False
