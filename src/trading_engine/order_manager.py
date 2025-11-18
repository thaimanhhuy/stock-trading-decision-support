"""Order management."""

from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import LoggerMixin


class OrderManager(LoggerMixin):
    """Manage trade orders and execution."""

    def __init__(self):
        """Initialize order manager."""
        self.orders: List[Dict[str, Any]] = []

    def create_order(
        self,
        symbol: str,
        signal: str,
        shares: int,
        price: float,
        stop_loss: float,
        take_profit: float,
    ) -> Dict[str, Any]:
        """Create a new order.

        Args:
            symbol: Stock symbol
            signal: buy/sell signal
            shares: Number of shares
            price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Order dictionary
        """
        order = {
            "order_id": len(self.orders) + 1,
            "symbol": symbol,
            "signal": signal,
            "shares": shares,
            "entry_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "timestamp": datetime.now(),
            "status": "pending",
        }

        self.orders.append(order)
        self.logger.info(f"Created order {order['order_id']} for {symbol}")

        return order

    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get orders by status."""
        if status:
            return [o for o in self.orders if o["status"] == status]
        return self.orders
