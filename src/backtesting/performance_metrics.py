"""Performance metrics calculation."""

import numpy as np
import pandas as pd
from typing import Dict
from src.utils.logger import LoggerMixin
from src.utils.constants import TRADING_DAYS_PER_YEAR


class PerformanceMetrics(LoggerMixin):
    """Calculate trading performance metrics."""

    def calculate_sharpe_ratio(
        self, returns: np.ndarray, risk_free_rate: float = 0.04
    ) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0:
            return 0.0

        mean_return = np.mean(returns) * TRADING_DAYS_PER_YEAR
        std_return = np.std(returns) * np.sqrt(TRADING_DAYS_PER_YEAR)

        if std_return == 0:
            return 0.0

        sharpe = (mean_return - risk_free_rate) / std_return
        return float(sharpe)

    def calculate_max_drawdown(self, portfolio_values: np.ndarray) -> float:
        """Calculate maximum drawdown."""
        if len(portfolio_values) == 0:
            return 0.0

        cummax = np.maximum.accumulate(portfolio_values)
        drawdown = (portfolio_values - cummax) / cummax
        max_dd = np.min(drawdown)

        return float(abs(max_dd))

    def calculate_all_metrics(
        self, portfolio_values: np.ndarray, trades: list
    ) -> Dict[str, float]:
        """Calculate all performance metrics."""
        returns = np.diff(portfolio_values) / portfolio_values[:-1]

        metrics = {
            "total_return": (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0],
            "sharpe_ratio": self.calculate_sharpe_ratio(returns),
            "max_drawdown": self.calculate_max_drawdown(portfolio_values),
            "num_trades": len(trades),
            "win_rate": self._calculate_win_rate(trades),
        }

        return metrics

    def _calculate_win_rate(self, trades: list) -> float:
        """Calculate win rate from trades."""
        if not trades:
            return 0.0

        winning_trades = sum(1 for t in trades if t.get("pnl", 0) > 0)
        return winning_trades / len(trades)
