"""Integration tests for backtest functionality."""

import pytest
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from src.backtesting.run_backtest import BacktestRunner


class TestBacktestIntegration:
    """Integration tests for complete backtest workflow."""

    @pytest.fixture
    def sample_historical_data(self):
        """Create realistic historical data."""
        np.random.seed(42)
        n_days = 252  # 1 year of trading days

        # Generate price data with trend
        base_price = 100.0
        returns = np.random.normal(0.0005, 0.02, n_days)  # Small positive drift
        prices = base_price * np.exp(np.cumsum(returns))

        dates = pd.date_range(start="2023-01-01", periods=n_days, freq="B")

        data = pd.DataFrame({
            "date": dates,
            "open": prices * (1 + np.random.uniform(-0.01, 0.01, n_days)),
            "high": prices * (1 + np.random.uniform(0, 0.02, n_days)),
            "low": prices * (1 - np.random.uniform(0, 0.02, n_days)),
            "close": prices,
            "volume": np.random.randint(1000000, 10000000, n_days),
        })

        # Add technical indicators (simplified)
        data["rsi"] = 50.0 + np.random.uniform(-20, 20, n_days)
        data["macd"] = np.random.uniform(-2, 2, n_days)
        data["sma_20"] = data["close"].rolling(20, min_periods=1).mean()
        data["ema_12"] = data["close"].ewm(span=12, adjust=False).mean()

        return data

    def test_full_backtest_workflow(self, sample_historical_data, tmp_path):
        """Test complete backtest workflow without models."""
        runner = BacktestRunner(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=100000.0,
        )

        # Mock model loading (since we don't have trained models)
        from unittest.mock import Mock

        mock_lstm = Mock()
        mock_lstm.predict.return_value = np.array([105.0])
        mock_lstm.is_trained = True

        mock_gru = Mock()
        mock_gru.predict.return_value = np.array([104.5])
        mock_gru.is_trained = True

        models = {"lstm": mock_lstm, "gru": mock_gru}

        # Run backtest
        results = runner.run_backtest(models, sample_historical_data)

        # Verify results
        assert results is not None
        assert results["symbol"] == "TEST"
        assert results["portfolio"]["initial_capital"] == 100000.0
        assert results["portfolio"]["final_capital"] > 0

        # Save results
        output_dir = str(tmp_path / "results")
        filepath = runner.save_results(results, output_dir=output_dir)

        # Verify file exists and is valid JSON
        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            loaded_results = json.load(f)
        assert loaded_results["symbol"] == "TEST"

    def test_backtest_with_profitable_strategy(self, sample_historical_data):
        """Test backtest with a profitable mock strategy."""
        runner = BacktestRunner(
            symbol="PROFIT_TEST",
            initial_capital=100000.0,
        )

        from unittest.mock import Mock

        # Create mock model that predicts higher prices (profitable)
        mock_model = Mock()

        def profitable_predict(X):
            # Always predict 2% higher than current
            return np.array([110.0])  # Simplified

        mock_model.predict = profitable_predict
        mock_model.is_trained = True

        models = {"lstm": mock_model}

        # Run backtest
        results = runner.run_backtest(models, sample_historical_data)

        # Verify metrics
        assert results["trading"]["num_trades"] >= 0
        assert results["risk_metrics"]["sharpe_ratio"] is not None
        assert results["risk_metrics"]["max_drawdown"] >= 0

    def test_backtest_metrics_consistency(self, sample_historical_data):
        """Test that backtest metrics are consistent and valid."""
        runner = BacktestRunner(
            symbol="METRICS_TEST",
            initial_capital=100000.0,
        )

        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        models = {"lstm": mock_model}

        # Run backtest
        results = runner.run_backtest(models, sample_historical_data)

        # Verify metric consistency
        total_return = results["returns"]["total_return"]
        final_capital = results["portfolio"]["final_capital"]
        initial_capital = results["portfolio"]["initial_capital"]

        # Total return should match capital change
        expected_return = ((final_capital - initial_capital) / initial_capital) * 100
        assert abs(total_return - expected_return) < 0.01

        # Win rate should be between 0 and 100
        assert 0 <= results["trading"]["win_rate"] <= 100

        # Max drawdown should be positive
        assert results["risk_metrics"]["max_drawdown"] >= 0

    def test_backtest_with_different_capital_levels(self, sample_historical_data):
        """Test backtest with different initial capital amounts."""
        capitals = [10000.0, 50000.0, 100000.0, 500000.0]
        all_results = []

        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        for capital in capitals:
            runner = BacktestRunner(
                symbol="TEST",
                initial_capital=capital,
            )

            models = {"lstm": mock_model}
            results = runner.run_backtest(models, sample_historical_data)
            all_results.append(results)

            # Verify initial capital is correct
            assert results["portfolio"]["initial_capital"] == capital

        # Returns should be similar across different capital levels
        # (percentage returns should not depend heavily on capital)
        returns = [r["returns"]["total_return"] for r in all_results]
        # Allow some variance but they should be in similar range
        assert max(returns) - min(returns) < 50  # Within 50% points

    def test_backtest_with_transaction_costs(self, sample_historical_data):
        """Test impact of transaction costs on results."""
        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        # Run with no transaction costs
        runner_no_cost = BacktestRunner(
            symbol="TEST",
            initial_capital=100000.0,
            transaction_cost=0.0,
            slippage=0.0,
        )

        results_no_cost = runner_no_cost.run_backtest(
            {"lstm": mock_model}, sample_historical_data
        )

        # Run with transaction costs
        runner_with_cost = BacktestRunner(
            symbol="TEST",
            initial_capital=100000.0,
            transaction_cost=0.01,  # 1%
            slippage=0.005,  # 0.5%
        )

        results_with_cost = runner_with_cost.run_backtest(
            {"lstm": mock_model}, sample_historical_data
        )

        # Results with costs should have lower or equal returns
        # (unless no trades were made)
        if results_no_cost["trading"]["num_trades"] > 0:
            assert (
                results_with_cost["returns"]["total_return"]
                <= results_no_cost["returns"]["total_return"]
            )

    def test_backtest_date_range_handling(self, sample_historical_data):
        """Test backtest with different date ranges."""
        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        # Test with different date ranges
        runner = BacktestRunner(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-06-30",  # Half year
            initial_capital=100000.0,
        )

        models = {"lstm": mock_model}

        # Filter data to match date range
        half_year_data = sample_historical_data[
            sample_historical_data["date"] <= "2023-06-30"
        ]

        results = runner.run_backtest(models, half_year_data)

        # Verify backtest period is correct
        assert results["backtest_period"]["start_date"] == "2023-01-01"
        assert results["backtest_period"]["end_date"] == "2023-06-30"

    def test_backtest_with_minimal_data(self):
        """Test backtest with minimal data points."""
        # Create minimal data (just enough for sequence length + 1)
        n_days = 65  # 60 for sequence + 5 for testing

        dates = pd.date_range(start="2023-01-01", periods=n_days, freq="D")
        data = pd.DataFrame({
            "date": dates,
            "open": [100.0] * n_days,
            "high": [105.0] * n_days,
            "low": [95.0] * n_days,
            "close": [100.0 + i * 0.5 for i in range(n_days)],
            "volume": [1000000] * n_days,
            "rsi": [50.0] * n_days,
            "macd": [0.0] * n_days,
        })

        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        runner = BacktestRunner(
            symbol="TEST",
            initial_capital=100000.0,
        )

        # Should not crash with minimal data
        results = runner.run_backtest({"lstm": mock_model}, data)

        assert results is not None
        assert results["symbol"] == "TEST"

    def test_backtest_summary_file_format(self, sample_historical_data, tmp_path):
        """Test that summary file has correct format."""
        from unittest.mock import Mock

        mock_model = Mock()
        mock_model.predict.return_value = np.array([105.0])
        mock_model.is_trained = True

        runner = BacktestRunner(
            symbol="TEST",
            initial_capital=100000.0,
        )

        results = runner.run_backtest({"lstm": mock_model}, sample_historical_data)

        output_dir = str(tmp_path / "results")
        runner.save_results(results, output_dir=output_dir)

        # Check summary file
        summary_path = os.path.join(output_dir, "backtest_summary.json")
        assert os.path.exists(summary_path)

        with open(summary_path, "r") as f:
            summary = json.load(f)

        # Verify required fields
        required_top_level = ["symbol", "backtest_period", "portfolio", "returns", "risk_metrics", "trading"]
        for field in required_top_level:
            assert field in summary

        # Verify nested fields
        assert "total_return" in summary["returns"]
        assert "annual_return" in summary["returns"]
        assert "sharpe_ratio" in summary["risk_metrics"]
        assert "max_drawdown" in summary["risk_metrics"]
        assert "win_rate" in summary["trading"]

    def test_backtest_with_no_trading_signals(self, sample_historical_data):
        """Test backtest when no trading signals are generated."""
        from unittest.mock import Mock

        # Mock model that predicts current price (no signal)
        mock_model = Mock()

        def no_signal_predict(X):
            # Predict same as current price (within threshold)
            return np.array([100.0])

        mock_model.predict = no_signal_predict
        mock_model.is_trained = True

        runner = BacktestRunner(
            symbol="TEST",
            initial_capital=100000.0,
        )

        results = runner.run_backtest({"lstm": mock_model}, sample_historical_data)

        # Should complete without errors
        assert results is not None

        # If no trades, final capital should equal initial capital
        # (or close to it, accounting for any default positions)
        if results["trading"]["num_trades"] == 0:
            assert abs(
                results["portfolio"]["final_capital"] - results["portfolio"]["initial_capital"]
            ) < 100  # Allow small difference
