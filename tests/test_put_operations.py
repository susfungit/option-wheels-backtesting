"""Tests for put operations (_sell_put and _check_put_assignment)."""

import pytest
import pandas as pd


class TestSellPut:
    """Tests for _sell_put method."""

    def test_sell_put_correct_strike(self, backtest_instance):
        """Test that put strike is calculated correctly (stock_price * (1 - put_otm_pct))."""
        date = pd.Timestamp('2024-01-05')
        stock_price = 100.0

        trade = backtest_instance._sell_put(date, stock_price)

        # Strike = 100 * (1 - 0.05) = 95
        assert trade['strike'] == 95.0

    def test_sell_put_increases_cash(self, backtest_instance):
        """Test that selling a put increases cash by premium amount."""
        initial_cash = backtest_instance.cash
        date = pd.Timestamp('2024-01-05')
        stock_price = 100.0

        trade = backtest_instance._sell_put(date, stock_price)

        assert backtest_instance.cash == initial_cash + trade['premium']
        assert backtest_instance.cash > initial_cash

    def test_sell_put_correct_trade_dict(self, backtest_instance):
        """Test that trade dict contains all required keys."""
        date = pd.Timestamp('2024-01-05')
        stock_price = 100.0

        trade = backtest_instance._sell_put(date, stock_price)

        required_keys = ['date', 'type', 'stock_price', 'strike', 'premium', 'cash', 'status']
        for key in required_keys:
            assert key in trade, f"Missing key: {key}"

        assert trade['type'] == 'SELL_PUT'
        assert trade['date'] == date
        assert trade['stock_price'] == stock_price

    def test_sell_put_status_pending(self, backtest_instance):
        """Test that new put trade has 'pending' status."""
        date = pd.Timestamp('2024-01-05')
        stock_price = 100.0

        trade = backtest_instance._sell_put(date, stock_price)

        assert trade['status'] == 'pending'


class TestCheckPutAssignment:
    """Tests for _check_put_assignment method."""

    def test_put_assigned_when_below_strike(self, backtest_instance, sample_put_trade):
        """Test that put is assigned when low price drops below strike."""
        low_price = 90.0  # Below strike of 95
        close_price = 92.0

        assigned, trade = backtest_instance._check_put_assignment(
            sample_put_trade, low_price, close_price
        )

        assert assigned is True
        assert trade['status'] == 'ASSIGNED'

    def test_put_expires_when_above_strike(self, backtest_instance, sample_put_trade):
        """Test that put expires worthless when low stays above strike."""
        low_price = 96.0  # Above strike of 95
        close_price = 98.0

        assigned, trade = backtest_instance._check_put_assignment(
            sample_put_trade, low_price, close_price
        )

        assert assigned is False
        assert trade['status'] == 'EXPIRED_WORTHLESS'

    def test_put_assignment_at_strike(self, backtest_instance, sample_put_trade):
        """Test edge case: low equals strike (should assign)."""
        low_price = 95.0  # Exactly at strike
        close_price = 96.0

        assigned, trade = backtest_instance._check_put_assignment(
            sample_put_trade, low_price, close_price
        )

        # Based on code: if low_price <= trade['strike'], so equals should trigger
        assert assigned is True
        assert trade['status'] == 'ASSIGNED'

    def test_put_assignment_updates_state(self, backtest_instance, sample_put_trade):
        """Test that assignment updates owns_stock and shares_owned."""
        low_price = 90.0
        close_price = 92.0

        assert backtest_instance.owns_stock is False
        assert backtest_instance.shares_owned == 0

        backtest_instance._check_put_assignment(sample_put_trade, low_price, close_price)

        assert backtest_instance.owns_stock is True
        assert backtest_instance.shares_owned == 100

    def test_put_assignment_decreases_cash(self, backtest_instance, sample_put_trade):
        """Test that assignment decreases cash by (strike * 100)."""
        low_price = 90.0
        close_price = 92.0
        initial_cash = backtest_instance.cash

        backtest_instance._check_put_assignment(sample_put_trade, low_price, close_price)

        expected_cost = sample_put_trade['strike'] * 100  # 95 * 100 = 9500
        assert backtest_instance.cash == initial_cash - expected_cost

    def test_put_insufficient_cash(self, backtest_instance, sample_put_trade):
        """Test behavior when insufficient cash for assignment."""
        backtest_instance.cash = 1000  # Not enough to buy 100 shares at $95
        low_price = 90.0
        close_price = 92.0

        assigned, trade = backtest_instance._check_put_assignment(
            sample_put_trade, low_price, close_price
        )

        # Current implementation does NOT check for sufficient cash before
        # returning True, it only checks inside the if block
        # So it returns True for the condition check, but doesn't execute assignment
        assert assigned is False  # Condition met but assignment not executed
        # The trade is modified even if assignment fails (status set but state unchanged)
