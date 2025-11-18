"""Tests for DataStorage."""

import pytest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src.data_ingestion.data_storage import DataStorage


class TestDataStorage:
    """Tests for DataStorage."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def storage(self, temp_dir):
        """Create storage instance with temp directories."""
        with patch("src.data_ingestion.data_storage.get_settings") as mock_settings:
            mock_config = MagicMock()
            mock_config.data_raw_path = os.path.join(temp_dir, "raw")
            mock_config.data_processed_path = os.path.join(temp_dir, "processed")
            mock_config.data_features_path = os.path.join(temp_dir, "features")
            mock_settings.return_value = mock_config
            return DataStorage()

    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        return pd.DataFrame({
            "date": pd.date_range(start="2023-01-01", periods=10, freq="D"),
            "open": [100.0] * 10,
            "high": [105.0] * 10,
            "low": [95.0] * 10,
            "close": [102.0] * 10,
            "volume": [1000000] * 10,
        })

    def test_save_and_load_raw(self, storage, sample_data):
        """Test saving and loading raw data."""
        symbol = "TEST"
        filepath = storage.save_raw(sample_data, symbol)

        assert os.path.exists(filepath)

        loaded_data = storage.load_raw(symbol)
        assert len(loaded_data) == len(sample_data)
        assert list(loaded_data.columns) == list(sample_data.columns)

    def test_load_raw_not_found(self, storage):
        """Test loading non-existent raw data."""
        with pytest.raises(FileNotFoundError, match="Raw data not found"):
            storage.load_raw("NONEXISTENT")

    def test_save_and_load_processed(self, storage, sample_data):
        """Test saving and loading processed data."""
        symbol = "TEST"
        filepath = storage.save_processed(sample_data, symbol)

        assert os.path.exists(filepath)

        loaded_data = storage.load_processed(symbol)
        assert len(loaded_data) == len(sample_data)

    def test_load_processed_not_found(self, storage):
        """Test loading non-existent processed data."""
        with pytest.raises(FileNotFoundError, match="Processed data not found"):
            storage.load_processed("NONEXISTENT")

    def test_save_and_load_features(self, storage, sample_data):
        """Test saving and loading features."""
        symbol = "TEST"
        filepath = storage.save_features(sample_data, symbol)

        assert os.path.exists(filepath)

        loaded_data = storage.load_features(symbol)
        assert len(loaded_data) == len(sample_data)

    def test_load_features_not_found(self, storage):
        """Test loading non-existent features."""
        with pytest.raises(FileNotFoundError, match="Features not found"):
            storage.load_features("NONEXISTENT")

    def test_directory_creation(self, temp_dir):
        """Test that directories are created on initialization."""
        with patch("src.data_ingestion.data_storage.get_settings") as mock_settings:
            mock_config = MagicMock()
            mock_config.data_raw_path = os.path.join(temp_dir, "new_raw")
            mock_config.data_processed_path = os.path.join(temp_dir, "new_processed")
            mock_config.data_features_path = os.path.join(temp_dir, "new_features")
            mock_settings.return_value = mock_config

            storage = DataStorage()

            assert os.path.exists(storage.raw_path)
            assert os.path.exists(storage.processed_path)
            assert os.path.exists(storage.features_path)
