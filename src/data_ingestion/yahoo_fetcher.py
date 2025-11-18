"""Yahoo Finance data fetcher."""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List
from src.utils.logger import LoggerMixin
from src.utils.exceptions import DataFetchError


class YahooDataFetcher(LoggerMixin):
    """Fetch stock data from Yahoo Finance."""

    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "2y",
    ) -> pd.DataFrame:
        """Fetch OHLCV data for a symbol.

        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            period: Period if dates not specified (1y, 2y, 5y, max)

        Returns:
            DataFrame with OHLCV data

        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            self.logger.info(f"Fetching data for {symbol}")

            ticker = yf.Ticker(symbol)

            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
            else:
                data = ticker.history(period=period)

            if data.empty:
                raise DataFetchError(f"No data found for {symbol}")

            # Reset index and rename columns
            data = data.reset_index()
            data.columns = data.columns.str.lower()

            # Ensure required columns exist
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            if not all(col in data.columns for col in required_cols):
                raise DataFetchError(f"Missing required columns for {symbol}")

            self.logger.info(f"Fetched {len(data)} rows for {symbol}")
            return data

        except Exception as e:
            self.logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise DataFetchError(f"Failed to fetch data for {symbol}: {e}")

    def fetch_multiple(
        self, symbols: List[str], **kwargs
    ) -> dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols.

        Args:
            symbols: List of stock symbols
            **kwargs: Arguments passed to fetch_data

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.fetch_data(symbol, **kwargs)
            except DataFetchError as e:
                self.logger.warning(f"Skipping {symbol}: {e}")
        return results
