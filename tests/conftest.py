"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from typing import Tuple


@pytest.fixture
def sample_ohlcv_data():
    """Sample OHLCV data for testing."""
    dates = pd.date_range(start="2023-01-01", periods=100, freq="D")
    data = pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(100, 110, 100),
        "high": np.random.uniform(105, 115, 100),
        "low": np.random.uniform(95, 105, 100),
        "close": np.random.uniform(100, 110, 100),
        "volume": np.random.randint(1000000, 10000000, 100),
    })
    return data


@pytest.fixture
def sample_symbol():
    """Sample stock symbol."""
    return "TEST"


@pytest.fixture
def sample_training_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Sample training data for LSTM/GRU models.

    Returns:
        Tuple of (X_train, y_train, X_test, y_test)
    """
    np.random.seed(42)
    X_train = np.random.randn(200, 60, 5)
    y_train = np.random.randn(200)
    X_test = np.random.randn(50, 60, 5)
    y_test = np.random.randn(50)
    return X_train, y_train, X_test, y_test


@pytest.fixture
def sample_sequences():
    """Sample sequence data for model testing."""
    np.random.seed(42)
    sequence_length = 60
    n_features = 5
    n_samples = 100

    X = np.random.randn(n_samples, sequence_length, n_features)
    y = np.random.randn(n_samples)

    return X, y


@pytest.fixture
def sample_us_symbols():
    """Sample US stock symbols."""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]


@pytest.fixture
def sample_vn_symbols():
    """Sample Vietnamese stock symbols."""
    return ["VCB.VN", "FPT.VN", "CTG.VN", "BID.VN", "MBB.VN"]


@pytest.fixture
def mock_model_config():
    """Mock model configuration."""
    return {
        "lstm": {
            "sequence_length": 60,
            "n_features": 5,
            "batch_size": 32,
            "epochs": 100,
            "patience": 15,
        },
        "gru": {
            "sequence_length": 60,
            "n_features": 5,
            "batch_size": 32,
            "epochs": 100,
            "patience": 15,
        }
    }
