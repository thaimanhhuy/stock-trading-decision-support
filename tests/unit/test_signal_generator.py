"""Tests for SignalGenerator."""

import pytest
import pandas as pd
from src.trading_engine.signal_generator import SignalGenerator
from src.utils.constants import SIGNAL_BUY, SIGNAL_SELL, SIGNAL_HOLD


class TestSignalGenerator:
    """Tests for SignalGenerator."""

    @pytest.fixture
    def generator(self):
        """Create signal generator with default thresholds."""
        return SignalGenerator(buy_threshold=0.03, sell_threshold=-0.03)

    def test_initialization(self, generator):
        """Test signal generator initialization."""
        assert generator.buy_threshold == 0.03
        assert generator.sell_threshold == -0.03

    def test_generate_buy_signal(self, generator):
        """Test generating buy signal."""
        current_price = 100.0
        prediction = 105.0  # 5% increase

        signal = generator.generate_signal(prediction, current_price)

        assert signal["signal"] == SIGNAL_BUY
        assert signal["strength"] > 0
        assert signal["predicted_return"] > generator.buy_threshold
        assert signal["current_price"] == current_price
        assert signal["target_price"] == prediction

    def test_generate_sell_signal(self, generator):
        """Test generating sell signal."""
        current_price = 100.0
        prediction = 95.0  # 5% decrease

        signal = generator.generate_signal(prediction, current_price)

        assert signal["signal"] == SIGNAL_SELL
        assert signal["strength"] > 0
        assert signal["predicted_return"] < generator.sell_threshold

    def test_generate_hold_signal(self, generator):
        """Test generating hold signal."""
        current_price = 100.0
        prediction = 101.0  # 1% increase (below threshold)

        signal = generator.generate_signal(prediction, current_price)

        assert signal["signal"] == SIGNAL_HOLD
        assert signal["strength"] == 0.0

    def test_signal_strength_scaling(self, generator):
        """Test signal strength scaling."""
        current_price = 100.0

        # Exactly at threshold
        signal1 = generator.generate_signal(103.0, current_price)
        assert abs(signal1["strength"] - 1.0) < 0.01

        # Double the threshold
        signal2 = generator.generate_signal(106.0, current_price)
        assert signal2["strength"] >= signal1["strength"]

    def test_signal_strength_capped(self, generator):
        """Test that signal strength is capped at 1.0."""
        current_price = 100.0
        prediction = 200.0  # 100% increase

        signal = generator.generate_signal(prediction, current_price)

        assert signal["strength"] <= 1.0

    def test_predicted_return_calculation(self, generator):
        """Test predicted return calculation."""
        current_price = 100.0
        prediction = 110.0

        signal = generator.generate_signal(prediction, current_price)

        expected_return = (110.0 - 100.0) / 100.0
        assert abs(signal["predicted_return"] - expected_return) < 0.0001

    def test_custom_thresholds(self):
        """Test signal generator with custom thresholds."""
        generator = SignalGenerator(buy_threshold=0.05, sell_threshold=-0.05)

        current_price = 100.0
        prediction = 104.0  # 4% increase

        signal = generator.generate_signal(prediction, current_price)

        # Should be HOLD with 5% threshold
        assert signal["signal"] == SIGNAL_HOLD

    def test_zero_return(self, generator):
        """Test signal with zero predicted return."""
        current_price = 100.0
        prediction = 100.0

        signal = generator.generate_signal(prediction, current_price)

        assert signal["signal"] == SIGNAL_HOLD
        assert signal["predicted_return"] == 0.0
        assert signal["strength"] == 0.0

    def test_negative_price_prediction(self, generator):
        """Test with valid negative return."""
        current_price = 100.0
        prediction = 90.0  # -10% return

        signal = generator.generate_signal(prediction, current_price)

        assert signal["signal"] == SIGNAL_SELL
        assert signal["predicted_return"] < 0

    def test_signal_with_technical_data(self, generator):
        """Test signal generation with technical data."""
        current_price = 100.0
        prediction = 105.0
        technical_data = pd.Series({
            "rsi": 65,
            "macd": 1.5,
            "volume": 1000000
        })

        signal = generator.generate_signal(prediction, current_price, technical_data)

        # Should still generate signal even with technical data
        assert signal["signal"] == SIGNAL_BUY

    def test_sell_signal_strength(self, generator):
        """Test sell signal strength calculation."""
        current_price = 100.0

        # Exactly at sell threshold
        signal1 = generator.generate_signal(97.0, current_price)  # -3%
        assert abs(signal1["strength"] - 1.0) < 0.01

        # Double the sell threshold
        signal2 = generator.generate_signal(94.0, current_price)  # -6%
        assert signal2["strength"] >= signal1["strength"]

    def test_boundary_cases(self, generator):
        """Test boundary cases near thresholds."""
        current_price = 100.0

        # Just above buy threshold
        signal1 = generator.generate_signal(103.01, current_price)
        assert signal1["signal"] == SIGNAL_BUY

        # Just below buy threshold
        signal2 = generator.generate_signal(102.99, current_price)
        assert signal2["signal"] == SIGNAL_HOLD

        # Just below sell threshold
        signal3 = generator.generate_signal(96.99, current_price)
        assert signal3["signal"] == SIGNAL_SELL

        # Just above sell threshold
        signal4 = generator.generate_signal(97.01, current_price)
        assert signal4["signal"] == SIGNAL_HOLD
