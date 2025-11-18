"""Data validation utilities."""

import pandas as pd
import numpy as np
from typing import Dict, List
from src.utils.logger import LoggerMixin
from src.utils.exceptions import DataValidationError


class DataValidator(LoggerMixin):
    """Validate stock market data."""

    def validate(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Validate and clean data.

        Args:
            data: DataFrame with OHLCV data
            symbol: Stock symbol

        Returns:
            Validated DataFrame

        Raises:
            DataValidationError: If validation fails
        """
        self.logger.info(f"Validating data for {symbol}")

        # Check for required columns
        required_cols = ["date", "open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise DataValidationError(f"Missing columns: {missing_cols}")

        # Check for missing values
        missing_pct = data[["open", "high", "low", "close"]].isnull().sum() / len(data)
        if missing_pct.max() > 0.05:
            raise DataValidationError(f"Too many missing values: {missing_pct.max():.2%}")

        # Forward fill missing values
        data = data.fillna(method="ffill").fillna(method="bfill")

        # Check for negative prices
        price_cols = ["open", "high", "low", "close"]
        if (data[price_cols] < 0).any().any():
            raise DataValidationError("Negative prices detected")

        # Check high >= low
        if (data["high"] < data["low"]).any():
            raise DataValidationError("High price less than low price")

        # Check for outliers (price changes > 50% in one day)
        returns = data["close"].pct_change().abs()
        if (returns > 0.5).any():
            self.logger.warning(f"Large price movements detected for {symbol}")

        self.logger.info(f"Validation passed for {symbol}")
        return data
