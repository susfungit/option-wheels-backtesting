"""Tests for export security fixes (path traversal prevention)."""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


@pytest.fixture
def sample_trades_df():
    """Sample trades DataFrame for export testing."""
    return pd.DataFrame({
        'date': pd.date_range('2024-01-05', periods=3, freq='W-FRI'),
        'type': ['SELL_PUT', 'SELL_PUT', 'SELL_CALL'],
        'strike': [95.0, 93.0, 99.0],
        'premium': [190.0, 186.0, 198.0],
        'status': ['EXPIRED_WORTHLESS', 'ASSIGNED', 'EXPIRED_WORTHLESS']
    })


@pytest.fixture
def backtest_for_export(mock_yfinance):
    """Backtest instance for testing exports."""
    from wheel_strategy_backtest import WheelStrategyBacktest
    return WheelStrategyBacktest(
        ticker='TEST',
        start_date='2024-01-01',
        end_date='2024-12-31',
        initial_capital=50000
    )


class TestExportTradesPathTraversal:
    """Tests for path traversal prevention in export_trades."""

    def test_default_filename_is_safe(self, backtest_for_export, sample_trades_df):
        """Default auto-generated filename should be safe."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(sample_trades_df)

            # Should not contain path separators
            assert '/' not in filename
            assert '\\' not in filename
            # Should follow expected pattern
            assert filename.startswith('wheel_backtest_TEST_')
            assert filename.endswith('.csv')

    def test_path_traversal_unix_stripped(self, backtest_for_export, sample_trades_df):
        """Unix-style path traversal should be stripped."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='../../../etc/passwd.csv'
            )

            # Should only keep the basename
            assert filename == 'passwd.csv'
            assert '/' not in filename

    def test_path_traversal_windows_stripped(self, backtest_for_export, sample_trades_df):
        """Windows-style path traversal should be stripped."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='..\\..\\Windows\\System32\\config.csv'
            )

            # Should only keep the basename
            assert filename == 'config.csv'
            assert '\\' not in filename

    def test_absolute_path_stripped(self, backtest_for_export, sample_trades_df):
        """Absolute paths should be stripped to basename."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='/tmp/malicious/output.csv'
            )

            assert filename == 'output.csv'

    def test_simple_filename_preserved(self, backtest_for_export, sample_trades_df):
        """Simple filename without path should be preserved."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='my_backtest.csv'
            )

            assert filename == 'my_backtest.csv'

    def test_empty_filename_after_sanitize_raises(self, backtest_for_export, sample_trades_df):
        """Empty filename after sanitization should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid filename"):
            backtest_for_export.export_trades(sample_trades_df, filename='/')

    def test_only_slashes_raises(self, backtest_for_export, sample_trades_df):
        """Filename with only slashes should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid filename"):
            backtest_for_export.export_trades(sample_trades_df, filename='///')

    def test_hidden_file_preserved(self, backtest_for_export, sample_trades_df):
        """Hidden files (starting with dot) should be preserved."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='.hidden_backtest.csv'
            )

            assert filename == '.hidden_backtest.csv'

    def test_nested_path_traversal_stripped(self, backtest_for_export, sample_trades_df):
        """Nested path traversal attempts should be stripped."""
        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='foo/../../../bar/baz/../output.csv'
            )

            assert filename == 'output.csv'

    def test_csv_actually_written(self, backtest_for_export, sample_trades_df, tmp_path):
        """Verify CSV is actually written to the correct location."""
        # Change to temp directory for this test
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            filename = backtest_for_export.export_trades(
                sample_trades_df,
                filename='test_output.csv'
            )

            # Verify file was created in current directory
            assert os.path.exists(filename)
            assert os.path.dirname(os.path.abspath(filename)) == str(tmp_path)

            # Verify content
            df_read = pd.read_csv(filename)
            assert len(df_read) == len(sample_trades_df)
        finally:
            os.chdir(original_cwd)


class TestExportTradesWithMaliciousTicker:
    """Tests ensuring ticker in filename is safe."""

    def test_ticker_in_default_filename(self, mock_yfinance, sample_trades_df):
        """Ticker used in default filename should be uppercase alphanumeric."""
        from wheel_strategy_backtest import WheelStrategyBacktest

        # The ticker is already validated/uppercased in __init__
        backtest = WheelStrategyBacktest(
            ticker='tsla',  # lowercase input
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_capital=50000
        )

        with patch.object(pd.DataFrame, 'to_csv') as mock_csv:
            filename = backtest.export_trades(sample_trades_df)

            # Should be uppercase
            assert 'TSLA' in filename
            assert 'tsla' not in filename
