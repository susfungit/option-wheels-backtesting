#!/usr/bin/env python3
"""
Wheel Strategy Backtester - Command Line Interface
"""

import argparse
import runpy
from wheel_strategy_backtest import run_backtest


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
        # Execute quick_start.py as a script
        import runpy
        runpy.run_path('quick_start.py', run_name='__main__')
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
