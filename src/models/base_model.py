"""Base model class."""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any
from src.utils.logger import LoggerMixin


class BaseModel(ABC, LoggerMixin):
    """Abstract base class for all models."""

    def __init__(self, symbol: str):
        """Initialize model.

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol
        self.is_trained = False

    @abstractmethod
    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> None:
        """Train the model."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Save model to file."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load model from file."""
        pass

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance.

        Args:
            X_test: Test features
            y_test: Test targets

        Returns:
            Dictionary of metrics
        """
        predictions = self.predict(X_test)

        mae = np.mean(np.abs(y_test - predictions))
        mse = np.mean((y_test - predictions) ** 2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100

        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "mape": float(mape),
        }
