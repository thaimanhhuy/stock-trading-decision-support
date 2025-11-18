"""Trading signal generation."""

import pandas as pd
from typing import Dict, Any
from src.utils.logger import LoggerMixin
from src.utils.constants import SIGNAL_BUY, SIGNAL_SELL, SIGNAL_HOLD


class SignalGenerator(LoggerMixin):
    """Generate trading signals from predictions."""

    def __init__(self, buy_threshold: float = 0.02, sell_threshold: float = -0.01):
        """Initialize signal generator.

        Args:
            buy_threshold: Minimum predicted gain for buy signal
            sell_threshold: Maximum predicted loss for sell signal
        """
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signal(
        self, prediction: float, current_price: float, technical_data: pd.Series = None
    ) -> Dict[str, Any]:
        """Generate trading signal.

        Args:
            prediction: Predicted price
            current_price: Current price
            technical_data: Technical indicators for confirmation

        Returns:
            Signal dictionary
        """
        predicted_return = (prediction - current_price) / current_price

        if predicted_return >= self.buy_threshold:
            signal = SIGNAL_BUY
            strength = min(predicted_return / self.buy_threshold, 1.0)
        elif predicted_return <= self.sell_threshold:
            signal = SIGNAL_SELL
            strength = min(abs(predicted_return / self.sell_threshold), 1.0)
        else:
            signal = SIGNAL_HOLD
            strength = 0.0

        return {
            "signal": signal,
            "strength": strength,
            "predicted_return": predicted_return,
            "current_price": current_price,
            "target_price": prediction,
        }
