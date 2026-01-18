# 🎯 WHEEL STRATEGY BACKTESTER

A comprehensive Python tool to backtest the Wheel Options Trading Strategy on any stock.

## 📦 What's Included

- `wheel_strategy_backtest.py` - Main backtesting engine
- `main.py` - Command-line interface
- `quick_start.py` - Ready-to-run examples (TSLA, HOOD, AFRM)
- `tests/` - Unit tests for the backtester
- `USAGE_GUIDE.md` - Comprehensive documentation
- `pyproject.toml` - Project configuration and dependencies

## 🚀 Installation

```bash
# Install dependencies using uv
uv sync

# Or if you prefer pip
pip install yfinance pandas numpy matplotlib
```

## ⚡ Quick Start (3 lines!)

```python
from wheel_strategy_backtest import run_backtest

trades, metrics = run_backtest('TSLA', '2025-01-01', '2025-12-31')
# That's it! Results are printed and plotted automatically.
```

## 📊 What It Does

The Wheel Strategy is an options income strategy:

1. **Sell Cash-Secured Puts** (5% below stock price)
   - Collect premium
   - If stock drops → Get assigned, own stock

2. **Sell Covered Calls** (5% above current price)
   - Collect premium while holding stock
   - If stock rises → Get called away, sell stock

3. **Repeat** (hence "The Wheel")

This backtester simulates this strategy week-by-week on historical data.

## 🖥️ Command Line Interface

```bash
# Run backtest on any stock
python main.py TSLA 2025-01-01 2025-12-31

# With custom starting capital
python main.py AAPL 2024-01-01 2024-12-31 --capital 50000

# Skip plots and CSV export
python main.py NVDA 2024-01-01 2024-12-31 --no-plot --no-csv

# Run quick start examples
python main.py --quick-start
```

## 🎬 Run Examples

```bash
# Run the pre-built examples
python main.py --quick-start

# Or run quick_start.py directly
python quick_start.py
```

This will test:
- Tesla (TSLA) for 2025
- Robinhood (HOOD) for 2024-2025
- Affirm (AFRM) for 2024

And show you which performed best!

## 💡 Basic Usage

### Test Any Stock

```python
from wheel_strategy_backtest import run_backtest

# Apple
trades, metrics = run_backtest('AAPL', '2024-01-01', '2024-12-31')

# NVIDIA
trades, metrics = run_backtest('NVDA', '2024-01-01', '2024-12-31')

# S&P 500 ETF
trades, metrics = run_backtest('SPY', '2024-01-01', '2024-12-31')
```

### Custom Parameters

```python
from wheel_strategy_backtest import WheelStrategyBacktest

backtest = WheelStrategyBacktest(
    ticker='TSLA',
    start_date='2025-01-01',
    end_date='2025-12-31',
    initial_capital=50000,
    put_otm_pct=0.07,      # 7% OTM puts (more conservative)
    call_otm_pct=0.08,     # 8% OTM calls (more upside room)
    premium_pct=0.025      # 2.5% weekly premium estimate
)

trades = backtest.run_backtest()
metrics = backtest.calculate_metrics(trades)
backtest.print_results(metrics)
```

## 📈 What You Get

### 1. Comprehensive Results Printed to Console

```
╔═══════════════════════════════════════════════════════════╗
║                    BACKTEST RESULTS                       ║
╚═══════════════════════════════════════════════════════════╝

📊 PERFORMANCE SUMMARY
────────────────────────────────────────────────────────────
Initial Capital:        $    40,000.00
Final Value:            $    99,630.00
Total Profit:           $    59,630.00
Total Return:                  149.08%
Annualized Return:             149.08%

💰 PROFIT BREAKDOWN
────────────────────────────────────────────────────────────
Total Premiums:         $    42,130.00
Stock Gains:            $    17,500.00

📈 BUY & HOLD COMPARISON
────────────────────────────────────────────────────────────
Buy & Hold Return:              31.20%
Wheel Outperformance:   $    47,240.00
✅ Wheel Strategy BEAT buy-and-hold!
```

### 2. Visual Charts

Four charts showing:
- Stock price with all your option strikes
- Cumulative premium income
- Portfolio value vs buy-and-hold
- Weekly premium distribution

### 3. Trade History CSV

Every trade exported with:
- Date, type (put/call), strike price
- Premium collected
- Assignment status
- Stock gains/losses

### 4. Metrics Dictionary

