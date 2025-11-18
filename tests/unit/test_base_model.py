"""Tests for BaseModel."""

import pytest
import numpy as np
from src.models.base_model import BaseModel


class ConcreteModel(BaseModel):
    """Concrete implementation of BaseModel for testing."""

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.trained_data = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray, **kwargs) -> None:
        """Train the model."""
        self.trained_data = (X_train, y_train)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        # Simple prediction: return mean of training targets
        return np.full(len(X), np.mean(self.trained_data[1]))

    def save(self, filepath: str) -> None:
        """Save model to file."""
        pass

    def load(self, filepath: str) -> None:
        """Load model from file."""
        pass


class TestBaseModel:
    """Tests for BaseModel."""

    @pytest.fixture
    def model(self):
        """Create model instance."""
        return ConcreteModel("TEST")

    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        X_train = np.random.randn(100, 60, 5)
        y_train = np.random.randn(100)
        X_test = np.random.randn(20, 60, 5)
        y_test = np.random.randn(20)
        return X_train, y_train, X_test, y_test

    def test_initialization(self, model):
        """Test model initialization."""
        assert model.symbol == "TEST"
        assert model.is_trained is False

    def test_train(self, model, sample_data):
        """Test model training."""
        X_train, y_train, _, _ = sample_data

        model.train(X_train, y_train)

        assert model.is_trained is True
        assert model.trained_data is not None

    def test_predict_untrained(self, model, sample_data):
        """Test prediction without training."""
        _, _, X_test, _ = sample_data

        with pytest.raises(ValueError, match="Model must be trained"):
            model.predict(X_test)

    def test_predict_trained(self, model, sample_data):
        """Test prediction after training."""
        X_train, y_train, X_test, _ = sample_data

        model.train(X_train, y_train)
        predictions = model.predict(X_test)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(X_test)

    def test_evaluate(self, model, sample_data):
        """Test model evaluation."""
        X_train, y_train, X_test, y_test = sample_data

        model.train(X_train, y_train)
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

    def test_evaluate_metrics_relationship(self, model, sample_data):
        """Test relationship between metrics."""
        X_train, y_train, X_test, y_test = sample_data

        model.train(X_train, y_train)
        metrics = model.evaluate(X_test, y_test)

        # RMSE should be sqrt of MSE
        np.testing.assert_almost_equal(metrics["rmse"], np.sqrt(metrics["mse"]))

    def test_evaluate_perfect_predictions(self, model):
        """Test evaluation with perfect predictions."""
        X_train = np.random.randn(50, 60, 5)
        y_train = np.ones(50) * 100.0

        model.train(X_train, y_train)

        # Test with same values
        X_test = np.random.randn(10, 60, 5)
        y_test = np.ones(10) * 100.0

        metrics = model.evaluate(X_test, y_test)

        # MAE and MSE should be very small
        assert metrics["mae"] < 0.01
        assert metrics["mse"] < 0.01

    def test_abstract_methods(self):
        """Test that BaseModel is abstract."""
        # Cannot instantiate BaseModel directly
        with pytest.raises(TypeError):
            BaseModel("TEST")

    def test_symbol_property(self, model):
        """Test symbol property."""
        assert hasattr(model, "symbol")
        assert model.symbol == "TEST"

    def test_is_trained_flag(self, model, sample_data):
        """Test is_trained flag lifecycle."""
        X_train, y_train, _, _ = sample_data

        assert model.is_trained is False

        model.train(X_train, y_train)
        assert model.is_trained is True
