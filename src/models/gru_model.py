"""GRU model implementation following thesis specifications."""

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


class GRUModel(BaseModel):
    """GRU model for stock price prediction.

    Architecture (matches model_config.yaml):
    - Input: (batch_size, 60, n_features) - 60 days lookback
    - GRU layer 1: 128 units, return_sequences=True, dropout=0.2
    - GRU layer 2: 64 units, return_sequences=True, dropout=0.2
    - GRU layer 3: 32 units, return_sequences=False, dropout=0.2
    - Dense output: 1 unit (next day close price)

    Training config:
    - Optimizer: Adam (lr=0.001)
    - Loss: MSE
    - Batch size: 32 (from config)
    - Max epochs: 100 (from config)
    - Early stopping: patience=15 (from config)
    - Random seed: 42
    """

    def __init__(self, symbol: str, sequence_length: int = 60, n_features: int = 4):
        """Initialize GRU model.

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
                "TensorFlow not available. GRU model will not work. "
                "Install with: pip install tensorflow"
            )
        else:
            # Set random seed for reproducibility (from thesis)
            tf.random.set_seed(42)
            np.random.seed(42)
            self._build_model()

    def _build_model(self) -> None:
        """Build GRU model architecture.

        Architecture: 3-layer GRU (128→64→32) matching model_config.yaml
        """
        if not TENSORFLOW_AVAILABLE:
            return

        self.model = keras.Sequential([
            # Input layer
            layers.Input(shape=(self.sequence_length, self.n_features)),

            # First GRU layer: 128 units (matches config)
            layers.GRU(128, return_sequences=True, dropout=0.2),

            # Second GRU layer: 64 units (matches config)
            layers.GRU(64, return_sequences=True, dropout=0.2),

            # Third GRU layer: 32 units (matches config)
            layers.GRU(32, return_sequences=False, dropout=0.2),

            # Dense output layer (1 unit for next day close price)
            layers.Dense(1)
        ])

        # Compile with Adam optimizer (lr=0.001) and MSE loss (from config)
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )

        self.logger.info(f"Built GRU model for {self.symbol}")
        self.logger.info(f"Model architecture: {self.model.summary()}")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        batch_size: int = 32,
        epochs: int = 100,
        patience: int = 15,
        **kwargs
    ) -> None:
        """Train GRU model.

        Args:
            X_train: Training sequences (n_samples, sequence_length, n_features)
            y_train: Training targets (n_samples,)
            X_val: Validation sequences (optional)
            y_val: Validation targets (optional)
            batch_size: Batch size (default 32 from config)
            epochs: Max epochs (default 100 from config)
            patience: Early stopping patience (default 15 from config)
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

        self.logger.info(f"Training GRU model for {self.symbol}")
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
        self.logger.info(f"GRU model training completed for {self.symbol}")

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
        self.logger.info(f"Saved GRU model to {filepath}")

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
        self.logger.info(f"Loaded GRU model from {filepath}")
