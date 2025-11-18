"""Sliding window generator for sequence models."""

import numpy as np
from typing import Tuple
from src.utils.logger import LoggerMixin


class SlidingWindowGenerator(LoggerMixin):
    """Generate sliding window sequences for LSTM/GRU."""

    def __init__(self, sequence_length: int = 60, prediction_horizon: int = 1):
        """Initialize generator.

        Args:
            sequence_length: Length of input sequences
            prediction_horizon: Days ahead to predict
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon

    def create_sequences(
        self, data: np.ndarray, target_column_idx: int = 0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create input/output sequences.

        Args:
            data: Input data array
            target_column_idx: Index of target column to predict

        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []

        for i in range(len(data) - self.sequence_length - self.prediction_horizon + 1):
            X.append(data[i : i + self.sequence_length])
            y.append(data[i + self.sequence_length + self.prediction_horizon - 1, target_column_idx])

        return np.array(X), np.array(y)

    def split_data(
        self, X: np.ndarray, y: np.ndarray, train_split: float = 0.7, val_split: float = 0.15
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train/val/test sets.

        Args:
            X: Input sequences
            y: Target values
            train_split: Proportion for training
            val_split: Proportion for validation

        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        n = len(X)
        train_end = int(n * train_split)
        val_end = int(n * (train_split + val_split))

        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]

        self.logger.info(f"Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

        return X_train, X_val, X_test, y_train, y_val, y_test
