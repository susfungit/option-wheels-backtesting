# WHEEL STRATEGY BACKTESTER - USAGE GUIDE

## 🚀 Quick Start

### Installation

First, install the required packages:

```bash
pip install yfinance pandas numpy matplotlib --break-system-packages
```

### Basic Usage

```python
from wheel_strategy_backtest import run_backtest

# Run backtest on any stock
trades, metrics = run_backtest(
    ticker='TSLA',              # Stock ticker
    start_date='2025-01-01',    # Start date
    end_date='2025-12-31',      # End date
    initial_capital=40000       # Starting capital
)

# Results are automatically printed and plotted!
```

---

## 📊 Examples

### Example 1: Tesla Full Year 2025

```python
trades, metrics = run_backtest(
    ticker='TSLA',
    start_date='2025-01-01',
    end_date='2025-12-31',
    initial_capital=40000
)

print(f"Total Return: {metrics['total_return_pct']:.2f}%")
print(f"Total Premiums: ${metrics['total_premiums']:,.2f}")
print(f"Outperformance vs Buy-Hold: ${metrics['outperformance']:,.2f}")
```

### Example 2: HOOD (Robinhood) Recent Period

```python
trades, metrics = run_backtest(
    ticker='HOOD',
    start_date='2024-01-01',
    end_date='2025-01-10',
    initial_capital=12000
)
```

### Example 3: AFRM (Affirm) 2024

```python
trades, metrics = run_backtest(
    ticker='AFRM',
    start_date='2024-01-01',
    end_date='2024-12-31',
    initial_capital=10000
)
```

### Example 4: Compare Multiple Stocks

```python
stocks = ['TSLA', 'AAPL', 'NVDA', 'HOOD', 'AFRM']

results = {}
for ticker in stocks:
    print(f"\n{'='*70}")
    print(f"Testing {ticker}")
    print('='*70)
    
    trades, metrics = run_backtest(
        ticker=ticker,
        start_date='2024-01-01',
        end_date='2024-12-31',
        initial_capital=30000,
        show_plot=False  # Don't show plots for each stock
    )
    
    results[ticker] = {
        'return': metrics['total_return_pct'],
        'premiums': metrics['total_premiums'],
        'outperformance': metrics['outperformance']
    }

# Print comparison
print("\n" + "="*70)
print("COMPARISON ACROSS STOCKS")
print("="*70)
for ticker, data in results.items():
    print(f"{ticker:6} | Return: {data['return']:7.2f}% | "
          f"Premiums: ${data['premiums']:8,.2f} | "
          f"vs Buy-Hold: ${data['outperformance']:8,.2f}")
```

---

## 🔧 Advanced Usage

### Customize Strategy Parameters

```python
from wheel_strategy_backtest import WheelStrategyBacktest

backtest = WheelStrategyBacktest(
    ticker='TSLA',
    start_date='2025-01-01',
    end_date='2025-12-31',
    initial_capital=50000,
    put_otm_pct=0.07,      # Sell puts 7% OTM (more conservative)
    call_otm_pct=0.08,     # Sell calls 8% OTM (more room for upside)
    premium_pct=0.025      # Estimate 2.5% weekly premium
)

trades_df = backtest.run_backtest()
metrics = backtest.calculate_metrics(trades_df)
backtest.print_results(metrics)
```

### Access Individual Trade Details

```python
trades, metrics = run_backtest('TSLA', '2025-01-01', '2025-12-31')

# Filter for specific trade types
put_trades = trades[trades['type'] == 'SELL_PUT']
call_trades = trades[trades['type'] == 'SELL_CALL']

# Find assignments
assignments = trades[trades['status'] == 'ASSIGNED']
print(f"\nGot assigned {len(assignments)} times:")
for idx, trade in assignments.iterrows():
    print(f"  {trade['date'].strftime('%Y-%m-%d')}: "
          f"Assigned at ${trade['strike']:.2f}, "
          f"Stock at ${trade['assignment_price']:.2f}")

# Find called away
called_away = trades[trades['status'] == 'CALLED_AWAY']
print(f"\nCalled away {len(called_away)} times:")
for idx, trade in called_away.iterrows():
    print(f"  {trade['date'].strftime('%Y-%m-%d')}: "
          f"Called at ${trade['strike']:.2f}, "
          f"Stock gain: ${trade['stock_gain']:.2f}")

# Calculate statistics
print(f"\nAverage premium per put: ${put_trades['premium'].mean():.2f}")
print(f"Average premium per call: ${call_trades['premium'].mean():.2f}")
print(f"Max premium collected: ${trades['premium'].max():.2f}")
print(f"Min premium collected: ${trades['premium'].min():.2f}")
```

### Export Results

