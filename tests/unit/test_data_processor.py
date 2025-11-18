"""Tests for DataProcessor."""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src.preprocessing.data_processor import DataProcessor


class TestDataProcessor:
    """Tests for DataProcessor."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def processor(self, temp_dir):
        """Create processor instance."""
        with patch("src.preprocessing.data_processor.get_settings") as mock_settings:
            mock_config = MagicMock()
            mock_config.model_scaler_path = temp_dir
            mock_settings.return_value = mock_config
            return DataProcessor()

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
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

    def test_process_data(self, processor, sample_data):
        """Test data processing."""
        result = processor.process(sample_data, "TEST")

        assert isinstance(result, pd.DataFrame)
        assert len(result) < len(sample_data)  # Some rows dropped due to NaN
        # Check that indicators were added
        assert "sma_20" in result.columns
        assert "rsi" in result.columns
        assert "macd" in result.columns

    def test_normalize_fit(self, processor, sample_data):
        """Test normalization with fitting."""
        processed_data = processor.process(sample_data, "TEST")
        normalized = processor.normalize(processed_data, fit=True)

        # Check that numeric columns are normalized
        numeric_cols = normalized.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != "date":
                values = normalized[col].values
                assert values.min() >= 0
                assert values.max() <= 1

    def test_normalize_transform(self, processor, sample_data):
        """Test normalization without fitting."""
        processed_data = processor.process(sample_data, "TEST")

        # First fit
        _ = processor.normalize(processed_data.copy(), fit=True)

        # Then transform
        normalized = processor.normalize(processed_data.copy(), fit=False)

        assert isinstance(normalized, pd.DataFrame)

    def test_save_and_load_scaler(self, processor, sample_data, temp_dir):
        """Test saving and loading scaler."""
        processed_data = processor.process(sample_data, "TEST")
        _ = processor.normalize(processed_data, fit=True)

        symbol = "TEST"
        filepath = processor.save_scaler(symbol)

        assert os.path.exists(filepath)

        # Create new processor and load scaler
        with patch("src.preprocessing.data_processor.get_settings") as mock_settings:
            mock_config = MagicMock()
            mock_config.model_scaler_path = temp_dir
            mock_settings.return_value = mock_config
            new_processor = DataProcessor()

        new_processor.load_scaler(symbol)
        # Scaler should be loaded successfully

    def test_load_scaler_not_found(self, processor):
        """Test loading non-existent scaler."""
        with pytest.raises(FileNotFoundError, match="Scaler not found"):
            processor.load_scaler("NONEXISTENT")

    def test_create_sequences(self, processor):
        """Test sequence creation for LSTM/GRU."""
        # Create normalized data
        data = np.random.randn(100, 5)
        sequence_length = 60

        X, y = processor.create_sequences(data, sequence_length=sequence_length, target_column_idx=0)

        assert X.shape[0] == 100 - sequence_length
        assert X.shape[1] == sequence_length
        assert X.shape[2] == 5
        assert y.shape[0] == 100 - sequence_length

    def test_create_sequences_target_column(self, processor):
        """Test sequence creation with different target column."""
        data = np.random.randn(100, 5)
        sequence_length = 60
        target_column_idx = 2

        X, y = processor.create_sequences(data, sequence_length=sequence_length, target_column_idx=target_column_idx)

        # Verify target is from correct column
        for i in range(len(X)):
            expected_target = data[i + sequence_length, target_column_idx]
            assert y[i] == expected_target

    def test_process_drops_nan(self, processor, sample_data):
        """Test that process drops NaN values."""
        result = processor.process(sample_data, "TEST")

        # Verify no NaN values in result
        assert not result.isna().any().any()

    def test_normalize_excludes_date_column(self, processor):
        """Test that normalization excludes date column."""
        data = pd.DataFrame({
            "date": pd.date_range(start="2023-01-01", periods=10, freq="D"),
            "value1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "value2": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        })

        normalized = processor.normalize(data, fit=True)

        # Date column should be unchanged (if numeric)
        # Value columns should be normalized
        assert normalized["value1"].min() == 0.0
        assert normalized["value1"].max() == 1.0
