"""Tests for RiskManager."""

import pytest
from src.trading_engine.risk_manager import RiskManager


class TestRiskManager:
    """Tests for RiskManager."""

    @pytest.fixture
    def risk_manager(self):
        """Create risk manager with default settings."""
        return RiskManager(
            max_position_size=0.10,
            stop_loss_pct=0.05,
            take_profit_pct=0.10
        )

    def test_initialization(self, risk_manager):
        """Test risk manager initialization."""
        assert risk_manager.max_position_size == 0.10
        assert risk_manager.stop_loss_pct == 0.05
        assert risk_manager.take_profit_pct == 0.10

    def test_calculate_position_size(self, risk_manager):
        """Test position size calculation."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        assert "position_value" in result
        assert "shares" in result
        assert "stop_loss" in result
        assert "take_profit" in result
        assert "risk_amount" in result

        # Position value should be 10% of portfolio
        assert result["position_value"] == 10000.0
        # Shares should be position_value / current_price
        assert result["shares"] == 100

    def test_position_size_with_partial_strength(self, risk_manager):
        """Test position size with partial signal strength."""
        signal_strength = 0.5
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Position value should be 5% of portfolio (0.5 * 0.10)
        assert result["position_value"] == 5000.0
        assert result["shares"] == 50

    def test_stop_loss_calculation(self, risk_manager):
        """Test stop loss calculation."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Stop loss should be 5% below current price
        expected_stop_loss = 100.0 * (1 - 0.05)
        assert result["stop_loss"] == expected_stop_loss

    def test_take_profit_calculation(self, risk_manager):
        """Test take profit calculation."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Take profit should be 10% above current price
        expected_take_profit = 100.0 * (1 + 0.10)
        assert result["take_profit"] == expected_take_profit

    def test_risk_amount_calculation(self, risk_manager):
        """Test risk amount calculation."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Risk amount should be position_value * stop_loss_pct
        expected_risk = 10000.0 * 0.05
        assert result["risk_amount"] == expected_risk

    def test_shares_rounding(self, risk_manager):
        """Test that shares are rounded to integers."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 333.33  # Will result in non-integer shares

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        assert isinstance(result["shares"], int)
        assert result["shares"] >= 0

    def test_zero_signal_strength(self, risk_manager):
        """Test with zero signal strength."""
        signal_strength = 0.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        assert result["position_value"] == 0.0
        assert result["shares"] == 0

    def test_custom_parameters(self):
        """Test risk manager with custom parameters."""
        risk_manager = RiskManager(
            max_position_size=0.20,
            stop_loss_pct=0.10,
            take_profit_pct=0.20
        )

        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Position value should be 20% of portfolio
        assert result["position_value"] == 20000.0
        # Stop loss should be 10% below
        assert result["stop_loss"] == 90.0
        # Take profit should be 20% above
        assert result["take_profit"] == 120.0

    def test_small_portfolio(self, risk_manager):
        """Test with small portfolio value."""
        signal_strength = 1.0
        portfolio_value = 1000.0
        current_price = 50.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Position value should be 10% of portfolio
        assert result["position_value"] == 100.0
        # Shares should be 2 (100 / 50)
        assert result["shares"] == 2

    def test_expensive_stock(self, risk_manager):
        """Test with expensive stock price."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 5000.0  # Expensive stock

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Shares should be 2 (10000 / 5000)
        assert result["shares"] == 2
        assert result["position_value"] == 10000.0

    def test_position_larger_than_stock_price(self, risk_manager):
        """Test when position value is larger than stock price."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 1.0  # Very cheap stock

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Shares should be 10000 (10000 / 1)
        assert result["shares"] == 10000

    def test_max_position_size_constraint(self, risk_manager):
        """Test that max position size is respected."""
        signal_strength = 1.0
        portfolio_value = 100000.0
        current_price = 100.0

        result = risk_manager.calculate_position_size(
            signal_strength, portfolio_value, current_price
        )

        # Position should not exceed max_position_size * portfolio_value
        assert result["position_value"] <= risk_manager.max_position_size * portfolio_value
