#!/usr/bin/env python3
"""
Backtest script for evaluating trained models.

This script:
1. Loads trained models (LSTM, GRU)
2. Runs backtest on historical data using walk-forward validation
3. Calculates performance metrics (annual return, max drawdown, Sharpe, win rate)
4. Saves results to results/backtest_summary.json

Usage:
    python -m src.backtesting.run_backtest --symbol AAPL --start-date 2023-01-01 --end-date 2023-12-31
    python -m src.backtesting.run_backtest --symbol AAPL --period 1y
    python -m src.backtesting.run_backtest --config config/backtest_config.yaml
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_ingestion.yahoo_fetcher import YahooDataFetcher
from src.preprocessing.data_processor import DataProcessor
from src.models.lstm_model import LSTMModel
from src.models.gru_model import GRUModel
from src.models.model_evaluator import ModelEvaluator
from src.trading_engine.signal_generator import SignalGenerator
from src.trading_engine.risk_manager import RiskManager
from src.backtesting.performance_metrics import PerformanceMetrics
from src.config.settings import get_settings
from src.utils.logger import LoggerMixin
from src.utils.constants import (
    TRADING_DAYS_PER_YEAR,
    DEFAULT_SEQUENCE_LENGTH,
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_HOLD,
)


class BacktestRunner(LoggerMixin):
    """Run comprehensive backtest with trained models."""

    def __init__(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "2y",
        initial_capital: float = 100000.0,
        transaction_cost: float = 0.001,  # 0.1% per trade
        slippage: float = 0.0005,  # 0.05% slippage
    ):
        """Initialize backtest runner.

        Args:
            symbol: Stock symbol to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period if dates not specified (1y, 2y, 5y)
            initial_capital: Initial portfolio capital
            transaction_cost: Transaction cost as percentage
            slippage: Slippage as percentage
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

        self.settings = get_settings()
        self.data_fetcher = YahooDataFetcher()
        self.data_processor = DataProcessor()
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.metrics_calculator = PerformanceMetrics()

        # Portfolio tracking
        self.portfolio_values = []
        self.cash = initial_capital
        self.position = 0  # Number of shares held
        self.trades = []
        self.daily_returns = []

    def load_models(self) -> Dict[str, Any]:
        """Load trained models from disk.

        Returns:
            Dictionary of loaded models
        """
        self.logger.info(f"Loading models for {self.symbol}")
        models = {}

        # Model file paths
        model_dir = self.settings.model_saved_path
        lstm_path = os.path.join(model_dir, f"{self.symbol}_lstm.h5")
        gru_path = os.path.join(model_dir, f"{self.symbol}_gru.h5")

        # Load LSTM model
        if os.path.exists(lstm_path):
            try:
                lstm_model = LSTMModel(self.symbol)
                lstm_model.load(lstm_path)
                models["lstm"] = lstm_model
                self.logger.info(f"Loaded LSTM model from {lstm_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load LSTM model: {e}")

        # Load GRU model
        if os.path.exists(gru_path):
            try:
                gru_model = GRUModel(self.symbol)
                gru_model.load(gru_path)
                models["gru"] = gru_model
                self.logger.info(f"Loaded GRU model from {gru_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load GRU model: {e}")

        if not models:
            raise FileNotFoundError(
                f"No trained models found for {self.symbol}. "
                f"Please train models first."
            )

        self.logger.info(f"Loaded {len(models)} models: {list(models.keys())}")
        return models

    def load_data(self) -> pd.DataFrame:
        """Load and preprocess historical data.

        Returns:
            Processed DataFrame with features
        """
        self.logger.info(f"Loading data for {self.symbol}")

        # Fetch data
        if self.start_date and self.end_date:
            data = self.data_fetcher.fetch_data(
                self.symbol, start_date=self.start_date, end_date=self.end_date
            )
        else:
            data = self.data_fetcher.fetch_data(self.symbol, period=self.period)

        # Process data and add technical indicators
        data = self.data_processor.process(data, self.symbol)

        self.logger.info(f"Loaded {len(data)} days of data")
        return data

    def prepare_features(
        self, data: pd.DataFrame, lookback: int = DEFAULT_SEQUENCE_LENGTH
    ) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """Prepare features for model predictions.

        Args:
            data: Processed data with technical indicators
            lookback: Lookback period for sequences

        Returns:
            Tuple of (sequences, targets, data)
        """
        # Select features (OHLC as per thesis)
        feature_cols = ["open", "high", "low", "close"]
        features = data[feature_cols].values

        # Normalize using saved scaler
        try:
            self.data_processor.load_scaler(self.symbol)
            features_normalized = self.data_processor.scaler.transform(features)
        except FileNotFoundError:
            self.logger.warning(
                f"Scaler not found for {self.symbol}, using fresh normalization"
            )
            features_normalized = features

        # Create sequences for LSTM/GRU
        sequences, targets = self.data_processor.create_sequences(
            features_normalized, sequence_length=lookback, target_column_idx=3
        )

        return sequences, targets, data

    def execute_trade(
        self,
        signal: str,
        price: float,
        date: pd.Timestamp,
        signal_strength: float = 1.0,
    ) -> None:
        """Execute a trade based on signal.

        Args:
            signal: Trading signal (BUY, SELL, HOLD)
            price: Current price
            date: Trade date
            signal_strength: Signal strength (0-1)
        """
        if signal == SIGNAL_HOLD:
            return

        # Calculate position size using risk manager
        risk_params = self.risk_manager.calculate_position_size(
            capital=self.cash + (self.position * price),
            price=price,
            volatility=0.02,  # Simplified
            signal_strength=signal_strength,
        )

        shares_to_trade = risk_params["shares"]

        if signal == SIGNAL_BUY and self.cash > 0:
            # Buy signal
            max_shares = int(self.cash / (price * (1 + self.transaction_cost + self.slippage)))
            shares = min(shares_to_trade, max_shares)

            if shares > 0:
                cost = shares * price * (1 + self.transaction_cost + self.slippage)
                self.cash -= cost
                self.position += shares

                self.trades.append(
                    {
                        "date": date,
                        "action": "BUY",
                        "price": price,
                        "shares": shares,
                        "cost": cost,
                        "pnl": 0,
                    }
                )
                self.logger.debug(f"BUY {shares} shares at ${price:.2f}")

        elif signal == SIGNAL_SELL and self.position > 0:
            # Sell signal
            shares = min(shares_to_trade, self.position)

            if shares > 0:
                revenue = shares * price * (1 - self.transaction_cost - self.slippage)
                self.cash += revenue

                # Calculate PnL (simplified - assumes FIFO)
                avg_buy_price = (self.initial_capital - self.cash) / self.position if self.position > 0 else price
                pnl = (price - avg_buy_price) * shares

                self.position -= shares

                self.trades.append(
                    {
                        "date": date,
                        "action": "SELL",
                        "price": price,
                        "shares": shares,
                        "revenue": revenue,
                        "pnl": pnl,
                    }
                )
                self.logger.debug(f"SELL {shares} shares at ${price:.2f}, PnL: ${pnl:.2f}")

    def run_backtest(self, models: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """Run walk-forward backtest.

        Args:
            models: Dictionary of trained models
            data: Historical price data with features

        Returns:
            Backtest results
        """
        self.logger.info(f"Running backtest for {self.symbol}")

        # Prepare features
        sequences, targets, data_with_features = self.prepare_features(data)

        # Calculate offset (sequence length)
        offset = DEFAULT_SEQUENCE_LENGTH

        # Initialize model evaluator for ensemble predictions
        evaluator = ModelEvaluator(self.symbol)

        # Walk-forward through time
        for i in range(len(sequences)):
            current_idx = i + offset
            if current_idx >= len(data_with_features):
                break

            current_date = data_with_features.iloc[current_idx]["date"]
            current_price = data_with_features.iloc[current_idx]["close"]

            # Get current sequence
            X_current = sequences[i : i + 1]

            # Generate ensemble prediction
            try:
                # Predict with deep learning models (LSTM/GRU)
                dl_models = {
                    k: v for k, v in models.items() if k in ["lstm", "gru"]
                }

                if dl_models:
                    prediction = evaluator.predict_ensemble(dl_models, X_current)[0]
                else:
                    # Fallback to current price if no DL models
                    prediction = current_price

                # Denormalize prediction if scaler was used
                if hasattr(self.data_processor.scaler, "data_min_"):
                    # Denormalize (close is index 3 in features)
                    close_min = self.data_processor.scaler.data_min_[3]
                    close_max = self.data_processor.scaler.data_max_[3]
                    prediction = prediction * (close_max - close_min) + close_min

            except Exception as e:
                self.logger.warning(f"Prediction failed at {current_date}: {e}")
                prediction = current_price

            # Generate trading signal
            signal_data = self.signal_generator.generate_signal(
                prediction=prediction,
                current_price=current_price,
                technical_data=data_with_features.iloc[current_idx],
            )

            # Execute trade
            self.execute_trade(
                signal=signal_data["signal"],
                price=current_price,
                date=current_date,
                signal_strength=signal_data["strength"],
            )

            # Update portfolio value
            portfolio_value = self.cash + (self.position * current_price)
            self.portfolio_values.append(portfolio_value)

            # Calculate daily return
            if len(self.portfolio_values) > 1:
                daily_return = (
                    self.portfolio_values[-1] - self.portfolio_values[-2]
                ) / self.portfolio_values[-2]
                self.daily_returns.append(daily_return)

        # Calculate final portfolio value
        final_price = data_with_features.iloc[-1]["close"]
        final_value = self.cash + (self.position * final_price)

        self.logger.info(f"Backtest complete. Final value: ${final_value:,.2f}")

        return self.calculate_metrics(final_value)

    def calculate_metrics(self, final_value: float) -> Dict[str, Any]:
        """Calculate performance metrics.

        Args:
            final_value: Final portfolio value

        Returns:
            Dictionary of metrics
        """
        # Total return
        total_return = (final_value - self.initial_capital) / self.initial_capital

        # Annual return (CAGR)
        n_days = len(self.portfolio_values)
        years = n_days / TRADING_DAYS_PER_YEAR
        annual_return = (
            (final_value / self.initial_capital) ** (1 / years) - 1 if years > 0 else 0
        )

        # Sharpe ratio
        returns_array = np.array(self.daily_returns)
        sharpe_ratio = self.metrics_calculator.calculate_sharpe_ratio(returns_array)

        # Max drawdown
        portfolio_array = np.array(self.portfolio_values)
        max_drawdown = self.metrics_calculator.calculate_max_drawdown(portfolio_array)

        # Win rate
        win_rate = self.metrics_calculator._calculate_win_rate(self.trades)

        # Additional metrics
        num_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.get("pnl", 0) > 0)
        losing_trades = sum(1 for t in self.trades if t.get("pnl", 0) < 0)

        # Average profit/loss
        total_pnl = sum(t.get("pnl", 0) for t in self.trades)
        avg_pnl = total_pnl / num_trades if num_trades > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns_array[returns_array < 0]
        downside_std = np.std(downside_returns) * np.sqrt(TRADING_DAYS_PER_YEAR)
        sortino_ratio = (
            (annual_return - 0.04) / downside_std if downside_std > 0 else 0
        )

        # Calmar ratio (return / max drawdown)
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

        metrics = {
            "symbol": self.symbol,
            "backtest_period": {
                "start_date": self.start_date or f"Last {self.period}",
                "end_date": self.end_date or datetime.now().strftime("%Y-%m-%d"),
                "total_days": n_days,
                "trading_years": round(years, 2),
            },
            "portfolio": {
                "initial_capital": self.initial_capital,
                "final_capital": final_value,
                "cash": self.cash,
                "position_shares": self.position,
            },
            "returns": {
                "total_return": round(total_return * 100, 2),  # Percentage
                "annual_return": round(annual_return * 100, 2),  # Percentage
                "total_pnl": round(total_pnl, 2),
            },
            "risk_metrics": {
                "sharpe_ratio": round(sharpe_ratio, 3),
                "sortino_ratio": round(sortino_ratio, 3),
                "calmar_ratio": round(calmar_ratio, 3),
                "max_drawdown": round(max_drawdown * 100, 2),  # Percentage
                "volatility": round(np.std(returns_array) * np.sqrt(TRADING_DAYS_PER_YEAR) * 100, 2),
            },
            "trading": {
                "num_trades": num_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate * 100, 2),  # Percentage
                "avg_pnl_per_trade": round(avg_pnl, 2),
            },
            "timestamp": datetime.now().isoformat(),
        }

        return metrics

    def save_results(self, results: Dict[str, Any], output_dir: str = "results") -> str:
        """Save backtest results to JSON file.

        Args:
            results: Backtest results
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_{self.symbol}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)

        # Save to JSON
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Saved backtest results to {filepath}")

        # Also save as backtest_summary.json (latest)
        summary_path = os.path.join(output_dir, "backtest_summary.json")
        with open(summary_path, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Saved summary to {summary_path}")

        return filepath

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print backtest summary to console.

        Args:
            results: Backtest results
        """
        print("\n" + "=" * 80)
        print(f"BACKTEST SUMMARY - {results['symbol']}")
        print("=" * 80)
        print(f"\nPeriod: {results['backtest_period']['start_date']} to {results['backtest_period']['end_date']}")
        print(f"Trading Days: {results['backtest_period']['total_days']} ({results['backtest_period']['trading_years']} years)")

        print("\n--- Portfolio Performance ---")
        print(f"Initial Capital:  ${results['portfolio']['initial_capital']:>12,.2f}")
        print(f"Final Capital:    ${results['portfolio']['final_capital']:>12,.2f}")
        print(f"Total Return:     {results['returns']['total_return']:>12.2f}%")
        print(f"Annual Return:    {results['returns']['annual_return']:>12.2f}%")
        print(f"Total P&L:        ${results['returns']['total_pnl']:>12,.2f}")

        print("\n--- Risk Metrics ---")
        print(f"Sharpe Ratio:     {results['risk_metrics']['sharpe_ratio']:>12.3f}")
        print(f"Sortino Ratio:    {results['risk_metrics']['sortino_ratio']:>12.3f}")
        print(f"Calmar Ratio:     {results['risk_metrics']['calmar_ratio']:>12.3f}")
        print(f"Max Drawdown:     {results['risk_metrics']['max_drawdown']:>12.2f}%")
        print(f"Volatility:       {results['risk_metrics']['volatility']:>12.2f}%")

        print("\n--- Trading Activity ---")
        print(f"Total Trades:     {results['trading']['num_trades']:>12}")
        print(f"Winning Trades:   {results['trading']['winning_trades']:>12}")
        print(f"Losing Trades:    {results['trading']['losing_trades']:>12}")
        print(f"Win Rate:         {results['trading']['win_rate']:>12.2f}%")
        print(f"Avg P&L/Trade:    ${results['trading']['avg_pnl_per_trade']:>12,.2f}")

        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point for backtest script."""
    parser = argparse.ArgumentParser(
        description="Run backtest on trained stock prediction models"
    )
    parser.add_argument(
        "--symbol", type=str, default="AAPL", help="Stock symbol (default: AAPL)"
    )
    parser.add_argument(
        "--start-date", type=str, help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date", type=str, help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--period", type=str, default="1y", help="Period if dates not specified (default: 1y)"
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=100000.0,
        help="Initial capital (default: 100000)",
    )
    parser.add_argument(
        "--transaction-cost",
        type=float,
        default=0.001,
        help="Transaction cost as percentage (default: 0.001)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory (default: results)",
    )

    args = parser.parse_args()

    # Create backtest runner
    runner = BacktestRunner(
        symbol=args.symbol,
        start_date=args.start_date,
        end_date=args.end_date,
        period=args.period,
        initial_capital=args.initial_capital,
        transaction_cost=args.transaction_cost,
    )

    try:
        # Load models
        models = runner.load_models()

        # Load data
        data = runner.load_data()

        # Run backtest
        results = runner.run_backtest(models, data)

        # Save results
        runner.save_results(results, output_dir=args.output_dir)

        # Print summary
        runner.print_summary(results)

        return 0

    except Exception as e:
        print(f"Error running backtest: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
