"""Model evaluation and ensemble prediction."""

import numpy as np
from typing import Dict, Any
from src.utils.logger import LoggerMixin


class ModelEvaluator(LoggerMixin):
    """Evaluate models and generate ensemble predictions."""

    def __init__(self, symbol: str):
        """Initialize evaluator."""
        self.symbol = symbol

    def predict_ensemble(
        self, models: Dict[str, Any], X: np.ndarray, weights: Dict[str, float] = None
    ) -> np.ndarray:
        """Generate ensemble prediction.

        Args:
            models: Dictionary of trained models
            X: Input data
            weights: Model weights for ensemble

        Returns:
            Ensemble predictions
        """
        if weights is None:
            weights = {name: 1.0 / len(models) for name in models.keys()}

        predictions = {}
        for name, model in models.items():
            try:
                pred = model.predict(X)
                predictions[name] = pred
            except Exception as e:
                self.logger.warning(f"Prediction failed for {name}: {e}")

        if not predictions:
            raise ValueError("No valid predictions")

        # Weighted average
        ensemble = np.zeros(len(X))
        total_weight = 0

        for name, pred in predictions.items():
            weight = weights.get(name, 1.0)
            ensemble += pred * weight
            total_weight += weight

        ensemble /= total_weight

        return ensemble
