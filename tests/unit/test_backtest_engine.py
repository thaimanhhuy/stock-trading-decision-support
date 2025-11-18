"""Tests for BacktestEngine."""

import pytest
import pandas as pd
import numpy as np
from src.backtesting.backtest_engine import BacktestEngine


class TestBacktestEngine:
    """Tests for BacktestEngine."""

    @pytest.fixture
    def backtest_engine(self):
        """Create backtest engine instance."""
        return BacktestEngine(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=100000.0
        )

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data."""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        data = pd.DataFrame({
            "date": dates,
            "open": [100.0] * 100,
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [100.0 + i for i in range(100)],
            "volume": [1000000] * 100,
        })
        return data

    @pytest.fixture
    def sample_signals(self):
        """Create sample trading signals."""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        signals = pd.DataFrame({
            "date": dates,
            "signal": ["HOLD"] * 100,
            "strength": [0.0] * 100,
        })
        # Add some buy signals
        signals.loc[10, "signal"] = "BUY"
        signals.loc[10, "strength"] = 1.0
        signals.loc[50, "signal"] = "SELL"
        signals.loc[50, "strength"] = 1.0
        return signals

    def test_initialization(self, backtest_engine):
        """Test backtest engine initialization."""
        assert backtest_engine.symbol == "TEST"
        assert backtest_engine.start_date == "2023-01-01"
        assert backtest_engine.end_date == "2023-12-31"
        assert backtest_engine.initial_capital == 100000.0
        assert backtest_engine.portfolio_value == 100000.0
        assert len(backtest_engine.trades) == 0

    def test_run_backtest(self, backtest_engine, sample_price_data, sample_signals):
        """Test running backtest."""
        results = backtest_engine.run(sample_price_data, sample_signals)

        assert isinstance(results, dict)
        assert "symbol" in results
        assert "initial_capital" in results
        assert "final_capital" in results
        assert "total_return" in results
        assert "num_trades" in results
        assert "sharpe_ratio" in results
        assert "max_drawdown" in results

    def test_results_structure(self, backtest_engine, sample_price_data, sample_signals):
        """Test backtest results structure."""
        results = backtest_engine.run(sample_price_data, sample_signals)

        assert results["symbol"] == "TEST"
        assert results["initial_capital"] == 100000.0
        assert isinstance(results["total_return"], float)

    def test_custom_initial_capital(self, sample_price_data, sample_signals):
        """Test backtest with custom initial capital."""
        engine = BacktestEngine(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=50000.0
        )

        results = engine.run(sample_price_data, sample_signals)

        assert results["initial_capital"] == 50000.0

    def test_total_return_calculation(self, backtest_engine, sample_price_data, sample_signals):
        """Test total return calculation."""
        results = backtest_engine.run(sample_price_data, sample_signals)

        expected_return = (results["final_capital"] - results["initial_capital"]) / results["initial_capital"]
        assert abs(results["total_return"] - expected_return) < 0.0001

    def test_empty_signals(self, backtest_engine, sample_price_data):
        """Test backtest with empty signals."""
        empty_signals = pd.DataFrame()

        results = backtest_engine.run(sample_price_data, empty_signals)

        assert isinstance(results, dict)
        assert results["num_trades"] == 0

    def test_multiple_backtests(self, backtest_engine, sample_price_data, sample_signals):
        """Test running multiple backtests."""
        results1 = backtest_engine.run(sample_price_data, sample_signals)
        results2 = backtest_engine.run(sample_price_data, sample_signals)

        assert isinstance(results1, dict)
        assert isinstance(results2, dict)

    def test_different_symbols(self, sample_price_data, sample_signals):
        """Test backtest with different symbols."""
        engine1 = BacktestEngine("AAPL", "2023-01-01", "2023-12-31", 100000.0)
        engine2 = BacktestEngine("GOOGL", "2023-01-01", "2023-12-31", 100000.0)

        results1 = engine1.run(sample_price_data, sample_signals)
        results2 = engine2.run(sample_price_data, sample_signals)

        assert results1["symbol"] == "AAPL"
        assert results2["symbol"] == "GOOGL"
