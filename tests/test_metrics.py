"""Tests for calculate_metrics method."""

import pytest
import pandas as pd


class TestCalculateMetrics:
    """Tests for the metrics calculation logic."""

    def test_metrics_total_value(self, backtest_instance):
        """Test that total_value = cash + stock_value."""
        # Run a backtest first
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        expected_total = metrics['final_cash'] + metrics['stock_value']
        assert metrics['total_value'] == expected_total

    def test_metrics_profit(self, backtest_instance):
        """Test that profit = total_value - initial_capital."""
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        expected_profit = metrics['total_value'] - metrics['initial_capital']
        assert metrics['total_profit'] == expected_profit

    def test_metrics_return_pct(self, backtest_instance):
        """Test that return percentage is calculated correctly."""
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        expected_return = (metrics['total_profit'] / metrics['initial_capital']) * 100
        assert abs(metrics['total_return_pct'] - expected_return) < 0.01

    def test_metrics_annualized_return(self, backtest_instance):
        """Test that annualized return uses compound formula."""
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        # Annualized = ((final/initial)^(1/years) - 1) * 100
        years = metrics['years_held']
        if years > 0:
            expected = ((metrics['total_value'] / metrics['initial_capital']) ** (1/years) - 1) * 100
            assert abs(metrics['annualized_return_pct'] - expected) < 0.01

    def test_metrics_buy_hold_comparison(self, backtest_instance):
        """Test that buy-and-hold benchmark is calculated correctly."""
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        # Buy hold: buy shares at start, sell at end
        initial_shares = metrics['initial_capital'] / metrics['starting_price']
        expected_value = initial_shares * metrics['ending_price']

        assert abs(metrics['buy_hold_value'] - expected_value) < 0.01

    def test_metrics_trade_counts(self, backtest_instance):
        """Test that trade counts are correct."""
        trades_df = backtest_instance.run_backtest()
        metrics = backtest_instance.calculate_metrics(trades_df)

        # Verify counts match DataFrame
        put_count = len(trades_df[trades_df['type'] == 'SELL_PUT'])
        call_count = len(trades_df[trades_df['type'] == 'SELL_CALL'])
        assigned_count = len(trades_df[trades_df['status'] == 'ASSIGNED'])
        called_away_count = len(trades_df[trades_df['status'] == 'CALLED_AWAY'])

        assert metrics['put_trades'] == put_count
        assert metrics['call_trades'] == call_count
        assert metrics['times_assigned'] == assigned_count
        assert metrics['times_called_away'] == called_away_count

    def test_metrics_stock_value_when_holding(self, backtest_instance):
        """Test that stock_value is non-zero when holding stock at end."""
        # Manipulate state to ensure we own stock at end
        trades_df = backtest_instance.run_backtest()

        # Force ownership state for this test
        backtest_instance.owns_stock = True
        backtest_instance.shares_owned = 100
        backtest_instance.stock_purchase_price = 90.0

        metrics = backtest_instance.calculate_metrics(trades_df)

        expected_value = backtest_instance.data['Close'].iloc[-1] * 100
        assert metrics['stock_value'] == expected_value
        assert metrics['owns_stock_at_end'] is True

    def test_metrics_stock_value_when_not_holding(self, backtest_instance):
        """Test that stock_value is 0 when not holding stock."""
        trades_df = backtest_instance.run_backtest()

        # Force no ownership state
        backtest_instance.owns_stock = False
        backtest_instance.shares_owned = 0

        metrics = backtest_instance.calculate_metrics(trades_df)

        assert metrics['stock_value'] == 0
        assert metrics['owns_stock_at_end'] is False
