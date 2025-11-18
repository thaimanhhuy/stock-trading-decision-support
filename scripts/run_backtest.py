#!/usr/bin/env python3
"""Run backtesting."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backtesting.backtest_engine import BacktestEngine
from src.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run backtest")
    parser.add_argument("--symbol", required=True, help="Stock symbol")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--initial-capital", type=float, default=100000.0, help="Initial capital")

    args = parser.parse_args()

    try:
        logger.info(f"Running backtest for {args.symbol}")

        engine = BacktestEngine(
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end,
            initial_capital=args.initial_capital,
        )

        # Placeholder - would load data and signals
        import pandas as pd

        data = pd.DataFrame()
        signals = pd.DataFrame()

        results = engine.run(data, signals)

        logger.info("Backtest Results:")
        logger.info(f"Total Return: {results['total_return']:.2%}")
        logger.info(f"Number of Trades: {results['num_trades']}")

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