```python
# Exports are automatic, but you can customize the filename
trades, metrics = run_backtest(
    ticker='TSLA',
    start_date='2025-01-01',
    end_date='2025-12-31',
    export_csv=True  # Creates CSV file automatically
)

# Or export manually with custom name
backtest = WheelStrategyBacktest('TSLA', '2025-01-01', '2025-12-31')
trades_df = backtest.run_backtest()
backtest.export_trades(trades_df, filename='my_custom_backtest.csv')
```

---

## 📈 Understanding the Output

### Printed Results

The script prints comprehensive results including:

1. **Performance Summary**
   - Initial capital, final value, total profit
   - Total return % and annualized return %

2. **Profit Breakdown**
   - Total premiums collected
   - Realized stock gains
   - Unrealized gains (if currently holding stock)

3. **Buy & Hold Comparison**
   - What you would have made just buying and holding
   - How much better (or worse) the Wheel performed

4. **Trade Statistics**
   - Number of puts/calls sold
   - Times assigned and called away
   - Average weekly premium

5. **Stock Performance**
   - Starting and ending stock price
   - Overall stock return

### Visualizations

The script creates 4 charts:

1. **Stock Price & Option Strikes**
   - Stock price over time
   - Green triangles: Put strikes
   - Red triangles: Call strikes
   - Orange circles: Assignments
   - Purple squares: Called away

2. **Cumulative Premium Income**
   - Total premiums collected over time
   - Shows steady income generation

3. **Portfolio Value**
   - Wheel strategy value (blue)
   - Buy-and-hold comparison (gray dashed)
   - Initial capital line (red)

4. **Weekly Premium Distribution**
   - Histogram of weekly premiums
   - Shows variability in income

---

## 🎯 Metrics Dictionary

When you run `trades, metrics = run_backtest(...)`, the `metrics` dictionary contains:

```python
metrics = {
    # Final values
    'initial_capital': 50000,
    'final_cash': 45000,
    'stock_value': 30000,  # If currently holding
    'total_value': 75000,
    'total_profit': 25000,
    'total_return_pct': 50.0,
    'annualized_return_pct': 45.2,
    
    # Component returns
    'total_premiums': 18000,
    'total_stock_gains': 7000,
    'unrealized_gain': 2000,  # If holding stock
    
    # Buy and hold comparison
    'buy_hold_value': 60000,
    'buy_hold_profit': 10000,
    'buy_hold_return_pct': 20.0,
    'outperformance': 15000,  # Wheel - Buy&Hold
    
    # Trade statistics
    'total_weeks': 52,
    'put_trades': 35,
    'call_trades': 17,
    'times_assigned': 2,
    'times_called_away': 2,
    'avg_weekly_premium': 346.15,
    
    # Stock metrics
    'starting_price': 380.00,
    'ending_price': 450.00,
    'stock_return_pct': 18.42,
    'owns_stock_at_end': False,
    
    # Time
    'days_held': 365,
    'years_held': 1.0
}
```

---

## 💡 Tips for Effective Backtesting

### 1. Test Multiple Time Periods

```python
periods = [
    ('2023-01-01', '2023-12-31'),
    ('2024-01-01', '2024-12-31'),
    ('2025-01-01', '2025-12-31'),
]

for start, end in periods:
    print(f"\n{'='*70}")
    print(f"Testing period: {start} to {end}")
    trades, metrics = run_backtest('TSLA', start, end, show_plot=False)
    print(f"Return: {metrics['total_return_pct']:.2f}%")
```

### 2. Test During Bear Markets

```python
# COVID crash period
trades, metrics = run_backtest(
    ticker='SPY',
    start_date='2020-01-01',
    end_date='2020-06-30'
)
```

### 3. Test High Volatility vs Low Volatility Periods

```python
# High volatility (2020 COVID)
high_vol = run_backtest('TSLA', '2020-01-01', '2020-12-31', show_plot=False)

# Low volatility (2017 steady market)
low_vol = run_backtest('TSLA', '2017-01-01', '2017-12-31', show_plot=False)

print(f"High vol premiums: ${high_vol[1]['total_premiums']:,.2f}")
print(f"Low vol premiums: ${low_vol[1]['total_premiums']:,.2f}")
```

### 4. Compare Across Sectors

```python
tech = ['TSLA', 'AAPL', 'NVDA', 'MSFT']
finance = ['JPM', 'BAC', 'GS', 'MS']
retail = ['AMZN', 'WMT', 'TGT', 'COST']

for sector, stocks in [('Tech', tech), ('Finance', finance), ('Retail', retail)]:
    print(f"\n{sector} Sector:")
    for ticker in stocks:
        try:
            _, m = run_backtest(ticker, '2024-01-01', '2024-12-31', 
                              show_plot=False, export_csv=False)
            print(f"  {ticker:6} - {m['total_return_pct']:6.2f}%")
        except:
            print(f"  {ticker:6} - Error")
```

