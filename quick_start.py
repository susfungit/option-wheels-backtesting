"""
QUICK START EXAMPLES
====================
Simple examples to get you started with the Wheel Strategy Backtester
"""

from wheel_strategy_backtest import run_backtest

print("""
╔═══════════════════════════════════════════════════════════════════╗
║           WHEEL STRATEGY BACKTESTER - QUICK START                 ║
╚═══════════════════════════════════════════════════════════════════╝
""")

# EXAMPLE 1: Tesla 2025 (the example from our conversation)
print("\n" + "="*70)
print("EXAMPLE 1: Tesla (TSLA) - Full Year 2025")
print("="*70)
print("Testing the exact scenario we discussed...")

trades_tsla, metrics_tsla = run_backtest(
    ticker='TSLA',
    start_date='2025-01-01',
    end_date='2025-12-31',
    initial_capital=40000,
    show_plot=True,
    export_csv=True
)

print(f"\nKey Takeaway:")
print(f"  Wheel Strategy: {metrics_tsla['total_return_pct']:.2f}% return")
print(f"  Buy & Hold: {metrics_tsla['buy_hold_return_pct']:.2f}% return")
print(f"  Outperformance: ${metrics_tsla['outperformance']:,.2f}")

# EXAMPLE 2: Your choice - HOOD
print("\n\n" + "="*70)
print("EXAMPLE 2: Robinhood (HOOD) - 2024-2025")
print("="*70)
print("Testing HOOD from our earlier analysis...")

trades_hood, metrics_hood = run_backtest(
    ticker='HOOD',
    start_date='2024-01-01',
    end_date='2025-01-10',
    initial_capital=12000,
    show_plot=True,
    export_csv=True
)

# EXAMPLE 3: Your choice - AFRM
print("\n\n" + "="*70)
print("EXAMPLE 3: Affirm (AFRM) - 2024")
print("="*70)
print("Testing AFRM...")

trades_afrm, metrics_afrm = run_backtest(
    ticker='AFRM',
    start_date='2024-01-01',
    end_date='2024-12-31',
    initial_capital=10000,
    show_plot=True,
    export_csv=True
)

# COMPARISON
print("\n\n" + "="*70)
print("COMPARISON: Which stock worked best for the Wheel?")
print("="*70)

results = [
    ('TSLA', metrics_tsla),
    ('HOOD', metrics_hood),
    ('AFRM', metrics_afrm)
]

print(f"\n{'Stock':<6} | {'Return':<8} | {'Premiums':<12} | {'vs Buy-Hold':<12} | {'Winner?'}")
print("-" * 70)

for ticker, m in results:
    winner = "✅ YES" if m['outperformance'] > 0 else "❌ NO"
    print(f"{ticker:<6} | {m['total_return_pct']:>6.2f}% | "
          f"${m['total_premiums']:>10,.0f} | "
          f"${m['outperformance']:>10,.0f} | {winner}")

print("\n" + "="*70)
print("YOUR TURN!")
print("="*70)
print("""
Now try your own stock! Here's the template:

    from wheel_strategy_backtest import run_backtest
    
    trades, metrics = run_backtest(
        ticker='YOUR_TICKER',      # Try: SPY, QQQ, NVDA, AAPL, etc.
        start_date='2024-01-01',
        end_date='2024-12-31',
        initial_capital=50000
    )
    
    print(f"Return: {metrics['total_return_pct']:.2f}%")
    print(f"Premiums: ${metrics['total_premiums']:,.2f}")
    print(f"Beat Buy-Hold: ${metrics['outperformance']:,.2f}")

Popular stocks to test:
  - Tech: NVDA, AAPL, MSFT, GOOGL, META, AMD
  - EV: TSLA, RIVN, LCID, NIO
  - Fintech: HOOD, COIN, SOFI, AFRM, SQ
  - ETFs: SPY, QQQ, IWM
  - Meme: GME, AMC (be careful!)
  
Have fun! 🚀
""")
