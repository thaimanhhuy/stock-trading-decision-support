"""Tests for SlidingWindowGenerator."""

import pytest
import numpy as np
from src.preprocessing.sliding_window import SlidingWindowGenerator


class TestSlidingWindowGenerator:
    """Tests for SlidingWindowGenerator."""

    @pytest.fixture
    def generator(self):
        """Create generator instance with default parameters."""
        return SlidingWindowGenerator(sequence_length=60, prediction_horizon=1)

    def test_create_sequences_basic(self, generator):
        """Test basic sequence creation."""
        data = np.arange(100).reshape(-1, 1)

        X, y = generator.create_sequences(data, target_column_idx=0)

        expected_samples = 100 - 60 - 1 + 1
        assert X.shape == (expected_samples, 60, 1)
        assert y.shape == (expected_samples,)

    def test_create_sequences_multidimensional(self, generator):
        """Test sequence creation with multidimensional data."""
        data = np.random.randn(100, 5)

        X, y = generator.create_sequences(data, target_column_idx=0)

        expected_samples = 100 - 60 - 1 + 1
        assert X.shape == (expected_samples, 60, 5)
        assert y.shape == (expected_samples,)

    def test_create_sequences_target_column(self):
        """Test sequence creation with different target column."""
        generator = SlidingWindowGenerator(sequence_length=10, prediction_horizon=1)
        data = np.arange(50).reshape(-1, 1)

        X, y = generator.create_sequences(data, target_column_idx=0)

        # Verify first target is correct
        assert y[0] == data[10, 0]
        # Verify last target is correct
        assert y[-1] == data[-1, 0]

    def test_create_sequences_prediction_horizon(self):
        """Test sequence creation with different prediction horizons."""
        generator = SlidingWindowGenerator(sequence_length=10, prediction_horizon=5)
        data = np.arange(50).reshape(-1, 1)

        X, y = generator.create_sequences(data, target_column_idx=0)

        expected_samples = 50 - 10 - 5 + 1
        assert len(X) == expected_samples
        # Target should be 5 days ahead
        assert y[0] == data[10 + 5 - 1, 0]

    def test_split_data_default(self, generator):
        """Test data splitting with default ratios."""
        X = np.random.randn(100, 60, 5)
        y = np.random.randn(100)

        X_train, X_val, X_test, y_train, y_val, y_test = generator.split_data(X, y)

        # Check sizes
        assert len(X_train) == 70  # 70%
        assert len(X_val) == 15    # 15%
        assert len(X_test) == 15   # 15%

        # Check shapes match
        assert X_train.shape[1:] == X.shape[1:]
        assert len(y_train) == len(X_train)

    def test_split_data_custom_ratios(self, generator):
        """Test data splitting with custom ratios."""
        X = np.random.randn(100, 60, 5)
        y = np.random.randn(100)

        X_train, X_val, X_test, y_train, y_val, y_test = generator.split_data(
            X, y, train_split=0.6, val_split=0.2
        )

        assert len(X_train) == 60  # 60%
        assert len(X_val) == 20    # 20%
        assert len(X_test) == 20   # 20%

    def test_split_data_maintains_order(self, generator):
        """Test that split maintains temporal order."""
        X = np.arange(100).reshape(100, 1, 1)
        y = np.arange(100)

        X_train, X_val, X_test, y_train, y_val, y_test = generator.split_data(X, y)

        # Train should come before val, val before test
        assert X_train[-1, 0, 0] < X_val[0, 0, 0]
        assert X_val[-1, 0, 0] < X_test[0, 0, 0]

    def test_sequence_length_parameter(self):
        """Test different sequence lengths."""
        short_gen = SlidingWindowGenerator(sequence_length=30, prediction_horizon=1)
        long_gen = SlidingWindowGenerator(sequence_length=90, prediction_horizon=1)

        data = np.random.randn(200, 3)

        X_short, y_short = short_gen.create_sequences(data)
        X_long, y_long = long_gen.create_sequences(data)

        assert X_short.shape[0] > X_long.shape[0]  # More samples with shorter sequences
        assert X_short.shape[1] == 30
        assert X_long.shape[1] == 90

    def test_create_sequences_minimum_data(self):
        """Test sequence creation with minimum required data."""
        generator = SlidingWindowGenerator(sequence_length=10, prediction_horizon=1)
        # Exactly enough data for 1 sample (need sequence_length + prediction_horizon points)
        data = np.arange(11).reshape(-1, 1)

        X, y = generator.create_sequences(data)

        assert len(X) == 1
        assert X.shape == (1, 10, 1)

    def test_create_sequences_insufficient_data(self):
        """Test sequence creation with insufficient data."""
        generator = SlidingWindowGenerator(sequence_length=10, prediction_horizon=1)
        # Not enough data
        data = np.arange(9).reshape(-1, 1)

        X, y = generator.create_sequences(data)

        assert len(X) == 0
        assert len(y) == 0