---

## ⚠️ Important Limitations

### 1. Premium Estimation

The script uses a **simplified premium model** (2% of strike per week). Real premiums vary based on:
- Implied volatility (IV)
- Time to expiration
- Distance from current price
- Market conditions

**Real premiums could be higher or lower!**

### 2. Execution Assumptions

The backtest assumes:
- ✅ You can sell at the strike price you want
- ✅ Options are liquid (tight bid-ask spreads)
- ✅ No slippage
- ✅ Instant assignment/execution

**In reality:** You may get worse fills, especially on illiquid stocks.

### 3. Weekly Frequency

The backtest uses **weekly** data (every Friday). It assumes:
- You trade every Friday
- Assignment happens at week-end only

**In reality:** You could trade multiple times per week and get assigned mid-week.

### 4. No Transaction Costs

The backtest does NOT include:
- ❌ Commission fees
- ❌ Exchange fees
- ❌ Regulatory fees
- ❌ Assignment fees

**Add ~$1-2 per contract in costs.**

### 5. Tax Implications

The backtest does NOT account for:
- Short-term capital gains taxes
- Wash sale rules
- State taxes

**Your actual after-tax returns will be lower!**

---

## 🔍 Interpreting Results

### When the Wheel Works Best

The strategy tends to outperform when:
- ✅ Stock is sideways or slightly uptrending
- ✅ Volatility is elevated (higher premiums)
- ✅ Stock has support levels that hold
- ✅ You get assigned near local lows

### When the Wheel Struggles

The strategy underperforms when:
- ❌ Stock crashes hard and stays down
- ❌ Stock moons (you miss big rallies)
- ❌ Volatility collapses (low premiums)
- ❌ Stock gaps through your strikes

### Red Flags in Results

Be concerned if you see:
- 🚩 Large negative stock gains
- 🚩 Premiums < 1% weekly
- 🚩 Multiple assignments with no calls away
- 🚩 Outperformance driven by ONE lucky assignment

---

## 📝 Example Analysis Workflow

```python
# 1. Run backtest
trades, metrics = run_backtest('TSLA', '2025-01-01', '2025-12-31', 40000)

# 2. Check if profitable
if metrics['total_return_pct'] > 0:
    print("✅ Strategy was profitable")
else:
    print("❌ Strategy lost money")

# 3. Compare to buy-and-hold
if metrics['outperformance'] > 0:
    print(f"✅ Beat buy-hold by ${metrics['outperformance']:,.2f}")
else:
    print(f"❌ Underperformed buy-hold by ${abs(metrics['outperformance']):,.2f}")

# 4. Check premium consistency
avg_premium = metrics['avg_weekly_premium']
if avg_premium > metrics['initial_capital'] * 0.01:  # >1% weekly
    print(f"✅ Strong premiums: ${avg_premium:.2f}/week")
else:
    print(f"⚠️ Weak premiums: ${avg_premium:.2f}/week")

# 5. Analyze assignments
if metrics['times_assigned'] > 0:
    avg_stock_gain = metrics['total_stock_gains'] / metrics['times_assigned']
    print(f"Average gain per assignment cycle: ${avg_stock_gain:,.2f}")

# 6. Check final state
if metrics['owns_stock_at_end']:
    if metrics['unrealized_gain'] < 0:
        print(f"⚠️ Currently underwater by ${abs(metrics['unrealized_gain']):,.2f}")
    else:
        print(f"✅ Currently profitable by ${metrics['unrealized_gain']:,.2f}")
```

---

## 🎓 Learning from the Backtest

### Questions to Ask:

1. **How many times did I get assigned?**
   - More assignments = more volatility
   - Check if stock recovered after assignments

2. **What was the largest drawdown?**
   - Look at the portfolio value chart
   - Could you stomach that loss?

3. **How long was I stuck in positions?**
   - Count weeks between assignment and called away
   - Is 3-6 months acceptable?

4. **Did I beat buy-and-hold?**
   - If no, why run the strategy?
   - Is the extra work worth small outperformance?

5. **What if I started 3 months later/earlier?**
   - Test different start dates
   - Results can vary dramatically!

---

## 🚀 Next Steps

1. **Run on your target stocks**
2. **Test multiple time periods**
3. **Compare to buy-and-hold**
4. **Analyze assignment patterns**
5. **Consider transaction costs**
6. **Factor in your tax situation**
7. **Decide if risk/reward is acceptable**

---

## 📞 Support

For questions or issues:
- Review the printed output carefully
- Check the generated CSV file for trade details
- Examine the charts for visual insights
- Test on familiar stocks first (SPY, AAPL, TSLA)

Happy backtesting! 🎯
