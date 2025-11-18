"""LSTM model - placeholder implementation."""

import numpy as np
from src.models.base_model import BaseModel

# Note: Full implementation requires TensorFlow/Keras
# This is a placeholder to maintain project structure


class LSTMModel(BaseModel):
    """LSTM model placeholder."""

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.logger.warning("LSTM model is a placeholder. Install TensorFlow for full implementation.")

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> None:
        """Train model - placeholder."""
        self.logger.info(f"LSTM training placeholder for {self.symbol}")
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict - placeholder returns random predictions."""
        self.logger.warning("Using placeholder LSTM predictions")
        return np.random.randn(len(X))

    def save(self, filepath: str) -> None:
        """Save model - placeholder."""
        self.logger.info(f"LSTM save placeholder: {filepath}")

    def load(self, filepath: str) -> None:
        """Load model - placeholder."""
        self.logger.info(f"LSTM load placeholder: {filepath}")
        self.is_trained = True
