"""Market monitoring service for event-based retraining."""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data_ingestion.data_fetcher import YahooDataFetcher
from src.utils.logger import LoggerMixin


class MarketMonitor(LoggerMixin):
    """Monitor market conditions for event-based retraining."""

    def __init__(self):
        """Initialize market monitor."""
        self.data_fetcher = YahooDataFetcher()
        self.events_file = Path("models/market_events.json")
        self._ensure_events_file()

        # Market indices for different regions
        self.market_indices = {
            "us": "^GSPC",  # S&P 500
            "vietnam": "^VNINDEX",  # VN Index (if available, otherwise use proxy)
        }

    def _ensure_events_file(self):
        """Ensure market events file exists."""
        if not self.events_file.exists():
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_events([])

    def _load_events(self) -> List[Dict[str, Any]]:
        """Load market events history."""
        try:
            with open(self.events_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load market events: {e}")
            return []

    def _save_events(self, events: List[Dict[str, Any]]):
        """Save market events history."""
        try:
            with open(self.events_file, "w") as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save market events: {e}")

    def _add_market_event(
        self,
        market: str,
        event_type: str,
        drop_percentage: float,
        start_date: str,
        end_date: str,
        details: Optional[Dict] = None,
    ):
        """Add a market event to history."""
        events = self._load_events()
        event = {
            "market": market,
            "event_type": event_type,
            "drop_percentage": drop_percentage,
            "start_date": start_date,
            "end_date": end_date,
            "detected_at": datetime.now().isoformat(),
            "details": details or {},
        }
        events.append(event)
        self._save_events(events)

    def calculate_market_change(
        self, market: str = "us", lookback_days: int = 5
    ) -> Dict[str, Any]:
        """Calculate market change over a period.

        Args:
            market: Market region (us, vietnam)
            lookback_days: Number of days to look back

        Returns:
            Dictionary with market change information
        """
        try:
            index_symbol = self.market_indices.get(market)
            if not index_symbol:
                raise ValueError(f"Unknown market: {market}")

            self.logger.info(
                f"Fetching {market} market data ({index_symbol}) for last {lookback_days} days"
            )

            # Fetch market index data
            # For Vietnam, we may need to use a proxy if ^VNINDEX is not available
            try:
                data = self.data_fetcher.fetch_data(
                    index_symbol, period=f"{lookback_days + 5}d"
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch {index_symbol}: {e}. "
                    f"Using fallback method for {market} market"
                )
                # For Vietnam, use a major stock as proxy
                if market == "vietnam":
                    data = self.data_fetcher.fetch_data("VCB.VN", period=f"{lookback_days + 5}d")
                else:
                    raise

            if data is None or len(data) < 2:
                raise ValueError(f"Insufficient data for {market} market")

            # Calculate change from lookback_days ago to now
            # Sort by date to ensure correct order
            data = data.sort_index()

            # Get the most recent close price
            current_price = data["close"].iloc[-1]

            # Get the price from lookback_days ago (or closest available)
            if len(data) >= lookback_days + 1:
                past_price = data["close"].iloc[-(lookback_days + 1)]
            else:
                # Use the oldest available data
                past_price = data["close"].iloc[0]

            # Calculate percentage change
            change_pct = ((current_price - past_price) / past_price) * 100

            # Get peak and trough during period
            period_high = data["close"].iloc[-lookback_days:].max()
            period_low = data["close"].iloc[-lookback_days:].min()
            max_drawdown = ((period_low - period_high) / period_high) * 100

            result = {
                "market": market,
                "index_symbol": index_symbol,
                "current_price": float(current_price),
                "past_price": float(past_price),
                "change_percentage": float(change_pct),
                "max_drawdown": float(max_drawdown),
                "lookback_days": lookback_days,
                "start_date": data.index[-(lookback_days + 1)].strftime("%Y-%m-%d")
                if len(data) >= lookback_days + 1
                else data.index[0].strftime("%Y-%m-%d"),
                "end_date": data.index[-1].strftime("%Y-%m-%d"),
                "data_points": len(data),
            }

            self.logger.info(
                f"{market} market change: {change_pct:.2f}% over {lookback_days} days, "
                f"max drawdown: {max_drawdown:.2f}%"
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to calculate market change for {market}: {e}")
            return {
                "market": market,
                "error": str(e),
                "change_percentage": 0.0,
                "max_drawdown": 0.0,
            }

    def check_market_drop_event(
        self,
        market: str = "us",
        threshold_percentage: float = 5.0,
        lookback_days: int = 5,
    ) -> Dict[str, Any]:
        """Check if there's a significant market drop event.

        Args:
            market: Market region (us, vietnam)
            threshold_percentage: Drop threshold to trigger event (positive number)
            lookback_days: Number of days to look back

        Returns:
            Dictionary with event information
        """
        change_data = self.calculate_market_change(market, lookback_days)

        # Check if there was a significant drop
        # Use max_drawdown for more accurate detection
        drop_detected = change_data.get("max_drawdown", 0) <= -threshold_percentage

        if drop_detected:
            self.logger.warning(
                f"Market drop event detected in {market}: "
                f"{change_data['max_drawdown']:.2f}% (threshold: -{threshold_percentage}%)"
            )

            # Record the event
            self._add_market_event(
                market=market,
                event_type="significant_drop",
                drop_percentage=abs(change_data.get("max_drawdown", 0)),
                start_date=change_data.get("start_date", ""),
                end_date=change_data.get("end_date", ""),
                details={
                    "threshold": threshold_percentage,
                    "lookback_days": lookback_days,
                    "change_percentage": change_data.get("change_percentage", 0),
                },
            )

        return {
            "event_detected": drop_detected,
            "market": market,
            "drop_percentage": abs(change_data.get("max_drawdown", 0)),
            "threshold": threshold_percentage,
            "market_data": change_data,
            "should_retrain": drop_detected,
        }

    def check_all_markets(
        self, threshold_percentage: float = 5.0, lookback_days: int = 5
    ) -> Dict[str, Any]:
        """Check all configured markets for drop events.

        Args:
            threshold_percentage: Drop threshold to trigger event
            lookback_days: Number of days to look back

        Returns:
            Dictionary with results for all markets
        """
        results = {}
        markets_with_events = []

        for market in self.market_indices.keys():
            result = self.check_market_drop_event(
                market, threshold_percentage, lookback_days
            )
            results[market] = result

            if result["event_detected"]:
                markets_with_events.append(market)

        return {
            "markets_checked": list(self.market_indices.keys()),
            "markets_with_events": markets_with_events,
            "any_events_detected": len(markets_with_events) > 0,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def get_market_events(
        self, market: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get historical market events.

        Args:
            market: Optional market to filter by
            limit: Maximum number of events to return

        Returns:
            List of market events
        """
        events = self._load_events()

        if market:
            events = [e for e in events if e["market"] == market]

        # Sort by detection date descending
        events = sorted(events, key=lambda x: x["detected_at"], reverse=True)

        return events[:limit]

    def get_symbols_for_market(self, market: str) -> List[str]:
        """Get list of symbols to retrain for a given market.

        Args:
            market: Market region

        Returns:
            List of stock symbols
        """
        # This could be loaded from config or database
        # For now, return some default symbols
        if market == "us":
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        elif market == "vietnam":
            return ["VCB.VN", "FPT.VN", "VHM.VN", "HPG.VN", "VNM.VN"]
        else:
            return []
