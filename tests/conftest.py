"""Shared fixtures for wheel strategy backtest tests."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_stock_data():
    """52 weeks of realistic stock data."""
    dates = pd.date_range('2024-01-05', periods=52, freq='W-FRI')
    np.random.seed(42)
    base_price = 100
    prices = base_price + np.cumsum(np.random.randn(52) * 2)
    return pd.DataFrame({
        'Open': prices,
        'High': prices + np.random.uniform(1, 5, 52),
        'Low': prices - np.random.uniform(1, 5, 52),
        'Close': prices + np.random.randn(52),
        'Volume': np.random.uniform(1e6, 1e7, 52),
    }, index=dates)


@pytest.fixture
def mock_yfinance(mock_stock_data):
    """Mock yfinance.Ticker to return test data."""
    with patch('wheel_strategy_backtest.yf.Ticker') as mock:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_stock_data
        mock.return_value = mock_ticker
        yield mock


@pytest.fixture
def backtest_instance(mock_yfinance):
    """Pre-configured backtest instance with mocked data."""
    from wheel_strategy_backtest import WheelStrategyBacktest
    return WheelStrategyBacktest(
        ticker='TEST',
        start_date='2024-01-01',
        end_date='2024-12-31',
        initial_capital=50000,
        put_otm_pct=0.05,
        call_otm_pct=0.05,
        premium_pct=0.02
    )


@pytest.fixture
def small_stock_data():
    """Small dataset for testing specific scenarios (4 weeks)."""
    dates = pd.date_range('2024-01-05', periods=4, freq='W-FRI')
    return pd.DataFrame({
        'Open': [100.0, 95.0, 90.0, 92.0],
        'High': [105.0, 98.0, 95.0, 98.0],
        'Low': [98.0, 90.0, 85.0, 88.0],
        'Close': [102.0, 92.0, 91.0, 96.0],
        'Volume': [1e6, 1.2e6, 1.5e6, 1.1e6],
    }, index=dates)


@pytest.fixture
def mock_yfinance_small(small_stock_data):
    """Mock yfinance.Ticker with small dataset."""
    with patch('wheel_strategy_backtest.yf.Ticker') as mock:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = small_stock_data
        mock.return_value = mock_ticker
        yield mock


@pytest.fixture
def backtest_small(mock_yfinance_small):
    """Backtest instance with small dataset for detailed testing."""
    from wheel_strategy_backtest import WheelStrategyBacktest
    return WheelStrategyBacktest(
        ticker='TEST',
        start_date='2024-01-01',
        end_date='2024-01-31',
        initial_capital=50000,
        put_otm_pct=0.05,
        call_otm_pct=0.05,
        premium_pct=0.02
    )


@pytest.fixture
def no_assignment_data():
    """Stock data where puts never get assigned (price stays high)."""
    dates = pd.date_range('2024-01-05', periods=4, freq='W-FRI')
    return pd.DataFrame({
        'Open': [100.0, 102.0, 104.0, 106.0],
        'High': [105.0, 107.0, 109.0, 111.0],
        'Low': [99.0, 101.0, 103.0, 105.0],  # All lows above 95 (5% OTM strike)
        'Close': [103.0, 105.0, 107.0, 109.0],
        'Volume': [1e6, 1.2e6, 1.5e6, 1.1e6],
    }, index=dates)


@pytest.fixture
def mock_yfinance_no_assignment(no_assignment_data):
    """Mock yfinance with data that never triggers put assignment."""
    with patch('wheel_strategy_backtest.yf.Ticker') as mock:
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = no_assignment_data
        mock.return_value = mock_ticker
        yield mock


@pytest.fixture
def full_wheel_data():
    """Stock data that completes a full wheel cycle: put assigned, then called away."""
    dates = pd.date_range('2024-01-05', periods=4, freq='W-FRI')
    return pd.DataFrame({
        # Week 1: Put sold at strike 95, low is 94 -> assigned
        # Week 2: Call sold at strike ~99.75 (95*1.05), high is 101 -> called away
        # Week 3: New put cycle
        # Week 4: Continues
        'Open': [100.0, 95.0, 100.0, 102.0],
        'High': [103.0, 101.0, 105.0, 108.0],
        'Low': [97.0, 94.0, 98.0, 100.0],  # Week 1: 97 > 95 (no assign), Week 2: 94 < 95 (needs adjustment)
        'Close': [101.0, 96.0, 103.0, 106.0],
        'Volume': [1e6, 1.2e6, 1.5e6, 1.1e6],
    }, index=dates)


@pytest.fixture
def sample_put_trade():
    """Sample put trade dictionary."""
    return {
        'date': pd.Timestamp('2024-01-05'),
        'type': 'SELL_PUT',
        'stock_price': 100.0,
        'strike': 95.0,
        'premium': 190.0,  # 95 * 0.02 * 100
        'cash': 50190.0,
        'status': 'pending'
    }


@pytest.fixture
def sample_call_trade():
    """Sample call trade dictionary."""
    return {
        'date': pd.Timestamp('2024-01-12'),
        'type': 'SELL_CALL',
        'stock_price': 95.0,
        'strike': 99.75,
        'premium': 199.5,  # 99.75 * 0.02 * 100
        'cash': 50389.5,
        'status': 'pending',
        'cost_basis': 95.0
    }
