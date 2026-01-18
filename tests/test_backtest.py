"""Integration tests for run_backtest method."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


class TestRunBacktest:
    """Integration tests for the complete backtest flow."""

    def test_backtest_single_week(self):
        """Test backtest with minimal data (1 week)."""
        single_week_data = pd.DataFrame({
            'Open': [100.0],
            'High': [105.0],
            'Low': [98.0],
            'Close': [102.0],
            'Volume': [1e6],
        }, index=pd.date_range('2024-01-05', periods=1, freq='W-FRI'))

        with patch('wheel_strategy_backtest.yf.Ticker') as mock:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = single_week_data
            mock.return_value = mock_ticker

            from wheel_strategy_backtest import WheelStrategyBacktest
            bt = WheelStrategyBacktest(
                ticker='TEST',
                start_date='2024-01-01',
                end_date='2024-01-10',
                initial_capital=50000
            )

            trades_df = bt.run_backtest()

            assert len(trades_df) == 1
            assert trades_df.iloc[0]['type'] == 'SELL_PUT'

    def test_backtest_no_assignments(self):
        """Test backtest where all puts expire worthless."""
        # Stock stays above put strikes (price rises)
        rising_data = pd.DataFrame({
            'Open': [100.0, 105.0, 110.0, 115.0],
            'High': [105.0, 110.0, 115.0, 120.0],
            'Low': [99.0, 104.0, 109.0, 114.0],  # All lows above 5% OTM strikes
            'Close': [103.0, 108.0, 113.0, 118.0],
            'Volume': [1e6, 1e6, 1e6, 1e6],
        }, index=pd.date_range('2024-01-05', periods=4, freq='W-FRI'))

        with patch('wheel_strategy_backtest.yf.Ticker') as mock:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = rising_data
            mock.return_value = mock_ticker

            from wheel_strategy_backtest import WheelStrategyBacktest
            bt = WheelStrategyBacktest(
                ticker='TEST',
                start_date='2024-01-01',
                end_date='2024-02-01',
                initial_capital=50000
            )

            trades_df = bt.run_backtest()

            # All should be puts that expired worthless
            assert all(trades_df['type'] == 'SELL_PUT')
            assert all(trades_df['status'] == 'EXPIRED_WORTHLESS')
            assert bt.owns_stock is False

    def test_backtest_full_wheel_cycle(self):
        """Test a complete wheel cycle: put assigned then called away."""
        # Week 1: Put at 95, low is 94 -> assigned
        # Week 2: Own stock, call at ~99.75, high is 102 -> called away
        cycle_data = pd.DataFrame({
            'Open': [100.0, 95.0],
            'High': [103.0, 102.0],
            'Low': [94.0, 93.0],  # Week 1 triggers assignment
            'Close': [96.0, 100.0],
            'Volume': [1e6, 1e6],
        }, index=pd.date_range('2024-01-05', periods=2, freq='W-FRI'))

        with patch('wheel_strategy_backtest.yf.Ticker') as mock:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = cycle_data
            mock.return_value = mock_ticker

            from wheel_strategy_backtest import WheelStrategyBacktest
            bt = WheelStrategyBacktest(
                ticker='TEST',
                start_date='2024-01-01',
                end_date='2024-01-20',
                initial_capital=50000
            )

            trades_df = bt.run_backtest()

            assert len(trades_df) == 2
            assert trades_df.iloc[0]['type'] == 'SELL_PUT'
            assert trades_df.iloc[0]['status'] == 'ASSIGNED'
            assert trades_df.iloc[1]['type'] == 'SELL_CALL'
            assert trades_df.iloc[1]['status'] == 'CALLED_AWAY'
            # After full cycle, should not own stock
            assert bt.owns_stock is False

    def test_backtest_multiple_cycles(self):
        """Test multiple complete wheel cycles."""
        # Create data that triggers multiple assign/call-away cycles
        multi_cycle_data = pd.DataFrame({
            'Open': [100.0, 95.0, 100.0, 95.0, 100.0, 95.0],
            'High': [103.0, 102.0, 103.0, 102.0, 103.0, 102.0],
            'Low': [94.0, 93.0, 94.0, 93.0, 94.0, 93.0],
            'Close': [96.0, 100.0, 96.0, 100.0, 96.0, 100.0],
            'Volume': [1e6] * 6,
        }, index=pd.date_range('2024-01-05', periods=6, freq='W-FRI'))

        with patch('wheel_strategy_backtest.yf.Ticker') as mock:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = multi_cycle_data
            mock.return_value = mock_ticker

            from wheel_strategy_backtest import WheelStrategyBacktest
            bt = WheelStrategyBacktest(
                ticker='TEST',
                start_date='2024-01-01',
                end_date='2024-02-20',
                initial_capital=50000
            )

            trades_df = bt.run_backtest()

            # Should have 3 puts assigned and 3 calls executed
            put_trades = trades_df[trades_df['type'] == 'SELL_PUT']
            call_trades = trades_df[trades_df['type'] == 'SELL_CALL']

            assert len(put_trades) == 3
            assert len(call_trades) == 3

    def test_backtest_returns_dataframe(self, backtest_instance):
        """Test that run_backtest returns a pandas DataFrame."""
        result = backtest_instance.run_backtest()

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_backtest_long_stock_hold(self):
        """Test scenario where stock is assigned but never called away."""
        # Stock drops and stays low
        holding_data = pd.DataFrame({
            'Open': [100.0, 90.0, 85.0, 82.0],
            'High': [103.0, 92.0, 87.0, 84.0],  # Never reaches call strike
            'Low': [94.0, 85.0, 80.0, 78.0],
            'Close': [91.0, 86.0, 81.0, 79.0],
            'Volume': [1e6] * 4,
        }, index=pd.date_range('2024-01-05', periods=4, freq='W-FRI'))

        with patch('wheel_strategy_backtest.yf.Ticker') as mock:
            mock_ticker = MagicMock()
            mock_ticker.history.return_value = holding_data
            mock.return_value = mock_ticker

            from wheel_strategy_backtest import WheelStrategyBacktest
            bt = WheelStrategyBacktest(
                ticker='TEST',
                start_date='2024-01-01',
                end_date='2024-02-01',
                initial_capital=50000
            )

            trades_df = bt.run_backtest()

            # First trade is put, gets assigned
            # Then calls are sold but all expire worthless
            assert trades_df.iloc[0]['type'] == 'SELL_PUT'
            assert trades_df.iloc[0]['status'] == 'ASSIGNED'

            # Remaining should be calls that expired worthless
            call_trades = trades_df[trades_df['type'] == 'SELL_CALL']
            assert all(call_trades['status'] == 'EXPIRED_WORTHLESS')

            # Should still own stock at end
            assert bt.owns_stock is True
            assert bt.shares_owned == 100
