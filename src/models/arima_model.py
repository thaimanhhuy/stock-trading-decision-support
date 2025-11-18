"""ARIMA model implementation."""

import numpy as np
import joblib
from statsmodels.tsa.arima.model import ARIMA
from src.models.base_model import BaseModel


class ARIMAModel(BaseModel):
    """ARIMA model for time series prediction."""

    def __init__(self, symbol: str, order: tuple = (1, 1, 1)):
        """Initialize ARIMA model.

        Args:
            symbol: Stock symbol
            order: ARIMA order (p, d, q)
        """
        super().__init__(symbol)
        self.order = order
        self.model = None
        self.fitted_model = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> None:
        """Train ARIMA model."""
        self.logger.info(f"Training ARIMA{self.order} for {self.symbol}")

        # ARIMA expects 1D time series
        if len(y_train.shape) > 1:
            y_train = y_train.flatten()

        self.model = ARIMA(y_train, order=self.order)
        self.fitted_model = self.model.fit()
        self.is_trained = True

        self.logger.info(f"ARIMA training complete for {self.symbol}")

    def predict(self, X: np.ndarray, steps: int = 1) -> np.ndarray:
        """Generate predictions."""
        if not self.is_trained:
            raise ValueError("Model not trained")

        forecast = self.fitted_model.forecast(steps=steps)
        return np.array(forecast)

    def save(self, filepath: str) -> None:
        """Save model."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        joblib.dump({"model": self.fitted_model, "order": self.order}, filepath)
        self.logger.info(f"Saved ARIMA model to {filepath}")

    def load(self, filepath: str) -> None:
        """Load model."""
        data = joblib.load(filepath)
        self.fitted_model = data["model"]
        self.order = data["order"]
        self.is_trained = True
        self.logger.info(f"Loaded ARIMA model from {filepath}")
