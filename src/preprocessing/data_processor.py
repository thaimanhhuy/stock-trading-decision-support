"""Data preprocessing and feature engineering."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import os
from src.preprocessing.technical_indicators import TechnicalIndicators
from src.utils.logger import LoggerMixin
from src.config.settings import get_settings


class DataProcessor(LoggerMixin):
    """Process and engineer features from raw data."""

    def __init__(self):
        """Initialize data processor."""
        self.indicators = TechnicalIndicators()
        self.scaler = StandardScaler()
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
