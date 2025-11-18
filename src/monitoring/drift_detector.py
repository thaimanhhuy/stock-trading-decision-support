"""Model drift detection."""

import numpy as np
from scipy import stats
from src.utils.logger import LoggerMixin


class DriftDetector(LoggerMixin):
    """Detect data and model drift."""

    def __init__(self, threshold: float = 0.05):
        """Initialize drift detector.

        Args:
            threshold: P-value threshold for drift detection
        """
        self.threshold = threshold

    def detect_drift(
        self, reference_data: np.ndarray, current_data: np.ndarray
    ) -> bool:
        """Detect drift using KS test.

        Args:
            reference_data: Reference distribution
            current_data: Current distribution

        Returns:
            True if drift detected
        """
        if len(reference_data) == 0 or len(current_data) == 0:
            self.logger.warning("Empty data provided for drift detection")
            return False

        # Kolmogorov-Smirnov test
        statistic, p_value = stats.ks_2samp(reference_data, current_data)

        drift_detected = p_value < self.threshold

        if drift_detected:
            self.logger.warning(f"Drift detected: p-value={p_value:.4f}")
        else:
            self.logger.info(f"No drift detected: p-value={p_value:.4f}")

        return drift_detected
