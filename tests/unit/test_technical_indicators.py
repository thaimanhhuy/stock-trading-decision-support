"""Tests for TechnicalIndicators."""

import pytest
import pandas as pd
import numpy as np
from src.preprocessing.technical_indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Tests for TechnicalIndicators."""

    @pytest.fixture
    def indicators(self):
        """Create indicators instance."""
        return TechnicalIndicators()

    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data."""
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        np.random.seed(42)
        close_prices = 100 + np.random.randn(100).cumsum()

        data = pd.DataFrame({
            "date": dates,
            "open": close_prices + np.random.randn(100) * 0.5,
            "high": close_prices + np.abs(np.random.randn(100)) * 2,
            "low": close_prices - np.abs(np.random.randn(100)) * 2,
            "close": close_prices,
            "volume": np.random.randint(1000000, 10000000, 100),
        })
        return data

    def test_calculate_sma(self, indicators, sample_price_data):
        """Test SMA calculation."""
        sma = indicators.calculate_sma(sample_price_data, period=20)

        assert isinstance(sma, pd.Series)
        assert len(sma) == len(sample_price_data)
        assert sma.isna().sum() == 19  # First 19 values should be NaN

    def test_calculate_ema(self, indicators, sample_price_data):
        """Test EMA calculation."""
        ema = indicators.calculate_ema(sample_price_data, period=20)

        assert isinstance(ema, pd.Series)
        assert len(ema) == len(sample_price_data)
        assert not ema.isna().all()

    def test_calculate_rsi(self, indicators, sample_price_data):
        """Test RSI calculation."""
        rsi = indicators.calculate_rsi(sample_price_data, period=14)

        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(sample_price_data)
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()

    def test_calculate_macd(self, indicators, sample_price_data):
        """Test MACD calculation."""
        macd_data = indicators.calculate_macd(sample_price_data)

        assert isinstance(macd_data, pd.DataFrame)
        assert "macd" in macd_data.columns
        assert "signal" in macd_data.columns
        assert "histogram" in macd_data.columns
        assert len(macd_data) == len(sample_price_data)

    def test_calculate_bollinger_bands(self, indicators, sample_price_data):
        """Test Bollinger Bands calculation."""
        bb_data = indicators.calculate_bollinger_bands(sample_price_data, period=20)

        assert isinstance(bb_data, pd.DataFrame)
        assert "bb_middle" in bb_data.columns
        assert "bb_upper" in bb_data.columns
        assert "bb_lower" in bb_data.columns

        # Upper band should be >= middle, middle >= lower
        valid_idx = ~bb_data["bb_middle"].isna()
        assert (bb_data.loc[valid_idx, "bb_upper"] >= bb_data.loc[valid_idx, "bb_middle"]).all()
        assert (bb_data.loc[valid_idx, "bb_middle"] >= bb_data.loc[valid_idx, "bb_lower"]).all()

    def test_calculate_atr(self, indicators, sample_price_data):
        """Test ATR calculation."""
        atr = indicators.calculate_atr(sample_price_data, period=14)

        assert isinstance(atr, pd.Series)
        assert len(atr) == len(sample_price_data)
        # ATR should be positive
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()

    def test_add_all_indicators(self, indicators, sample_price_data):
        """Test adding all indicators."""
        result = indicators.add_all_indicators(sample_price_data)

        assert isinstance(result, pd.DataFrame)

        # Check that all expected columns are present
        expected_cols = [
            "sma_20", "sma_50", "ema_12", "ema_26",
            "rsi", "macd", "macd_signal",
            "bb_middle", "bb_upper", "bb_lower",
            "atr", "returns", "log_returns"
        ]

        for col in expected_cols:
            assert col in result.columns

    def test_sma_custom_column(self, indicators, sample_price_data):
        """Test SMA with custom column."""
        sma = indicators.calculate_sma(sample_price_data, period=10, column="open")

        assert isinstance(sma, pd.Series)
        assert len(sma) == len(sample_price_data)

    def test_rsi_extreme_values(self, indicators):
        """Test RSI with extreme values."""
        # Create data with constant increase
        data = pd.DataFrame({
            "close": [100 + i for i in range(50)]
        })

        rsi = indicators.calculate_rsi(data, period=14)
        valid_rsi = rsi.dropna()

        # With constant increase, RSI should approach 100
        assert valid_rsi.iloc[-1] > 80

    def test_macd_crossover(self, indicators, sample_price_data):
        """Test MACD crossover detection."""
        macd_data = indicators.calculate_macd(sample_price_data)

        # Check histogram is difference between MACD and signal
        valid_idx = ~macd_data["macd"].isna() & ~macd_data["signal"].isna()
        expected_histogram = macd_data.loc[valid_idx, "macd"] - macd_data.loc[valid_idx, "signal"]
        actual_histogram = macd_data.loc[valid_idx, "histogram"]

        np.testing.assert_allclose(expected_histogram, actual_histogram, rtol=1e-5)
