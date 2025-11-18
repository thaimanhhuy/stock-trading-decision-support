"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np


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
