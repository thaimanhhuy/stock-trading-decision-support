"""Tests for data ingestion modules."""

import pytest
from src.data_ingestion.data_validator import DataValidator


class TestDataValidator:
    """Tests for DataValidator."""

    def test_validate_valid_data(self, sample_ohlcv_data, sample_symbol):
        """Test validation of valid data."""
        validator = DataValidator()
        result = validator.validate(sample_ohlcv_data, sample_symbol)
        assert len(result) > 0
        assert "close" in result.columns

    def test_validate_missing_columns(self, sample_symbol):
        """Test validation with missing columns."""
        import pandas as pd

        validator = DataValidator()
        invalid_data = pd.DataFrame({"date": ["2023-01-01"], "close": [100]})

        with pytest.raises(Exception):
            validator.validate(invalid_data, sample_symbol)
