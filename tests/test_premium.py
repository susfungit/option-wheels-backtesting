"""Tests for _calculate_premium method."""

import pytest


class TestCalculatePremium:
    """Tests for the premium calculation logic."""

    def test_premium_at_the_money(self, backtest_instance):
        """Test premium calculation when strike equals stock price."""
        strike = 100.0
        stock_price = 100.0

        premium = backtest_instance._calculate_premium(strike, stock_price)

        # At ATM, adjustment should be 1.0 (no reduction)
        # Premium = strike * premium_pct * adjustment * 100
        # = 100 * 0.02 * 1.0 * 100 = 200
        assert premium == 200.0

    def test_premium_out_of_money(self, backtest_instance):
        """Test that OTM adjustment reduces premium."""
        strike = 95.0  # 5% OTM
        stock_price = 100.0

        premium = backtest_instance._calculate_premium(strike, stock_price)

        # OTM distance = |95 - 100| / 100 = 0.05
        # Adjustment = max(0.3, 1 - (0.05 * 5)) = max(0.3, 0.75) = 0.75
        # Premium = 95 * 0.02 * 0.75 * 100 = 142.5
        assert premium == 142.5

    def test_premium_far_otm(self, backtest_instance):
        """Test that far OTM hits minimum adjustment of 0.3."""
        strike = 80.0  # 20% OTM
        stock_price = 100.0

        premium = backtest_instance._calculate_premium(strike, stock_price)

        # OTM distance = |80 - 100| / 100 = 0.20
        # Adjustment = max(0.3, 1 - (0.20 * 5)) = max(0.3, 0.0) = 0.3
        # Premium = 80 * 0.02 * 0.3 * 100 = 48.0
        assert premium == 48.0

    def test_premium_in_the_money(self, backtest_instance):
        """Test premium when strike is ITM (adjustment still applies based on distance)."""
        strike = 105.0  # ITM for a put
        stock_price = 100.0

        premium = backtest_instance._calculate_premium(strike, stock_price)

        # OTM distance (using abs) = |105 - 100| / 100 = 0.05
        # Adjustment = max(0.3, 1 - (0.05 * 5)) = 0.75
        # Premium = 105 * 0.02 * 0.75 * 100 = 157.5
        assert premium == pytest.approx(157.5)

    def test_premium_zero_stock_price(self, backtest_instance):
        """Test handling of zero stock price edge case."""
        strike = 50.0
        stock_price = 0.0

        # This should raise ZeroDivisionError or handle gracefully
        # Current implementation will divide by zero
        with pytest.raises(ZeroDivisionError):
            backtest_instance._calculate_premium(strike, stock_price)

    def test_premium_deterministic(self, backtest_instance):
        """Test that same inputs always produce same output."""
        strike = 100.0
        stock_price = 105.0

        premium1 = backtest_instance._calculate_premium(strike, stock_price)
        premium2 = backtest_instance._calculate_premium(strike, stock_price)
        premium3 = backtest_instance._calculate_premium(strike, stock_price)

        assert premium1 == premium2 == premium3
