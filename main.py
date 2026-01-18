#!/usr/bin/env python3
"""
Wheel Strategy Backtester - Command Line Interface
"""

import argparse
import os
import re
import runpy
from datetime import datetime
from wheel_strategy_backtest import run_backtest

# Constants for validation
MIN_CAPITAL = 1000
MAX_CAPITAL = 100_000_000
TICKER_PATTERN = re.compile(r'^[A-Za-z]{1,5}$')


def validate_inputs(ticker: str, start_date: str, end_date: str, capital: float) -> None:
    """
    Validate user inputs for security and correctness.

    Raises:
        ValueError: If any input is invalid
    """
    # Validate ticker format (1-5 alphabetic characters)
    if not TICKER_PATTERN.match(ticker):
        raise ValueError(
            f"Invalid ticker '{ticker}'. Must be 1-5 alphabetic characters (e.g., TSLA, AAPL)"
        )

    # Validate capital range
    if not (MIN_CAPITAL <= capital <= MAX_CAPITAL):
        raise ValueError(
            f"Capital must be between ${MIN_CAPITAL:,} and ${MAX_CAPITAL:,}. Got: ${capital:,.2f}"
        )

    # Parse and validate dates
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(
            f"Invalid start date '{start_date}'. Must be in YYYY-MM-DD format"
        )

    try:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(
            f"Invalid end date '{end_date}'. Must be in YYYY-MM-DD format"
        )

    # Validate date order
    if start_dt >= end_dt:
        raise ValueError(
            f"Start date ({start_date}) must be before end date ({end_date})"
        )


def main():
    parser = argparse.ArgumentParser(
        description='Backtest the Wheel Options Trading Strategy on any stock',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest on TSLA for 2025
  python main.py TSLA 2025-01-01 2025-12-31

  # Run with custom capital
  python main.py AAPL 2024-01-01 2024-12-31 --capital 50000

  # Run without plots or CSV export
  python main.py NVDA 2024-01-01 2024-12-31 --no-plot --no-csv

  # Run quick start examples
  python main.py --quick-start
        """
    )
    
    parser.add_argument(
        'ticker',
        nargs='?',
        help='Stock ticker symbol (e.g., TSLA, AAPL, NVDA)'
    )
    parser.add_argument(
        'start_date',
        nargs='?',
        help='Start date in YYYY-MM-DD format'
    )
    parser.add_argument(
        'end_date',
        nargs='?',
        help='End date in YYYY-MM-DD format'
    )
    parser.add_argument(
        '--capital', '-c',
        type=float,
        default=50000,
        help='Initial capital (default: 50000)'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Skip displaying plots'
    )
    parser.add_argument(
        '--no-csv',
        action='store_true',
        help='Skip exporting CSV file'
    )
    parser.add_argument(
        '--quick-start',
        action='store_true',
        help='Run quick start examples (TSLA, HOOD, AFRM)'
    )
    
    args = parser.parse_args()
    
    # Run quick start examples
    if args.quick_start:
        print("Running quick start examples...")
        print("=" * 70)
        # Execute quick_start.py as a script using absolute path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        quick_start_path = os.path.join(script_dir, 'quick_start.py')
        runpy.run_path(quick_start_path, run_name='__main__')
        return
    
    # Validate required arguments
    if not args.ticker or not args.start_date or not args.end_date:
        parser.print_help()
        print("\n" + "=" * 70)
        print("ERROR: Missing required arguments")
        print("=" * 70)
        print("\nEither provide all three arguments (ticker, start_date, end_date)")
        print("or use --quick-start to run examples.\n")
        return
    
    # Validate inputs
    try:
        validate_inputs(args.ticker, args.start_date, args.end_date, args.capital)
    except ValueError as e:
        print(f"\nERROR: {e}")
        return 1

    # Run backtest
    print(f"\n{'='*70}")
    print(f"Running backtest for {args.ticker}")
    print(f"Period: {args.start_date} to {args.end_date}")
    print(f"Initial Capital: ${args.capital:,.2f}")
    print(f"{'='*70}\n")

    try:
        trades, metrics = run_backtest(
            ticker=args.ticker,
            start_date=args.start_date,
            end_date=args.end_date,
            initial_capital=args.capital,
            show_plot=not args.no_plot,
            export_csv=not args.no_csv
        )
        
        print(f"\n{'='*70}")
        print("BACKTEST COMPLETE")
        print(f"{'='*70}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Total Premiums: ${metrics['total_premiums']:,.2f}")
        print(f"Outperformance vs Buy-Hold: ${metrics['outperformance']:,.2f}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nPlease check:")
        print("  - Ticker symbol is valid")
        print("  - Date format is YYYY-MM-DD")
        print("  - Dates are valid and in the past")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main() or 0)
