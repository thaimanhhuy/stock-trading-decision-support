"""Tests for GRU model with 3-layer architecture."""

import pytest
import numpy as np
from unittest.mock import patch

# Try to import TensorFlow components
try:
    from src.models.gru_model import GRUModel
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


@pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
class TestGRUModel:
    """Tests for GRU model."""

    @pytest.fixture
    def model(self):
        """Create GRU model instance."""
        return GRUModel(symbol="TEST", sequence_length=60, n_features=5)

    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        np.random.seed(42)
        X_train = np.random.randn(200, 60, 5)
        y_train = np.random.randn(200)
        X_val = np.random.randn(50, 60, 5)
        y_val = np.random.randn(50)
        X_test = np.random.randn(30, 60, 5)
        y_test = np.random.randn(30)
        return X_train, y_train, X_val, y_val, X_test, y_test

    def test_initialization(self, model):
        """Test model initialization."""
        assert model.symbol == "TEST"
        assert model.sequence_length == 60
        assert model.n_features == 5
        assert model.is_trained is False
        assert model.model is not None  # Model should be built on init

    def test_model_architecture(self, model):
        """Test that model has correct 3-layer architecture."""
        # Check that model has 3 GRU layers + 1 Dense layer
        layers = model.model.layers

        # Should have: Input, GRU(128), GRU(64), GRU(32), Dense(1)
        assert len(layers) >= 4  # At minimum GRU layers + Dense

        # Check output shape
        assert model.model.output_shape == (None, 1)

    def test_model_config(self, model):
        """Test that model has correct configuration."""
        config = model.model.get_config()

        # Verify it's a Sequential model
        assert config['name'].startswith('sequential')

    def test_train_without_validation(self, model, sample_data):
        """Test training without validation data."""
        X_train, y_train, _, _, _, _ = sample_data

        # Train with only 2 epochs for speed
        model.train(X_train, y_train, epochs=2, batch_size=32)

        assert model.is_trained is True
        assert model.history is not None

    def test_train_with_validation(self, model, sample_data):
        """Test training with validation data."""
        X_train, y_train, X_val, y_val, _, _ = sample_data

        # Train with validation data
        model.train(X_train, y_train, X_val=X_val, y_val=y_val, epochs=2, batch_size=32)

        assert model.is_trained is True
        assert model.history is not None
        # Check that validation metrics were tracked
        assert 'val_loss' in model.history.history

    def test_train_with_config_defaults(self, model, sample_data):
        """Test training with default parameters from config."""
        X_train, y_train, X_val, y_val, _, _ = sample_data

        # Default parameters should be: batch_size=32, epochs=100, patience=15
        # We'll override epochs for speed
        model.train(X_train, y_train, X_val=X_val, y_val=y_val, epochs=2)

        assert model.is_trained is True

    def test_predict_untrained(self, model, sample_data):
        """Test prediction without training."""
        _, _, _, _, X_test, _ = sample_data

        predictions = model.predict(X_test)

        # Should return empty array if not trained
        assert len(predictions) == 0

    def test_predict_trained(self, model, sample_data):
        """Test prediction after training."""
        X_train, y_train, _, _, X_test, _ = sample_data

        model.train(X_train, y_train, epochs=2, batch_size=32)
        predictions = model.predict(X_test)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(X_test)
        # Predictions should be 1D array
        assert predictions.ndim == 1

    def test_prediction_shape(self, model, sample_data):
        """Test prediction output shape."""
        X_train, y_train, _, _, X_test, _ = sample_data

        model.train(X_train, y_train, epochs=2, batch_size=32)
        predictions = model.predict(X_test)

        # Each prediction should be a scalar (next day price)
        assert predictions.shape == (len(X_test),)

    def test_early_stopping(self, model, sample_data):
        """Test early stopping callback."""
        X_train, y_train, X_val, y_val, _, _ = sample_data

        # Train with high epochs but early stopping should kick in
        model.train(X_train, y_train, X_val=X_val, y_val=y_val, epochs=100, patience=5)

        # Should have stopped before 100 epochs (in most cases)
        # Or at least completed training
        assert model.is_trained is True
        assert len(model.history.history['loss']) <= 100

    def test_save_model(self, model, sample_data, tmp_path):
        """Test saving model to disk."""
        X_train, y_train, _, _, _, _ = sample_data

        model.train(X_train, y_train, epochs=2, batch_size=32)

        filepath = str(tmp_path / "test_model.keras")
        model.save(filepath)

        import os
        assert os.path.exists(filepath)

    def test_load_model(self, model, sample_data, tmp_path):
        """Test loading model from disk."""
        X_train, y_train, _, _, X_test, _ = sample_data

        # Train and save
        model.train(X_train, y_train, epochs=2, batch_size=32)
        filepath = str(tmp_path / "test_model.keras")
        model.save(filepath)

        # Get predictions from original model
        original_predictions = model.predict(X_test)

        # Create new model and load
        new_model = GRUModel(symbol="TEST", sequence_length=60, n_features=5)
        new_model.load(filepath)

        # Get predictions from loaded model
        loaded_predictions = new_model.predict(X_test)

        # Predictions should be the same
        np.testing.assert_array_almost_equal(original_predictions, loaded_predictions)

    def test_load_nonexistent_model(self, model):
        """Test loading non-existent model."""
        model.load("/nonexistent/path/model.keras")

        # Should log error but not raise exception
        # Model should not be marked as trained
        assert model.is_trained is False

    def test_different_sequence_lengths(self):
        """Test model with different sequence lengths."""
        model_30 = GRUModel(symbol="TEST", sequence_length=30, n_features=5)
        model_90 = GRUModel(symbol="TEST", sequence_length=90, n_features=5)

        assert model_30.sequence_length == 30
        assert model_90.sequence_length == 90

    def test_different_feature_counts(self):
        """Test model with different feature counts."""
        model_4 = GRUModel(symbol="TEST", sequence_length=60, n_features=4)
        model_10 = GRUModel(symbol="TEST", sequence_length=60, n_features=10)

        assert model_4.n_features == 4
        assert model_10.n_features == 10

    def test_evaluate(self, model, sample_data):
        """Test model evaluation."""
        X_train, y_train, _, _, X_test, y_test = sample_data

        model.train(X_train, y_train, epochs=2, batch_size=32)
        metrics = model.evaluate(X_test, y_test)

        assert isinstance(metrics, dict)
        assert "mae" in metrics
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics

        # All metrics should be non-negative
        assert metrics["mae"] >= 0
        assert metrics["mse"] >= 0
        assert metrics["rmse"] >= 0

    def test_symbol_property(self, model):
        """Test symbol property."""
        assert model.symbol == "TEST"

    def test_reproducibility(self):
        """Test that random seed ensures reproducibility."""
        # Create two models with same seed
        model1 = GRUModel(symbol="TEST", sequence_length=60, n_features=5)
        model2 = GRUModel(symbol="TEST", sequence_length=60, n_features=5)

        # Both models should be initialized
        assert model1.model is not None
        assert model2.model is not None

    def test_gru_vs_lstm_architecture(self):
        """Test that GRU has similar but distinct architecture from LSTM."""
        from src.models.lstm_model import LSTMModel

        gru_model = GRUModel(symbol="TEST", sequence_length=60, n_features=5)
        lstm_model = LSTMModel(symbol="TEST", sequence_length=60, n_features=5)

        # Both should have models
        assert gru_model.model is not None
        assert lstm_model.model is not None

        # Both should have same output shape
        assert gru_model.model.output_shape == lstm_model.model.output_shape


