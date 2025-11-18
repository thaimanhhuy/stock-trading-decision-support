"""Data storage utilities."""

import pandas as pd
import os
from pathlib import Path
from src.utils.logger import LoggerMixin
from src.config.settings import get_settings


class DataStorage(LoggerMixin):
    """Handle data persistence."""

    def __init__(self):
        """Initialize data storage."""
        self.settings = get_settings()
        self.raw_path = self.settings.data_raw_path
        self.processed_path = self.settings.data_processed_path
        self.features_path = self.settings.data_features_path

        # Ensure directories exist
        for path in [self.raw_path, self.processed_path, self.features_path]:
            Path(path).mkdir(parents=True, exist_ok=True)

    def save_raw(self, data: pd.DataFrame, symbol: str) -> str:
        """Save raw data.

        Args:
            data: DataFrame to save
            symbol: Stock symbol

        Returns:
            Path to saved file
        """
        filepath = os.path.join(self.raw_path, f"{symbol}.csv")
        data.to_csv(filepath, index=False)
        self.logger.info(f"Saved raw data to {filepath}")
        return filepath

    def load_raw(self, symbol: str) -> pd.DataFrame:
        """Load raw data.

        Args:
            symbol: Stock symbol

        Returns:
            DataFrame with raw data
        """
        filepath = os.path.join(self.raw_path, f"{symbol}.csv")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Raw data not found: {filepath}")

        data = pd.read_csv(filepath)
        self.logger.info(f"Loaded raw data from {filepath}")
        return data

    def save_processed(self, data: pd.DataFrame, symbol: str) -> str:
        """Save processed data."""
        filepath = os.path.join(self.processed_path, f"{symbol}_processed.csv")
        data.to_csv(filepath, index=False)
        self.logger.info(f"Saved processed data to {filepath}")
        return filepath

    def load_processed(self, symbol: str) -> pd.DataFrame:
        """Load processed data."""
        filepath = os.path.join(self.processed_path, f"{symbol}_processed.csv")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Processed data not found: {filepath}")

        data = pd.read_csv(filepath)
        self.logger.info(f"Loaded processed data from {filepath}")
        return data

    def save_features(self, data: pd.DataFrame, symbol: str) -> str:
        """Save feature data."""
        filepath = os.path.join(self.features_path, f"{symbol}_features.csv")
        data.to_csv(filepath, index=False)
        self.logger.info(f"Saved features to {filepath}")
        return filepath

    def load_features(self, symbol: str) -> pd.DataFrame:
        """Load feature data."""
        filepath = os.path.join(self.features_path, f"{symbol}_features.csv")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Features not found: {filepath}")

        data = pd.read_csv(filepath)
        self.logger.info(f"Loaded features from {filepath}")
        return data
