"""Tests for YahooDataFetcher."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.data_ingestion.yahoo_fetcher import YahooDataFetcher
from src.utils.exceptions import DataFetchError


class TestYahooDataFetcher:
    """Tests for YahooDataFetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance."""
        return YahooDataFetcher()

    @pytest.fixture
    def mock_yfinance_data(self):
        """Create mock yfinance data."""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        data = pd.DataFrame({
            "Date": dates,
            "Open": [100.0] * 100,
            "High": [105.0] * 100,
            "Low": [95.0] * 100,
            "Close": [102.0] * 100,
            "Volume": [1000000] * 100,
        })
        data.set_index("Date", inplace=True)
        return data

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_data_success(self, mock_ticker, fetcher, mock_yfinance_data):
        """Test successful data fetch."""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_yfinance_data
        mock_ticker.return_value = mock_instance

        result = fetcher.fetch_data("AAPL", start_date="2023-01-01", end_date="2023-12-31")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 100
        assert "date" in result.columns
        assert "close" in result.columns
        mock_ticker.assert_called_once_with("AAPL")

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_data_empty_result(self, mock_ticker, fetcher):
        """Test fetch with empty result."""
        mock_instance = Mock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance

        with pytest.raises(DataFetchError, match="No data found"):
            fetcher.fetch_data("INVALID")

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_data_with_period(self, mock_ticker, fetcher, mock_yfinance_data):
        """Test fetch with period parameter."""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_yfinance_data
        mock_ticker.return_value = mock_instance

        result = fetcher.fetch_data("AAPL", period="1y")

        assert isinstance(result, pd.DataFrame)
        mock_instance.history.assert_called_once_with(period="1y")

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_data_exception(self, mock_ticker, fetcher):
        """Test fetch with exception."""
        mock_ticker.side_effect = Exception("Network error")

        with pytest.raises(DataFetchError, match="Failed to fetch data"):
            fetcher.fetch_data("AAPL")

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_multiple_success(self, mock_ticker, fetcher, mock_yfinance_data):
        """Test fetching multiple symbols."""
        mock_instance = Mock()
        mock_instance.history.return_value = mock_yfinance_data
        mock_ticker.return_value = mock_instance

        symbols = ["AAPL", "GOOGL", "MSFT"]
        results = fetcher.fetch_multiple(symbols, period="1y")

        assert len(results) == 3
        assert all(symbol in results for symbol in symbols)
        assert all(isinstance(df, pd.DataFrame) for df in results.values())

    @patch("src.data_ingestion.yahoo_fetcher.yf.Ticker")
    def test_fetch_multiple_partial_failure(self, mock_ticker, fetcher, mock_yfinance_data):
        """Test fetching multiple symbols with partial failure."""
        def side_effect(symbol):
            mock_instance = Mock()
            if symbol == "INVALID":
                mock_instance.history.return_value = pd.DataFrame()
            else:
                mock_instance.history.return_value = mock_yfinance_data
            return mock_instance

        mock_ticker.side_effect = side_effect

        symbols = ["AAPL", "INVALID", "GOOGL"]
        results = fetcher.fetch_multiple(symbols, period="1y")

        assert len(results) == 2
        assert "AAPL" in results
        assert "GOOGL" in results
        assert "INVALID" not in results
