"""Model training orchestrator."""

from typing import Dict, Any
from src.models.arima_model import ARIMAModel
from src.models.lstm_model import LSTMModel
from src.models.gru_model import GRUModel
from src.utils.logger import LoggerMixin


class ModelTrainer(LoggerMixin):
    """Orchestrate model training."""

    def __init__(self, symbol: str):
        """Initialize trainer.

        Args:
            symbol: Stock symbol
        """
        self.symbol = symbol

    def train_arima(self, X_train, y_train, order=(1, 1, 1)) -> ARIMAModel:
        """Train ARIMA model."""
        model = ARIMAModel(self.symbol, order=order)
        model.train(X_train, y_train)
        return model

    def train_lstm(self, X_train, y_train, **kwargs) -> LSTMModel:
        """Train LSTM model."""
        model = LSTMModel(self.symbol)
        model.train(X_train, y_train, **kwargs)
        return model

    def train_gru(self, X_train, y_train, **kwargs) -> GRUModel:
        """Train GRU model."""
        model = GRUModel(self.symbol)
        model.train(X_train, y_train, **kwargs)
        return model

    def train_all(self, X_train, y_train) -> Dict[str, Any]:
        """Train all models."""
        self.logger.info(f"Training all models for {self.symbol}")

        models = {
            "arima": self.train_arima(X_train, y_train),
            "lstm": self.train_lstm(X_train, y_train),
            "gru": self.train_gru(X_train, y_train),
        }

        self.logger.info("All models trained")
        return models
