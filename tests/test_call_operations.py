"""Tests for call operations (_sell_call and _check_call_assignment)."""

import pytest
import pandas as pd


class TestSellCall:
    """Tests for _sell_call method."""

    def test_sell_call_correct_strike(self, backtest_instance):
        """Test that call strike is calculated correctly (stock_price * (1 + call_otm_pct))."""
        # Setup: need to own stock first
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        date = pd.Timestamp('2024-01-12')
        stock_price = 100.0

        trade = backtest_instance._sell_call(date, stock_price)

        # Strike = 100 * (1 + 0.05) = 105
        assert trade['strike'] == 105.0

    def test_sell_call_increases_cash(self, backtest_instance):
        """Test that selling a call increases cash by premium amount."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        initial_cash = backtest_instance.cash
        date = pd.Timestamp('2024-01-12')
        stock_price = 100.0

        trade = backtest_instance._sell_call(date, stock_price)

        assert backtest_instance.cash == initial_cash + trade['premium']
        assert backtest_instance.cash > initial_cash

    def test_sell_call_tracks_cost_basis(self, backtest_instance):
        """Test that call trade includes cost_basis from stock purchase."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        date = pd.Timestamp('2024-01-12')
        stock_price = 100.0

        trade = backtest_instance._sell_call(date, stock_price)

        assert 'cost_basis' in trade
        assert trade['cost_basis'] == 95.0


class TestCheckCallAssignment:
    """Tests for _check_call_assignment method."""

    def test_call_assigned_when_above_strike(self, backtest_instance, sample_call_trade):
        """Test that call is assigned when high price rises above strike."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        high_price = 105.0  # Above strike of 99.75
        close_price = 102.0

        assigned, trade = backtest_instance._check_call_assignment(
            sample_call_trade, high_price, close_price
        )

        assert assigned is True
        assert trade['status'] == 'CALLED_AWAY'

    def test_call_expires_when_below_strike(self, backtest_instance, sample_call_trade):
        """Test that call expires worthless when high stays below strike."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        high_price = 98.0  # Below strike of 99.75
        close_price = 96.0

        assigned, trade = backtest_instance._check_call_assignment(
            sample_call_trade, high_price, close_price
        )

        assert assigned is False
        assert trade['status'] == 'EXPIRED_WORTHLESS'

    def test_call_assignment_at_strike(self, backtest_instance, sample_call_trade):
        """Test edge case: high equals strike (should assign)."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        high_price = 99.75  # Exactly at strike
        close_price = 98.0

        assigned, trade = backtest_instance._check_call_assignment(
            sample_call_trade, high_price, close_price
        )

        # Based on code: if high_price >= trade['strike'], so equals should trigger
        assert assigned is True
        assert trade['status'] == 'CALLED_AWAY'

    def test_call_assignment_updates_state(self, backtest_instance, sample_call_trade):
        """Test that assignment updates owns_stock and shares_owned."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0

        high_price = 105.0
        close_price = 102.0

        backtest_instance._check_call_assignment(sample_call_trade, high_price, close_price)

        assert backtest_instance.owns_stock is False
        assert backtest_instance.shares_owned == 0
        assert backtest_instance.stock_purchase_price == 0

    def test_call_assignment_increases_cash(self, backtest_instance, sample_call_trade):
        """Test that assignment increases cash by (strike * shares)."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0
        initial_cash = backtest_instance.cash

        high_price = 105.0
        close_price = 102.0

        backtest_instance._check_call_assignment(sample_call_trade, high_price, close_price)

        expected_proceeds = sample_call_trade['strike'] * 100  # 99.75 * 100 = 9975
        assert backtest_instance.cash == initial_cash + expected_proceeds

    def test_call_assignment_calculates_gain(self, backtest_instance, sample_call_trade):
        """Test that stock_gain is calculated as (strike - cost_basis) * shares."""
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 95.0
        initial_stock_gains = backtest_instance.total_stock_gains

        high_price = 105.0
        close_price = 102.0

        assigned, trade = backtest_instance._check_call_assignment(
            sample_call_trade, high_price, close_price
        )

        expected_gain = (sample_call_trade['strike'] - 95.0) * 100  # (99.75 - 95) * 100 = 475
        assert trade['stock_gain'] == expected_gain
        assert backtest_instance.total_stock_gains == initial_stock_gains + expected_gain
