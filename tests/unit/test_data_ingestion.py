"""Tests for data ingestion modules."""

import pytest
import pandas as pd
import numpy as np
from src.data_ingestion.data_validator import DataValidator
from src.utils.exceptions import DataValidationError


class TestDataValidator:
    """Tests for DataValidator."""

    def test_validate_valid_data(self, sample_ohlcv_data, sample_symbol):
        """Test validation of valid data."""
        validator = DataValidator()
        result = validator.validate(sample_ohlcv_data, sample_symbol)
        assert len(result) > 0
        assert "close" in result.columns
        assert "open" in result.columns
        assert "high" in result.columns
        assert "low" in result.columns

    def test_validate_missing_columns(self, sample_symbol):
        """Test validation with missing columns."""
        validator = DataValidator()
        invalid_data = pd.DataFrame({"date": ["2023-01-01"], "close": [100]})

        with pytest.raises(DataValidationError, match="Missing columns"):
            validator.validate(invalid_data, sample_symbol)

    def test_validate_negative_prices(self, sample_symbol):
        """Test validation with negative prices."""
        validator = DataValidator()
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        invalid_data = pd.DataFrame({
            "date": dates,
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [-95.0] * 10,  # Negative price
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
        })

        with pytest.raises(DataValidationError, match="Negative prices detected"):
            validator.validate(invalid_data, sample_symbol)

    def test_validate_high_less_than_low(self, sample_symbol):
        """Test validation with high < low."""
        validator = DataValidator()
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        invalid_data = pd.DataFrame({
            "date": dates,
            "open": [100.0] * 10,
            "high": [95.0] * 10,  # High less than low
            "low": [105.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
        })

        with pytest.raises(DataValidationError, match="High price less than low price"):
            validator.validate(invalid_data, sample_symbol)

    def test_validate_too_many_missing_values(self, sample_symbol):
        """Test validation with too many missing values."""
        validator = DataValidator()
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        invalid_data = pd.DataFrame({
            "date": dates,
            "open": [np.nan] * 10 + [100.0] * 90,  # 10% missing
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
        })

        with pytest.raises(DataValidationError, match="Too many missing values"):
            validator.validate(invalid_data, sample_symbol)

    def test_validate_fills_missing_values(self, sample_symbol):
        """Test that validator fills small amounts of missing values."""
        validator = DataValidator()
        dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
        data_with_nan = pd.DataFrame({
            "date": dates,
            "open": [np.nan, 100.0] + [100.0] * 98,  # 1% missing
            "high": [105.0] * 100,
            "low": [95.0] * 100,
            "close": [102.0] * 100,
            "volume": [1000000] * 100,
        })

        result = validator.validate(data_with_nan, sample_symbol)
        assert result["open"].isna().sum() == 0  # All NaN should be filled

    def test_validate_large_price_movements(self, sample_symbol, caplog):
        """Test validation with large price movements (logs warning)."""
        validator = DataValidator()
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        data = pd.DataFrame({
            "date": dates,
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [100.0, 200.0] + [100.0] * 8,  # 100% jump
            "volume": [1000000] * 10,
        })

        result = validator.validate(data, sample_symbol)
        # Should not raise exception, just log warning
        assert len(result) > 0
