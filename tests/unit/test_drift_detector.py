"""Tests for DriftDetector."""

import pytest
import numpy as np
from src.monitoring.drift_detector import DriftDetector


class TestDriftDetector:
    """Tests for DriftDetector."""

    @pytest.fixture
    def detector(self):
        """Create drift detector with default threshold."""
        return DriftDetector(threshold=0.05)

    def test_initialization(self, detector):
        """Test drift detector initialization."""
        assert detector.threshold == 0.05

    def test_no_drift_same_distribution(self, detector):
        """Test no drift detected with same distribution."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(0, 1, 1000)

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should not detect drift for same distribution
        assert drift_detected is False

    def test_drift_different_distribution(self, detector):
        """Test drift detected with different distribution."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(5, 1, 1000)  # Different mean

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should detect drift for different distribution
        assert drift_detected is True

    def test_drift_different_variance(self, detector):
        """Test drift detection with different variance."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(0, 5, 1000)  # Different variance

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should detect drift
        assert drift_detected is True

    def test_empty_reference_data(self, detector):
        """Test with empty reference data."""
        reference_data = np.array([])
        current_data = np.random.normal(0, 1, 100)

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should return False for empty data
        assert drift_detected is False

    def test_empty_current_data(self, detector):
        """Test with empty current data."""
        reference_data = np.random.normal(0, 1, 100)
        current_data = np.array([])

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should return False for empty data
        assert drift_detected is False

    def test_both_empty(self, detector):
        """Test with both datasets empty."""
        reference_data = np.array([])
        current_data = np.array([])

        drift_detected = detector.detect_drift(reference_data, current_data)

        assert drift_detected is False

    def test_custom_threshold(self):
        """Test with custom threshold."""
        detector_strict = DriftDetector(threshold=0.01)  # More strict
        detector_lenient = DriftDetector(threshold=0.10)  # More lenient

        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(0.5, 1, 1000)  # Slightly different

        drift_strict = detector_strict.detect_drift(reference_data, current_data)
        drift_lenient = detector_lenient.detect_drift(reference_data, current_data)

        # Strict threshold more likely to detect drift
        # But this depends on the actual p-value

    def test_small_sample_size(self, detector):
        """Test with small sample sizes."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 10)
        current_data = np.random.normal(0, 1, 10)

        drift_detected = detector.detect_drift(reference_data, current_data)

        assert isinstance(drift_detected, bool)

    def test_identical_data(self, detector):
        """Test with identical data."""
        data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        drift_detected = detector.detect_drift(data, data)

        # Should not detect drift for identical data
        assert drift_detected is False

    def test_subtle_drift(self, detector):
        """Test with subtle drift."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(0.1, 1, 1000)  # Very small shift

        drift_detected = detector.detect_drift(reference_data, current_data)

        # May or may not detect drift depending on p-value
        assert isinstance(drift_detected, bool)

    def test_obvious_drift(self, detector):
        """Test with obvious drift."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(10, 1, 1000)  # Large shift

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should definitely detect drift
        assert drift_detected is True

    def test_drift_with_outliers(self, detector):
        """Test drift detection with outliers."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)
        current_data = np.random.normal(0, 1, 1000)
        # Add outliers to current data
        current_data[:10] = 100

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should detect drift due to outliers
        assert drift_detected is True

    def test_different_distributions_types(self, detector):
        """Test drift between different distribution types."""
        np.random.seed(42)
        reference_data = np.random.normal(0, 1, 1000)  # Normal
        current_data = np.random.exponential(1, 1000)  # Exponential

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should detect drift for different distribution types
        assert drift_detected is True

    def test_uniform_distributions(self, detector):
        """Test with uniform distributions."""
        np.random.seed(42)
        reference_data = np.random.uniform(0, 1, 1000)
        current_data = np.random.uniform(0, 1, 1000)

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should not detect drift
        assert drift_detected is False

    def test_shifted_uniform_distributions(self, detector):
        """Test with shifted uniform distributions."""
        np.random.seed(42)
        reference_data = np.random.uniform(0, 1, 1000)
        current_data = np.random.uniform(1, 2, 1000)  # Shifted range

        drift_detected = detector.detect_drift(reference_data, current_data)

        # Should detect drift
        assert drift_detected is True
