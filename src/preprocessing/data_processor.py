"""Data preprocessing and feature engineering."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Tuple
import joblib
import os
from src.preprocessing.technical_indicators import TechnicalIndicators
from src.utils.logger import LoggerMixin
from src.config.settings import get_settings


class DataProcessor(LoggerMixin):
    """Process and engineer features from raw data."""

    def __init__(self) -> None:
        """Initialize data processor."""
        self.indicators = TechnicalIndicators()
        # Use MinMaxScaler to normalize to [0,1] range as per thesis requirement
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.settings = get_settings()

    def process(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Process raw data into features.

        Args:
            data: Raw OHLCV data
            symbol: Stock symbol

        Returns:
            Processed data with features
        """
        self.logger.info(f"Processing data for {symbol}")

        # Add technical indicators
        data = self.indicators.add_all_indicators(data)

        # Drop NaN values created by indicators
        data = data.dropna()

        self.logger.info(f"Processed {len(data)} rows for {symbol}")
        return data

    def normalize(self, data: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Normalize features.

        Args:
            data: DataFrame with features
            fit: Whether to fit the scaler

        Returns:
            Normalized DataFrame
        """
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        exclude_cols = ["date"] if "date" in numeric_cols else []
        cols_to_scale = [col for col in numeric_cols if col not in exclude_cols]

        if fit:
            data[cols_to_scale] = self.scaler.fit_transform(data[cols_to_scale])
        else:
            data[cols_to_scale] = self.scaler.transform(data[cols_to_scale])

        return data

    def save_scaler(self, symbol: str) -> str:
        """Save fitted scaler."""
        filepath = os.path.join(self.settings.model_scaler_path, f"{symbol}_scaler.pkl")
        joblib.dump(self.scaler, filepath)
        self.logger.info(f"Saved scaler to {filepath}")
        return filepath

    def load_scaler(self, symbol: str) -> None:
        """Load fitted scaler."""
        filepath = os.path.join(self.settings.model_scaler_path, f"{symbol}_scaler.pkl")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Scaler not found: {filepath}")
        self.scaler = joblib.load(filepath)
        self.logger.info(f"Loaded scaler from {filepath}")

    def create_sequences(
        self, data: np.ndarray, sequence_length: int = 60, target_column_idx: int = 0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sliding window sequences for LSTM/GRU models.

        Args:
            data: Input data array (features)
            sequence_length: Length of each sequence (default 60 days from thesis)
            target_column_idx: Index of target column (typically close price at index 0)

        Returns:
            Tuple of (X_sequences, y_targets)
            - X_sequences: shape (n_samples, sequence_length, n_features)
            - y_targets: shape (n_samples,) - next day close price
        """
        X, y = [], []

        for i in range(len(data) - sequence_length):
            # Get sequence of past 60 days
            sequence = data[i:i + sequence_length]
            # Target is the next day's close price
            target = data[i + sequence_length, target_column_idx]

            X.append(sequence)
            y.append(target)

        X = np.array(X)
        y = np.array(y)

        self.logger.info(
            f"Created {len(X)} sequences with shape X={X.shape}, y={y.shape}"
        )

        return X, y