```python
trades, metrics = run_backtest('TSLA', '2025-01-01', '2025-12-31')

print(f"Total Return: {metrics['total_return_pct']:.2f}%")
print(f"Total Premiums: ${metrics['total_premiums']:,.2f}")
print(f"Times Assigned: {metrics['times_assigned']}")
print(f"Beat Buy-Hold by: ${metrics['outperformance']:,.2f}")
```

## 🔍 Example Output

```python
>>> trades, metrics = run_backtest('TSLA', '2025-01-01', '2025-12-31', 40000)

Week   1 | PUT EXPIRED  at $360.00 | Premium: $ 750.00 | Stock: $385.00
Week   2 | PUT EXPIRED  at $365.00 | Premium: $ 800.00 | Stock: $390.00
...
Week  16 | PUT ASSIGNED at $228.00 | Premium: $1200.00 | Stock: $214.00
Week  17 | CALL EXPIRED at $225.00 | Premium: $ 550.00 | Unrlzd: $-700.00
...
Week  29 | CALLED AWAY  at $275.00 | Premium: $ 700.00 | Gain: $4700.00
...

Final Results:
  Total Return: 149.08%
  Total Premiums: $42,130
  Stock Gains: $17,500
  Beat Buy-Hold by: $47,240
```

## 📚 Documentation

See `USAGE_GUIDE.md` for:
- Detailed examples
- Advanced customization
- Multiple stock comparison
- Interpreting results
- Important limitations
- Best practices

## ⚠️ Important Notes

### This is a BACKTEST, not a guarantee!

**The script makes simplified assumptions:**

1. **Premium Estimation**: Uses 2% of strike per week
   - Real premiums vary with IV, time, distance from strike
   - Could be higher OR lower in reality

2. **Perfect Execution**: Assumes you can sell at your desired strike
   - Real trading has slippage and bid-ask spreads
   - Illiquid options can have poor fills

3. **No Transaction Costs**: Doesn't include commissions/fees
   - Add ~$1-2 per contract in real costs

4. **No Taxes**: Doesn't account for tax implications
   - All premiums are taxed as ordinary income
   - Stock gains are taxed based on holding period

5. **Weekly Frequency**: Only trades Fridays
   - Real trading can be more frequent
   - Could miss mid-week opportunities

**Use this to understand the CONCEPT and PATTERNS, not as a precise profit calculator!**

## 🎯 Best Practices

1. **Test multiple time periods** - One year isn't enough
2. **Compare across stocks** - See which work best
3. **Test bear markets** - How does it handle crashes?
4. **Check assignment patterns** - How often do you get stuck?
5. **Factor in costs** - Subtract commissions from results
6. **Consider taxes** - Your after-tax return will be lower

## 🧪 Suggested Tests

```python
# Test during COVID crash
run_backtest('SPY', '2020-02-01', '2020-06-30')

# Test steady bull market
run_backtest('AAPL', '2017-01-01', '2017-12-31')

# Test sideways market
run_backtest('SPY', '2015-01-01', '2015-12-31')

# Test your target stock for last 2 years
run_backtest('YOUR_STOCK', '2023-01-01', '2024-12-31')
```

## 📊 Compare Stocks

```python
stocks = ['TSLA', 'AAPL', 'NVDA', 'HOOD', 'SPY']

for ticker in stocks:
    _, m = run_backtest(ticker, '2024-01-01', '2024-12-31', 
                       show_plot=False, export_csv=False)
    print(f"{ticker}: {m['total_return_pct']:.2f}% | "
          f"Premiums: ${m['total_premiums']:,.0f}")
```

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run a specific test file
uv run pytest tests/test_premium.py
```

## 🤝 Contributing

Have improvements? Found bugs? Suggestions welcome!

## 📄 License

Free to use for personal backtesting and education.

## ⚡ Quick Reference

```python
# Basic usage
run_backtest('TICKER', 'START_DATE', 'END_DATE')

# With capital
run_backtest('TICKER', 'START_DATE', 'END_DATE', initial_capital=50000)

# No plots/exports
run_backtest('TICKER', 'START_DATE', 'END_DATE', 
            show_plot=False, export_csv=False)

# Access metrics
trades, metrics = run_backtest('TICKER', 'START', 'END')
print(metrics['total_return_pct'])
print(metrics['total_premiums'])
print(metrics['outperformance'])
```

## 🎓 Learn More

The Wheel Strategy is popular on:
- r/thetagang (Reddit)
- r/options (Reddit)
- YouTube: Search "wheel strategy"
- Option trading courses

---

**Happy Backtesting! 📈**

Remember: Past performance doesn't guarantee future results. Use this tool to learn and understand the strategy, not as financial advice.
