"""Tests for run_backtest script."""

import pytest
import pandas as pd
import numpy as np
import os
import json
from unittest.mock import Mock, patch, MagicMock
from src.backtesting.run_backtest import BacktestRunner


class TestBacktestRunner:
    """Tests for BacktestRunner."""

    @pytest.fixture
    def backtest_runner(self):
        """Create backtest runner instance."""
        return BacktestRunner(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=100000.0,
        )

    @pytest.fixture
    def sample_data(self):
        """Create sample market data."""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        data = pd.DataFrame({
            "date": dates,
            "open": np.random.uniform(100, 110, 100),
            "high": np.random.uniform(105, 115, 100),
            "low": np.random.uniform(95, 105, 100),
            "close": np.random.uniform(100, 110, 100),
            "volume": np.random.randint(1000000, 10000000, 100),
        })
        # Add some basic technical indicators
        data["rsi"] = 50.0
        data["macd"] = 0.0
        return data

    @pytest.fixture
    def mock_models(self):
        """Create mock models."""
        models = {}

        # Mock LSTM model
        lstm_mock = Mock()
        lstm_mock.predict.return_value = np.array([105.0])
        lstm_mock.is_trained = True
        models["lstm"] = lstm_mock

        # Mock GRU model
        gru_mock = Mock()
        gru_mock.predict.return_value = np.array([106.0])
        gru_mock.is_trained = True
        models["gru"] = gru_mock

        return models

    def test_initialization(self, backtest_runner):
        """Test backtest runner initialization."""
        assert backtest_runner.symbol == "TEST"
        assert backtest_runner.initial_capital == 100000.0
        assert backtest_runner.cash == 100000.0
        assert backtest_runner.position == 0
        assert len(backtest_runner.trades) == 0
        assert len(backtest_runner.portfolio_values) == 0

    def test_initialization_with_custom_params(self):
        """Test initialization with custom parameters."""
        runner = BacktestRunner(
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=50000.0,
            transaction_cost=0.002,
            slippage=0.001,
        )

        assert runner.symbol == "AAPL"
        assert runner.initial_capital == 50000.0
        assert runner.transaction_cost == 0.002
        assert runner.slippage == 0.001

    @patch("os.path.exists")
    @patch("src.backtesting.run_backtest.LSTMModel")
    @patch("src.backtesting.run_backtest.GRUModel")
    def test_load_models_success(
        self, mock_gru_class, mock_lstm_class, mock_exists, backtest_runner
    ):
        """Test successful model loading."""
        # Mock file existence
        mock_exists.return_value = True

        # Mock model instances
        mock_lstm = Mock()
        mock_gru = Mock()

        mock_lstm_class.return_value = mock_lstm
        mock_gru_class.return_value = mock_gru

        # Load models
        models = backtest_runner.load_models()

        # Verify models loaded
        assert "lstm" in models
        assert "gru" in models
        assert len(models) == 2

    @patch("os.path.exists")
    def test_load_models_no_models_found(self, mock_exists, backtest_runner):
        """Test error when no models found."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError) as exc_info:
            backtest_runner.load_models()

        assert "No trained models found" in str(exc_info.value)

    @patch("src.backtesting.run_backtest.YahooDataFetcher")
    @patch("src.backtesting.run_backtest.DataProcessor")
    def test_load_data_with_dates(self, mock_processor_class, mock_fetcher_class):
        """Test data loading with specific dates."""
        runner = BacktestRunner(
            symbol="TEST",
            start_date="2023-01-01",
            end_date="2023-12-31",
        )

        # Mock data fetcher
        mock_fetcher = Mock()
        mock_data = pd.DataFrame({
            "date": pd.date_range("2023-01-01", periods=10),
            "close": [100] * 10,
        })
        mock_fetcher.fetch_data.return_value = mock_data
        runner.data_fetcher = mock_fetcher

        # Mock data processor
        mock_processor = Mock()
        mock_processor.process.return_value = mock_data
        runner.data_processor = mock_processor

        # Load data
        data = runner.load_data()

        # Verify fetch was called with dates
        mock_fetcher.fetch_data.assert_called_once_with(
            "TEST", start_date="2023-01-01", end_date="2023-12-31"
        )

    def test_execute_trade_buy(self, backtest_runner):
        """Test executing buy trade."""
        initial_cash = backtest_runner.cash
        price = 100.0
        date = pd.Timestamp("2023-01-01")

        backtest_runner.execute_trade("buy", price, date, signal_strength=1.0)

        # Verify trade was executed
        assert len(backtest_runner.trades) > 0
        assert backtest_runner.cash < initial_cash
        assert backtest_runner.position > 0

    def test_execute_trade_sell(self, backtest_runner):
        """Test executing sell trade."""
        # First buy some shares
        backtest_runner.position = 100
        backtest_runner.cash = 50000.0
        price = 110.0
        date = pd.Timestamp("2023-01-02")

        backtest_runner.execute_trade("sell", price, date, signal_strength=1.0)

        # Verify sell was executed
        assert any(t["action"] == "SELL" for t in backtest_runner.trades)
        assert backtest_runner.position < 100

    def test_execute_trade_hold(self, backtest_runner):
        """Test hold signal does nothing."""
        initial_cash = backtest_runner.cash
        initial_position = backtest_runner.position
        price = 100.0
        date = pd.Timestamp("2023-01-01")

        backtest_runner.execute_trade("hold", price, date)

        # Verify nothing changed
        assert backtest_runner.cash == initial_cash
        assert backtest_runner.position == initial_position
        assert len(backtest_runner.trades) == 0

    def test_calculate_metrics_basic(self, backtest_runner):
        """Test basic metrics calculation."""
        # Simulate some portfolio values
        backtest_runner.portfolio_values = [100000, 102000, 104000, 103000, 105000]
        backtest_runner.daily_returns = [0.02, 0.02, -0.01, 0.02]
        backtest_runner.trades = [
            {"pnl": 1000},
            {"pnl": 500},
            {"pnl": -200},
        ]

        final_value = 105000.0
        metrics = backtest_runner.calculate_metrics(final_value)

        # Verify metrics structure
        assert "symbol" in metrics
        assert "backtest_period" in metrics
        assert "portfolio" in metrics
        assert "returns" in metrics
        assert "risk_metrics" in metrics
        assert "trading" in metrics

        # Verify some values
        assert metrics["symbol"] == "TEST"
        assert metrics["portfolio"]["final_capital"] == final_value
        assert metrics["portfolio"]["initial_capital"] == 100000.0
        assert metrics["returns"]["total_return"] == 5.0  # 5% return

    def test_calculate_metrics_win_rate(self, backtest_runner):
        """Test win rate calculation."""
        backtest_runner.portfolio_values = [100000, 105000]
        backtest_runner.daily_returns = [0.05]
        backtest_runner.trades = [
            {"pnl": 1000},
            {"pnl": 500},
            {"pnl": -200},
            {"pnl": 800},
        ]

        metrics = backtest_runner.calculate_metrics(105000.0)

        # 3 winning trades out of 4 = 75% win rate
        assert metrics["trading"]["winning_trades"] == 3
        assert metrics["trading"]["losing_trades"] == 1
        assert metrics["trading"]["win_rate"] == 75.0

    def test_save_results(self, backtest_runner, tmp_path):
        """Test saving results to file."""
        results = {
            "symbol": "TEST",
            "returns": {"total_return": 10.5},
            "timestamp": "2023-01-01T00:00:00",
        }

        output_dir = str(tmp_path / "test_results")
        filepath = backtest_runner.save_results(results, output_dir=output_dir)

        # Verify file was created
        assert os.path.exists(filepath)

        # Verify content
        with open(filepath, "r") as f:
            saved_data = json.load(f)

        assert saved_data["symbol"] == "TEST"
        assert saved_data["returns"]["total_return"] == 10.5

        # Verify summary file also created
        summary_path = os.path.join(output_dir, "backtest_summary.json")
        assert os.path.exists(summary_path)

    def test_print_summary(self, backtest_runner, capsys):
        """Test printing summary to console."""
        results = {
            "symbol": "TEST",
            "backtest_period": {
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "total_days": 252,
                "trading_years": 1.0,
            },
            "portfolio": {
                "initial_capital": 100000.0,
                "final_capital": 110000.0,
            },
            "returns": {
                "total_return": 10.0,
                "annual_return": 10.0,
                "total_pnl": 10000.0,
            },
            "risk_metrics": {
                "sharpe_ratio": 1.2,
                "sortino_ratio": 1.5,
                "calmar_ratio": 0.8,
                "max_drawdown": 5.0,
                "volatility": 15.0,
            },
            "trading": {
                "num_trades": 50,
                "winning_trades": 30,
                "losing_trades": 20,
                "win_rate": 60.0,
                "avg_pnl_per_trade": 200.0,
            },
        }

        backtest_runner.print_summary(results)

        captured = capsys.readouterr()
        assert "BACKTEST SUMMARY" in captured.out
        assert "TEST" in captured.out
        assert "10.0%" in captured.out  # Total return

    def test_prepare_features(self, backtest_runner, sample_data):
        """Test feature preparation."""
        # Mock scaler loading failure to use fresh normalization
        with patch.object(backtest_runner.data_processor, "load_scaler", side_effect=FileNotFoundError):
            sequences, targets, data = backtest_runner.prepare_features(sample_data)

            # Verify shapes
            assert len(sequences) > 0
            assert len(targets) == len(sequences)
            assert sequences.shape[1] == 60  # Default sequence length
            assert sequences.shape[2] == 4  # OHLC features

    def test_transaction_costs(self, backtest_runner):
        """Test that transaction costs are applied."""
        backtest_runner.transaction_cost = 0.01  # 1%
        backtest_runner.slippage = 0.01  # 1%

        price = 100.0
        date = pd.Timestamp("2023-01-01")

        initial_cash = backtest_runner.cash
        backtest_runner.execute_trade("buy", price, date, signal_strength=1.0)

        # Verify costs were applied (total cost > price * shares)
        if len(backtest_runner.trades) > 0:
            trade = backtest_runner.trades[0]
            expected_cost_per_share = price * (1 + backtest_runner.transaction_cost + backtest_runner.slippage)
            actual_cost_per_share = trade["cost"] / trade["shares"]

            assert abs(actual_cost_per_share - expected_cost_per_share) < 0.01

    def test_empty_portfolio_values(self, backtest_runner):
        """Test metrics calculation with no trading activity."""
        backtest_runner.portfolio_values = []
        backtest_runner.daily_returns = []
        backtest_runner.trades = []

        metrics = backtest_runner.calculate_metrics(100000.0)

        assert metrics["trading"]["num_trades"] == 0
        assert metrics["trading"]["win_rate"] == 0.0
        assert metrics["returns"]["total_return"] == 0.0

    @patch("src.backtesting.run_backtest.ModelEvaluator")
    def test_run_backtest_integration(self, mock_evaluator_class, backtest_runner, mock_models, sample_data):
        """Test full backtest run (integration-style test)."""
        # Mock evaluator
        mock_evaluator = Mock()
        mock_evaluator.predict_ensemble.return_value = np.array([105.0])
        mock_evaluator_class.return_value = mock_evaluator

        # Mock data processor methods
        backtest_runner.data_processor.create_sequences = Mock(
            return_value=(
                np.random.rand(10, 60, 4),  # sequences
                np.random.rand(10)  # targets
            )
        )

        # Run backtest
        results = backtest_runner.run_backtest(mock_models, sample_data)

        # Verify results structure
        assert isinstance(results, dict)
        assert "symbol" in results
        assert "returns" in results
        assert "risk_metrics" in results
        assert "trading" in results

    def test_different_initial_capitals(self):
        """Test backtest with different initial capital amounts."""
        runner1 = BacktestRunner("TEST", initial_capital=50000.0)
        runner2 = BacktestRunner("TEST", initial_capital=200000.0)

        assert runner1.cash == 50000.0
        assert runner2.cash == 200000.0

    def test_risk_manager_integration(self, backtest_runner):
        """Test integration with risk manager."""
        # Ensure risk manager is initialized
        assert backtest_runner.risk_manager is not None

        # Execute a trade (which uses risk manager internally)
        price = 100.0
        date = pd.Timestamp("2023-01-01")
        backtest_runner.execute_trade("buy", price, date, signal_strength=0.8)

        # Verify trade was executed with risk management
        if len(backtest_runner.trades) > 0:
            assert backtest_runner.trades[0]["shares"] > 0
