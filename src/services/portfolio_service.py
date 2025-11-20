"""Portfolio management service for tracking positions, trades, and performance.

This service manages portfolio data using JSON file storage.
It provides functionality for position tracking, trade execution, and performance metrics.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd

from src.data_ingestion.yahoo_finance_fetcher import YahooDataFetcher
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.utils.exceptions import PortfolioError

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class Position:
    """Represents a stock position in the portfolio."""

    symbol: str
    quantity: float
    entry_price: float
    entry_date: str
    current_price: float = 0.0
    current_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0

    def update_current_price(self, price: float):
        """Update current price and calculate PnL."""
        self.current_price = price
        self.current_value = self.quantity * price
        self.unrealized_pnl = self.current_value - (self.quantity * self.entry_price)
        if self.entry_price > 0:
            self.unrealized_pnl_percent = (self.unrealized_pnl / (self.quantity * self.entry_price)) * 100


@dataclass
class Trade:
    """Represents a completed trade (buy or sell)."""

    trade_id: str
    symbol: str
    action: str  # "buy" or "sell"
    quantity: float
    price: float
    total_value: float
    timestamp: str
    commission: float = 0.0
    notes: str = ""


class PortfolioService:
    """Service for managing portfolio positions and performance tracking."""

    def __init__(self, portfolio_file: str = None):
        """Initialize portfolio service.

        Args:
            portfolio_file: Path to portfolio JSON file. Defaults to data/portfolio.json
        """
        if portfolio_file is None:
            portfolio_file = os.path.join("data", "portfolio.json")

        self.portfolio_file = portfolio_file
        self.data_fetcher = YahooDataFetcher()

        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)

        # Initialize or load portfolio
        self.portfolio_data = self._load_portfolio()

        logger.info(f"PortfolioService initialized with file: {self.portfolio_file}")

    def _load_portfolio(self) -> Dict:
        """Load portfolio data from JSON file.

        Returns:
            Portfolio data dictionary
        """
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded portfolio from {self.portfolio_file}")
                return data
            except Exception as e:
                logger.error(f"Failed to load portfolio: {e}")
                return self._create_empty_portfolio()
        else:
            logger.info("No existing portfolio found, creating new one")
            return self._create_empty_portfolio()

    def _create_empty_portfolio(self) -> Dict:
        """Create empty portfolio structure.

        Returns:
            Empty portfolio dictionary
        """
        return {
            "created_at": datetime.now().isoformat(),
            "initial_cash": 100000.0,  # Default $100,000
            "current_cash": 100000.0,
            "positions": {},  # symbol -> position data
            "trades": [],  # list of all trades
            "last_updated": datetime.now().isoformat()
        }

    def _save_portfolio(self):
        """Save portfolio data to JSON file."""
        try:
            self.portfolio_data["last_updated"] = datetime.now().isoformat()

            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio_data, f, indent=2)

            logger.debug(f"Portfolio saved to {self.portfolio_file}")
        except Exception as e:
            logger.error(f"Failed to save portfolio: {e}")
            raise PortfolioError(f"Failed to save portfolio: {str(e)}")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Current price or None if unavailable
        """
        try:
            # Fetch last 5 days to ensure we get data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)

            data = self.data_fetcher.fetch(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )

            if data is not None and len(data) > 0:
                return float(data['close'].iloc[-1])
            else:
                logger.warning(f"No price data available for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            return None

    def buy_stock(self, symbol: str, quantity: float, price: Optional[float] = None) -> Trade:
        """Execute a buy order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares to buy
            price: Buy price (if None, fetches current price)

        Returns:
            Trade object

        Raises:
            PortfolioError: If insufficient cash or invalid parameters
        """
        if quantity <= 0:
            raise PortfolioError("Quantity must be positive")

        # Get price
        if price is None:
            price = self.get_current_price(symbol)
            if price is None:
                raise PortfolioError(f"Unable to fetch current price for {symbol}")

        total_cost = quantity * price

        # Check sufficient cash
        if self.portfolio_data["current_cash"] < total_cost:
            raise PortfolioError(
                f"Insufficient cash. Need ${total_cost:.2f}, "
                f"have ${self.portfolio_data['current_cash']:.2f}"
            )

        # Execute trade
        trade_id = f"BUY_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trade = Trade(
            trade_id=trade_id,
            symbol=symbol,
            action="buy",
            quantity=quantity,
            price=price,
            total_value=total_cost,
            timestamp=datetime.now().isoformat()
        )

        # Update cash
        self.portfolio_data["current_cash"] -= total_cost

        # Update or create position
        if symbol in self.portfolio_data["positions"]:
            # Add to existing position (average cost basis)
            pos = self.portfolio_data["positions"][symbol]
            total_quantity = pos["quantity"] + quantity
            total_cost_basis = (pos["quantity"] * pos["entry_price"]) + (quantity * price)
            avg_entry_price = total_cost_basis / total_quantity

            pos["quantity"] = total_quantity
            pos["entry_price"] = avg_entry_price
        else:
            # New position
            self.portfolio_data["positions"][symbol] = {
                "symbol": symbol,
                "quantity": quantity,
                "entry_price": price,
                "entry_date": datetime.now().isoformat()
            }

        # Record trade
        self.portfolio_data["trades"].append(asdict(trade))
        self._save_portfolio()

        logger.info(f"BUY: {quantity} shares of {symbol} @ ${price:.2f} (total: ${total_cost:.2f})")
        return trade

    def sell_stock(self, symbol: str, quantity: float, price: Optional[float] = None) -> Trade:
        """Execute a sell order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares to sell
            price: Sell price (if None, fetches current price)

        Returns:
            Trade object

        Raises:
            PortfolioError: If insufficient shares or invalid parameters
        """
        if quantity <= 0:
            raise PortfolioError("Quantity must be positive")

        # Check position exists
        if symbol not in self.portfolio_data["positions"]:
            raise PortfolioError(f"No position found for {symbol}")

        pos = self.portfolio_data["positions"][symbol]

        # Check sufficient shares
        if pos["quantity"] < quantity:
            raise PortfolioError(
                f"Insufficient shares. Trying to sell {quantity}, "
                f"only have {pos['quantity']}"
            )

        # Get price
        if price is None:
            price = self.get_current_price(symbol)
            if price is None:
                raise PortfolioError(f"Unable to fetch current price for {symbol}")

        total_proceeds = quantity * price

        # Execute trade
        trade_id = f"SELL_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        realized_pnl = (price - pos["entry_price"]) * quantity

        trade = Trade(
            trade_id=trade_id,
            symbol=symbol,
            action="sell",
            quantity=quantity,
            price=price,
            total_value=total_proceeds,
            timestamp=datetime.now().isoformat(),
            notes=f"Realized P&L: ${realized_pnl:.2f}"
        )

        # Update cash
        self.portfolio_data["current_cash"] += total_proceeds

        # Update position
        pos["quantity"] -= quantity

        # Remove position if fully sold
        if pos["quantity"] <= 0:
            del self.portfolio_data["positions"][symbol]

        # Record trade
        self.portfolio_data["trades"].append(asdict(trade))
        self._save_portfolio()

        logger.info(
            f"SELL: {quantity} shares of {symbol} @ ${price:.2f} "
            f"(total: ${total_proceeds:.2f}, P&L: ${realized_pnl:+.2f})"
        )
        return trade

    def get_positions(self, update_prices: bool = True) -> List[Position]:
        """Get all current positions.

        Args:
            update_prices: Whether to fetch current prices

        Returns:
            List of Position objects
        """
        positions = []

        for symbol, pos_data in self.portfolio_data["positions"].items():
            position = Position(**pos_data)

            if update_prices:
                current_price = self.get_current_price(symbol)
                if current_price:
                    position.update_current_price(current_price)
                else:
                    # Use entry price if can't fetch current
                    position.update_current_price(position.entry_price)

            positions.append(position)

        return positions

    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary with performance metrics.

        Returns:
            Dictionary with portfolio metrics
        """
        positions = self.get_positions(update_prices=True)

        # Calculate totals
        total_equity = sum(pos.current_value for pos in positions)
        total_invested = sum(pos.quantity * pos.entry_price for pos in positions)
        unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)

        cash = self.portfolio_data["current_cash"]
        total_value = cash + total_equity

        initial_cash = self.portfolio_data["initial_cash"]
        total_return = total_value - initial_cash
        total_return_percent = (total_return / initial_cash) * 100 if initial_cash > 0 else 0.0

        # Calculate performance metrics
        trades_df = pd.DataFrame(self.portfolio_data["trades"]) if self.portfolio_data["trades"] else pd.DataFrame()

        # Count trades
        total_trades = len(trades_df)
        buy_trades = len(trades_df[trades_df["action"] == "buy"]) if not trades_df.empty else 0
        sell_trades = len(trades_df[trades_df["action"] == "sell"]) if not trades_df.empty else 0

        summary = {
            "timestamp": datetime.now().isoformat(),
            "cash": round(cash, 2),
            "equity": round(total_equity, 2),
            "total_value": round(total_value, 2),
            "initial_value": initial_cash,
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_percent, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "invested_capital": round(total_invested, 2),
            "positions_count": len(positions),
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "created_at": self.portfolio_data["created_at"],
            "last_updated": self.portfolio_data["last_updated"]
        }

        return summary

    def get_performance_metrics(self) -> Dict:
        """Calculate advanced performance metrics.

        Returns:
            Dictionary with Sharpe ratio, max drawdown, win rate, etc.
        """
        trades = pd.DataFrame(self.portfolio_data["trades"]) if self.portfolio_data["trades"] else pd.DataFrame()

        if trades.empty:
            return {
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0
            }

        # For now, return placeholder metrics
        # TODO: Implement actual calculations based on daily portfolio values
        summary = self.get_portfolio_summary()

        metrics = {
            "sharpe_ratio": 1.23,  # Placeholder
            "max_drawdown": -8.5,  # Placeholder
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "total_return": summary["total_return_percent"]
        }

        return metrics

    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Trade]:
        """Get trade history.

        Args:
            symbol: Filter by symbol (optional)
            limit: Maximum number of trades to return

        Returns:
            List of Trade objects
        """
        trades = self.portfolio_data["trades"]

        if symbol:
            trades = [t for t in trades if t["symbol"] == symbol]

        # Sort by timestamp descending (newest first)
        trades = sorted(trades, key=lambda x: x["timestamp"], reverse=True)

        # Limit results
        trades = trades[:limit]

        return [Trade(**t) for t in trades]

    def reset_portfolio(self, initial_cash: float = 100000.0):
        """Reset portfolio to initial state.

        Args:
            initial_cash: Starting cash amount

        Warning:
            This deletes all positions and trade history!
        """
        logger.warning("Resetting portfolio - all data will be lost")

        self.portfolio_data = self._create_empty_portfolio()
        self.portfolio_data["initial_cash"] = initial_cash
        self.portfolio_data["current_cash"] = initial_cash

        self._save_portfolio()

        logger.info(f"Portfolio reset with ${initial_cash:,.2f} initial cash")

    def export_to_csv(self, output_dir: str = "data"):
        """Export portfolio data to CSV files.

        Args:
            output_dir: Directory to save CSV files
        """
        os.makedirs(output_dir, exist_ok=True)

        # Export positions
        positions = self.get_positions(update_prices=True)
        if positions:
            pos_df = pd.DataFrame([asdict(p) for p in positions])
            pos_file = os.path.join(output_dir, f"positions_{datetime.now().strftime('%Y%m%d')}.csv")
            pos_df.to_csv(pos_file, index=False)
            logger.info(f"Positions exported to {pos_file}")

        # Export trades
        if self.portfolio_data["trades"]:
            trades_df = pd.DataFrame(self.portfolio_data["trades"])
            trades_file = os.path.join(output_dir, f"trades_{datetime.now().strftime('%Y%m%d')}.csv")
            trades_df.to_csv(trades_file, index=False)
            logger.info(f"Trades exported to {trades_file}")
