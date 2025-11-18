"""Risk management."""

from typing import Dict, Any
from src.utils.logger import LoggerMixin


class RiskManager(LoggerMixin):
    """Manage trading risk and position sizing."""

    def __init__(
        self,
        max_position_size: float = 0.10,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10,
    ):
        """Initialize risk manager.

        Args:
            max_position_size: Maximum position size as fraction of portfolio (10% from thesis)
            stop_loss_pct: Stop loss percentage (5% from thesis)
            take_profit_pct: Take profit percentage (10% suggested)
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def calculate_position_size(
        self, signal_strength: float, portfolio_value: float, current_price: float
    ) -> Dict[str, Any]:
        """Calculate position size.

        Args:
            signal_strength: Signal strength (0-1)
            portfolio_value: Current portfolio value
            current_price: Current stock price

        Returns:
            Position sizing information
        """
        position_value = portfolio_value * self.max_position_size * signal_strength
        shares = int(position_value / current_price)

        stop_loss = current_price * (1 - self.stop_loss_pct)
        take_profit = current_price * (1 + self.take_profit_pct)

        return {
            "position_value": position_value,
            "shares": shares,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_amount": position_value * self.stop_loss_pct,
        }
