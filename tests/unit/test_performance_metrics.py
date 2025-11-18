"""Tests for PerformanceMetrics."""

import pytest
import numpy as np
from src.backtesting.performance_metrics import PerformanceMetrics


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance."""
        return PerformanceMetrics()

    def test_calculate_sharpe_ratio_positive(self, metrics):
        """Test Sharpe ratio calculation with positive returns."""
        # Generate random positive returns
        np.random.seed(42)
        returns = np.random.randn(252) * 0.01 + 0.001  # Mean positive return

        sharpe = metrics.calculate_sharpe_ratio(returns, risk_free_rate=0.04)

        assert isinstance(sharpe, float)
        # With positive mean return > risk free rate, Sharpe should be positive
        assert sharpe > 0

    def test_calculate_sharpe_ratio_zero_std(self, metrics):
        """Test Sharpe ratio with zero standard deviation."""
        returns = np.array([0.0] * 100)  # Constant zero returns (std is exactly 0)

        sharpe = metrics.calculate_sharpe_ratio(returns)

        assert sharpe == 0.0

    def test_calculate_sharpe_ratio_empty(self, metrics):
        """Test Sharpe ratio with empty returns."""
        returns = np.array([])

        sharpe = metrics.calculate_sharpe_ratio(returns)

        assert sharpe == 0.0

    def test_calculate_max_drawdown(self, metrics):
        """Test max drawdown calculation."""
        # Portfolio that goes up then down
        portfolio_values = np.array([100, 110, 120, 115, 100, 95, 100])

        max_dd = metrics.calculate_max_drawdown(portfolio_values)

        assert isinstance(max_dd, float)
        assert max_dd >= 0  # Drawdown is reported as positive
        # Max drawdown should be from peak (120) to trough (95)
        expected_dd = (120 - 95) / 120
        assert abs(max_dd - expected_dd) < 0.01

    def test_calculate_max_drawdown_no_drawdown(self, metrics):
        """Test max drawdown with constantly increasing portfolio."""
        portfolio_values = np.array([100, 110, 120, 130, 140])

        max_dd = metrics.calculate_max_drawdown(portfolio_values)

        assert max_dd == 0.0

    def test_calculate_max_drawdown_empty(self, metrics):
        """Test max drawdown with empty array."""
        portfolio_values = np.array([])

        max_dd = metrics.calculate_max_drawdown(portfolio_values)

        assert max_dd == 0.0

    def test_calculate_all_metrics(self, metrics):
        """Test calculating all metrics."""
        portfolio_values = np.array([100, 105, 110, 108, 115, 120])
        trades = [
            {"pnl": 500},
            {"pnl": -200},
            {"pnl": 300},
            {"pnl": 100},
        ]

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        assert isinstance(result, dict)
        assert "total_return" in result
        assert "sharpe_ratio" in result
        assert "max_drawdown" in result
        assert "num_trades" in result
        assert "win_rate" in result

        assert result["num_trades"] == 4
        assert 0 <= result["win_rate"] <= 1

    def test_calculate_total_return(self, metrics):
        """Test total return calculation."""
        portfolio_values = np.array([100, 110, 120, 130])
        trades = []

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        expected_return = (130 - 100) / 100
        assert abs(result["total_return"] - expected_return) < 0.001

    def test_win_rate_all_winning(self, metrics):
        """Test win rate with all winning trades."""
        portfolio_values = np.array([100, 110])
        trades = [
            {"pnl": 500},
            {"pnl": 300},
            {"pnl": 100},
        ]

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        assert result["win_rate"] == 1.0

    def test_win_rate_all_losing(self, metrics):
        """Test win rate with all losing trades."""
        portfolio_values = np.array([100, 90])
        trades = [
            {"pnl": -500},
            {"pnl": -300},
            {"pnl": -100},
        ]

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        assert result["win_rate"] == 0.0

    def test_win_rate_mixed(self, metrics):
        """Test win rate with mixed trades."""
        portfolio_values = np.array([100, 105])
        trades = [
            {"pnl": 500},   # Win
            {"pnl": -200},  # Loss
            {"pnl": 300},   # Win
            {"pnl": -100},  # Loss
        ]

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        assert result["win_rate"] == 0.5

    def test_win_rate_no_trades(self, metrics):
        """Test win rate with no trades."""
        portfolio_values = np.array([100, 100])
        trades = []

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        assert result["win_rate"] == 0.0

    def test_win_rate_break_even(self, metrics):
        """Test win rate with break-even trades."""
        portfolio_values = np.array([100, 100])
        trades = [
            {"pnl": 0},
            {"pnl": 0},
        ]

        result = metrics.calculate_all_metrics(portfolio_values, trades)

        # Break-even trades are not winning trades
        assert result["win_rate"] == 0.0

    def test_sharpe_ratio_custom_risk_free_rate(self, metrics):
        """Test Sharpe ratio with custom risk-free rate."""
        np.random.seed(42)
        returns = np.random.randn(252) * 0.01 + 0.001

        sharpe1 = metrics.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
        sharpe2 = metrics.calculate_sharpe_ratio(returns, risk_free_rate=0.06)

        # Higher risk-free rate should result in lower Sharpe ratio
        assert sharpe1 > sharpe2

    def test_negative_returns(self, metrics):
        """Test metrics with negative returns."""
        np.random.seed(42)
        returns = np.random.randn(252) * 0.01 - 0.001  # Mean negative return

        sharpe = metrics.calculate_sharpe_ratio(returns, risk_free_rate=0.04)

        # Negative returns should result in negative Sharpe ratio
        assert sharpe < 0

    def test_max_drawdown_recovery(self, metrics):
        """Test max drawdown with recovery."""
        # Portfolio that drops then recovers
        portfolio_values = np.array([100, 90, 80, 85, 95, 105])

        max_dd = metrics.calculate_max_drawdown(portfolio_values)

        # Max drawdown should be from peak (100) to trough (80)
        expected_dd = (100 - 80) / 100
        assert abs(max_dd - expected_dd) < 0.01
