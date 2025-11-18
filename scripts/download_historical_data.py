#!/usr/bin/env python3
"""Download historical stock data."""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion.yahoo_fetcher import YahooDataFetcher
from src.data_ingestion.data_validator import DataValidator
from src.data_ingestion.data_storage import DataStorage
from src.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download historical stock data")
    parser.add_argument("--symbols", required=True, help="Comma-separated list of symbols")
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--period", default="2y", help="Period (1y, 2y, 5y, max)")

    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",")]

    fetcher = YahooDataFetcher()
    validator = DataValidator()
    storage = DataStorage()

    for symbol in symbols:
        try:
            logger.info(f"Processing {symbol}")

            # Fetch data
            data = fetcher.fetch_data(symbol, args.start, args.end, args.period)

            # Validate
            data = validator.validate(data, symbol)

            # Save
            storage.save_raw(data, symbol)

            logger.info(f"Successfully downloaded and saved {symbol}")

        except Exception as e:
            logger.error(f"Failed to process {symbol}: {e}")

    logger.info("Data download complete")


if __name__ == "__main__":
    main()
