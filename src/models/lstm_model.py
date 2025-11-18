"""LSTM model implementation following thesis specifications."""

import numpy as np
import os
from typing import Optional
from src.models.base_model import BaseModel

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class LSTMModel(BaseModel):
    """LSTM model for stock price prediction.

    Architecture from thesis:
    - Input: (batch_size, 60, 4) - 60 days lookback, 4 features
    - LSTM layer: 128 units
    - Dropout: 0.2
    - Dense output: 1 unit (next day close price)

    Training config from thesis:
    - Optimizer: Adam (lr=0.001)
    - Loss: MSE
    - Batch size: 64
    - Max epochs: 50
    - Early stopping: patience=8
    - Random seed: 42
    """

    def __init__(self, symbol: str, sequence_length: int = 60, n_features: int = 4):
        """Initialize LSTM model.

        Args:
            symbol: Stock symbol
            sequence_length: Input sequence length (default 60 from thesis)
            n_features: Number of input features (default 4 from thesis)
        """
        super().__init__(symbol)
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.history = None

        if not TENSORFLOW_AVAILABLE:
            self.logger.warning(
                "TensorFlow not available. LSTM model will not work. "
                "Install with: pip install tensorflow"
            )
        else:
            # Set random seed for reproducibility (from thesis)
            tf.random.set_seed(42)
            np.random.seed(42)
            self._build_model()

    def _build_model(self) -> None:
        """Build LSTM model architecture."""
        if not TENSORFLOW_AVAILABLE:
            return

        self.model = keras.Sequential([
            # Input layer
            layers.Input(shape=(self.sequence_length, self.n_features)),

            # LSTM layer with 128 units (from thesis)
            layers.LSTM(128, return_sequences=False),

            # Dropout layer (0.2 from thesis)
            layers.Dropout(0.2),

            # Dense output layer (1 unit for next day close price)
            layers.Dense(1)
        ])

        # Compile with Adam optimizer (lr=0.001) and MSE loss (from thesis)
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )

        self.logger.info(f"Built LSTM model for {self.symbol}")
        self.logger.info(f"Model architecture: {self.model.summary()}")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        batch_size: int = 64,
        epochs: int = 50,
        patience: int = 8,
        **kwargs
    ) -> None:
        """Train LSTM model.

        Args:
            X_train: Training sequences (n_samples, sequence_length, n_features)
            y_train: Training targets (n_samples,)
            X_val: Validation sequences (optional)
            y_val: Validation targets (optional)
            batch_size: Batch size (default 64 from thesis)
            epochs: Max epochs (default 50 from thesis)
            patience: Early stopping patience (default 8 from thesis)
            **kwargs: Additional arguments
        """
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("TensorFlow not available. Cannot train model.")
            return

        if self.model is None:
            self._build_model()

        # Setup callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            )
        ]

        # Prepare validation data
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)

        self.logger.info(f"Training LSTM model for {self.symbol}")
        self.logger.info(f"Training data shape: X={X_train.shape}, y={y_train.shape}")
        if validation_data:
            self.logger.info(f"Validation data shape: X={X_val.shape}, y={y_val.shape}")

        # Train model
        self.history = self.model.fit(
            X_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )

        self.is_trained = True
        self.logger.info(f"LSTM model training completed for {self.symbol}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions.

        Args:
            X: Input sequences (n_samples, sequence_length, n_features)

        Returns:
            Predictions (n_samples,)
        """
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("TensorFlow not available. Cannot make predictions.")
            return np.array([])

        if self.model is None or not self.is_trained:
            self.logger.error("Model not trained. Call train() first.")
            return np.array([])

        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()

    def save(self, filepath: str) -> None:
        """Save model to disk.

        Args:
            filepath: Path to save model (.h5 or .keras format)
        """
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("TensorFlow not available. Cannot save model.")
            return

        if self.model is None:
            self.logger.error("No model to save.")
            return

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Save model
        self.model.save(filepath)
        self.logger.info(f"Saved LSTM model to {filepath}")

    def load(self, filepath: str) -> None:
        """Load model from disk.

        Args:
            filepath: Path to saved model
        """
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("TensorFlow not available. Cannot load model.")
            return

        if not os.path.exists(filepath):
            self.logger.error(f"Model file not found: {filepath}")
            return

        # Load model
        self.model = keras.models.load_model(filepath)
        self.is_trained = True
        self.logger.info(f"Loaded LSTM model from {filepath}")