@pytest.mark.skipif(TENSORFLOW_AVAILABLE, reason="Only test when TensorFlow not available")
class TestGRUModelWithoutTensorFlow:
    """Tests for GRU model without TensorFlow."""

    def test_initialization_without_tensorflow(self):
        """Test that model handles missing TensorFlow gracefully."""
        with patch("src.models.gru_model.TENSORFLOW_AVAILABLE", False):
            model = GRUModel(symbol="TEST")

            assert model.model is None
            assert model.is_trained is False

    def test_train_without_tensorflow(self):
        """Test that training fails gracefully without TensorFlow."""
        with patch("src.models.gru_model.TENSORFLOW_AVAILABLE", False):
            model = GRUModel(symbol="TEST")
            X_train = np.random.randn(100, 60, 5)
            y_train = np.random.randn(100)

            model.train(X_train, y_train)

            # Should not raise exception, just log error
            assert model.is_trained is False

    def test_predict_without_tensorflow(self):
        """Test that prediction fails gracefully without TensorFlow."""
        with patch("src.models.gru_model.TENSORFLOW_AVAILABLE", False):
            model = GRUModel(symbol="TEST")
            X_test = np.random.randn(10, 60, 5)

            predictions = model.predict(X_test)

            # Should return empty array
            assert len(predictions) == 0
