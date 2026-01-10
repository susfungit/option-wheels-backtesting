"""
WHEEL STRATEGY BACKTESTER
==========================
Backtests the Wheel Options Trading Strategy on any stock.

The Wheel Strategy:
1. Sell cash-secured puts (5% OTM) weekly
2. If assigned, own the stock
3. Sell covered calls (5% OTM) weekly while holding
4. If called away, return to step 1

Author: Claude
Date: January 2026
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')


class WheelStrategyBacktest:
    """
    Backtests the Wheel Options Strategy on historical stock data.
    """
    
    def __init__(self, ticker: str, start_date: str, end_date: str, 
                 initial_capital: float = 50000,
                 put_otm_pct: float = 0.05,
                 call_otm_pct: float = 0.05,
                 premium_pct: float = 0.02):
        """
        Initialize the backtest.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'TSLA', 'AAPL')
        start_date : str
            Start date in 'YYYY-MM-DD' format
        end_date : str
            End date in 'YYYY-MM-DD' format
        initial_capital : float
            Starting capital in dollars
        put_otm_pct : float
            How far out-of-the-money to sell puts (default 5%)
        call_otm_pct : float
            How far out-of-the-money to sell calls (default 5%)
        premium_pct : float
            Estimated weekly premium as % of strike price (default 2%)
        """
        self.ticker = ticker.upper()
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.initial_capital = initial_capital
        self.put_otm_pct = put_otm_pct
        self.call_otm_pct = call_otm_pct
        self.premium_pct = premium_pct
        
        # State variables
        self.owns_stock = False
        self.stock_purchase_price = 0
        self.shares_owned = 0
        self.cash = initial_capital
        self.total_premiums = 0
        self.total_stock_gains = 0
        self.trades = []
        
        # Download data
        print(f"\n{'='*70}")
        print(f"WHEEL STRATEGY BACKTEST: {self.ticker}")
        print(f"{'='*70}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${initial_capital:,.2f}")
        print(f"\nDownloading historical data...")
        
        self.data = self._download_data()
        
    def _download_data(self) -> pd.DataFrame:
        """Download historical stock data from Yahoo Finance."""
        try:
            stock = yf.Ticker(self.ticker)
            df = stock.history(start=self.start_date, end=self.end_date)
            
            if df.empty:
                raise ValueError(f"No data found for {self.ticker}")
            
            # Use weekly data (every Friday or last trading day of week)
            df = df.resample('W-FRI').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            print(f"✓ Downloaded {len(df)} weeks of data")
            print(f"  Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
            print(f"  Starting price: ${df['Close'].iloc[0]:.2f}")
            print(f"  Ending price: ${df['Close'].iloc[-1]:.2f}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error downloading data: {e}")
    
    def _calculate_premium(self, strike_price: float, stock_price: float) -> float:
        """
        Estimate option premium based on strike price and volatility.
        
        Simplified model: Premium ≈ 2% of strike price per week
        In reality, this varies with IV, but provides reasonable estimate.
        """
        # Base premium
        base_premium = strike_price * self.premium_pct
        
        # Adjust for how far OTM (further OTM = lower premium)
        otm_distance = abs(strike_price - stock_price) / stock_price
        adjustment = max(0.3, 1 - (otm_distance * 5))  # Reduces premium for far OTM
        
        return base_premium * adjustment * 100  # x100 for per contract
    
    def _sell_put(self, date: pd.Timestamp, stock_price: float) -> Dict:
        """
        Simulate selling a cash-secured put option.
        
        Returns trade details dictionary.
        """
        # Calculate strike price (5% below current price)
        strike_price = stock_price * (1 - self.put_otm_pct)
        strike_price = round(strike_price, 2)
        
        # Calculate premium
        premium = self._calculate_premium(strike_price, stock_price)
        
        # Collect premium
        self.cash += premium
        self.total_premiums += premium
        
        trade = {
            'date': date,
            'type': 'SELL_PUT',
            'stock_price': stock_price,
            'strike': strike_price,
            'premium': premium,
            'cash': self.cash,
            'status': 'pending'
        }
        
        return trade
    
    def _check_put_assignment(self, trade: Dict, low_price: float, 
                              close_price: float) -> Tuple[bool, Dict]:
        """
        Check if put was assigned (stock dropped below strike).
        
        Returns (assigned, updated_trade)
        """
        if low_price <= trade['strike']:
            # Assigned! Buy 100 shares at strike price
            shares = 100
            cost = trade['strike'] * shares
            
            if self.cash >= cost:
                self.owns_stock = True
                self.shares_owned = shares
                self.stock_purchase_price = trade['strike']
                self.cash -= cost
                
                trade['status'] = 'ASSIGNED'
                trade['assignment_price'] = close_price
                trade['shares_acquired'] = shares
                trade['capital_deployed'] = cost
                
                return True, trade
        
        # Not assigned - put expired worthless (good!)
        trade['status'] = 'EXPIRED_WORTHLESS'
        return False, trade
    
    def _sell_call(self, date: pd.Timestamp, stock_price: float) -> Dict:
        """
        Simulate selling a covered call option.
        
        Returns trade details dictionary.
        """
        # Calculate strike price (5% above current price)
        strike_price = stock_price * (1 + self.call_otm_pct)
        strike_price = round(strike_price, 2)
        
        # Calculate premium
        premium = self._calculate_premium(strike_price, stock_price)
        
        # Collect premium
        self.cash += premium
        self.total_premiums += premium
        
        trade = {
            'date': date,
            'type': 'SELL_CALL',
            'stock_price': stock_price,
            'strike': strike_price,
            'premium': premium,
            'cash': self.cash,
            'status': 'pending',
            'cost_basis': self.stock_purchase_price
        }
        
        return trade
    
    def _check_call_assignment(self, trade: Dict, high_price: float,
                               close_price: float) -> Tuple[bool, Dict]:
        """
        Check if call was assigned (stock rose above strike).
        
        Returns (assigned, updated_trade)
        """
        if high_price >= trade['strike']:
            # Called away! Sell 100 shares at strike price
            proceeds = trade['strike'] * self.shares_owned
            stock_gain = (trade['strike'] - self.stock_purchase_price) * self.shares_owned
            
            self.cash += proceeds
            self.total_stock_gains += stock_gain
            
            self.owns_stock = False
            self.shares_owned = 0
            self.stock_purchase_price = 0
            
            trade['status'] = 'CALLED_AWAY'
            trade['sale_price'] = trade['strike']
            trade['stock_gain'] = stock_gain
            trade['total_proceeds'] = proceeds
            
            return True, trade
        
        # Not called away - call expired worthless (good!)
        trade['status'] = 'EXPIRED_WORTHLESS'
        return False, trade
    
    def run_backtest(self) -> pd.DataFrame:
        """
        Execute the complete backtest.
        
        Returns DataFrame of all trades.
        """
        print(f"\n{'='*70}")
        print("RUNNING BACKTEST")
        print(f"{'='*70}\n")
        
        week_num = 0
        
        for idx in range(len(self.data)):
            week_num += 1
            date = self.data.index[idx]
            open_price = self.data['Open'].iloc[idx]
            high_price = self.data['High'].iloc[idx]
            low_price = self.data['Low'].iloc[idx]
            close_price = self.data['Close'].iloc[idx]
            
            # Determine action based on current state
            if not self.owns_stock:
                # Phase 1: Sell cash-secured puts
                trade = self._sell_put(date, open_price)
                
                # Check if assigned at week end
                assigned, trade = self._check_put_assignment(trade, low_price, close_price)
                
                if assigned:
                    print(f"Week {week_num:3d} | PUT ASSIGNED at ${trade['strike']:.2f} "
                          f"| Premium: ${trade['premium']:6.2f} | Stock: ${close_price:.2f}")
                else:
                    print(f"Week {week_num:3d} | PUT EXPIRED  at ${trade['strike']:.2f} "
                          f"| Premium: ${trade['premium']:6.2f} | Stock: ${close_price:.2f}")
            
            else:
                # Phase 2: Sell covered calls
                trade = self._sell_call(date, open_price)
                
                # Check if called away at week end
                called_away, trade = self._check_call_assignment(trade, high_price, close_price)
                
                if called_away:
                    print(f"Week {week_num:3d} | CALLED AWAY at ${trade['strike']:.2f} "
                          f"| Premium: ${trade['premium']:6.2f} | Gain: ${trade['stock_gain']:7.2f}")
                else:
                    unrealized = (close_price - self.stock_purchase_price) * self.shares_owned
                    print(f"Week {week_num:3d} | CALL EXPIRED at ${trade['strike']:.2f} "
                          f"| Premium: ${trade['premium']:6.2f} | Unrlzd: ${unrealized:7.2f}")
            
            self.trades.append(trade)
        
        return pd.DataFrame(self.trades)
    
    def calculate_metrics(self, trades_df: pd.DataFrame) -> Dict:
        """Calculate comprehensive performance metrics."""
        
        # Current position value
        if self.owns_stock:
            current_stock_value = self.data['Close'].iloc[-1] * self.shares_owned
            unrealized_gain = (self.data['Close'].iloc[-1] - self.stock_purchase_price) * self.shares_owned
        else:
            current_stock_value = 0
            unrealized_gain = 0
        
        # Total account value
        total_value = self.cash + current_stock_value
        total_profit = total_value - self.initial_capital
        total_return_pct = (total_profit / self.initial_capital) * 100
        
        # Buy and hold comparison
        initial_shares = self.initial_capital / self.data['Close'].iloc[0]
        buy_hold_value = initial_shares * self.data['Close'].iloc[-1]
        buy_hold_profit = buy_hold_value - self.initial_capital
        buy_hold_return_pct = (buy_hold_profit / self.initial_capital) * 100
        
        # Trade statistics
        total_trades = len(trades_df)
        put_trades = len(trades_df[trades_df['type'] == 'SELL_PUT'])
        call_trades = len(trades_df[trades_df['type'] == 'SELL_CALL'])
        assignments = len(trades_df[trades_df['status'] == 'ASSIGNED'])
        called_away = len(trades_df[trades_df['status'] == 'CALLED_AWAY'])
        
        # Time metrics
        days_held = (self.end_date - self.start_date).days
        years_held = days_held / 365.25
        annualized_return = ((total_value / self.initial_capital) ** (1/years_held) - 1) * 100 if years_held > 0 else 0
        
        metrics = {
            # Final values
            'initial_capital': self.initial_capital,
            'final_cash': self.cash,
            'stock_value': current_stock_value,
            'total_value': total_value,
            'total_profit': total_profit,
            'total_return_pct': total_return_pct,
            'annualized_return_pct': annualized_return,
            
            # Component returns
            'total_premiums': self.total_premiums,
            'total_stock_gains': self.total_stock_gains,
            'unrealized_gain': unrealized_gain,
            
            # Buy and hold comparison
            'buy_hold_value': buy_hold_value,
            'buy_hold_profit': buy_hold_profit,
            'buy_hold_return_pct': buy_hold_return_pct,
            'outperformance': total_profit - buy_hold_profit,
            
            # Trade statistics
            'total_weeks': total_trades,
            'put_trades': put_trades,
            'call_trades': call_trades,
            'times_assigned': assignments,
            'times_called_away': called_away,
            'avg_weekly_premium': self.total_premiums / total_trades if total_trades > 0 else 0,
            
            # Stock metrics
            'starting_price': self.data['Close'].iloc[0],
            'ending_price': self.data['Close'].iloc[-1],
            'stock_return_pct': ((self.data['Close'].iloc[-1] / self.data['Close'].iloc[0]) - 1) * 100,
            'owns_stock_at_end': self.owns_stock,
            
            # Time
            'days_held': days_held,
            'years_held': years_held
        }
        
        return metrics
    
    def print_results(self, metrics: Dict):
        """Print comprehensive backtest results."""
        
        print(f"\n{'='*70}")
        print("BACKTEST RESULTS")
        print(f"{'='*70}\n")
        
        print(f"📊 PERFORMANCE SUMMARY")
        print(f"{'-'*70}")
        print(f"Initial Capital:        ${metrics['initial_capital']:>15,.2f}")
        print(f"Final Cash:             ${metrics['final_cash']:>15,.2f}")
        print(f"Stock Holdings:         ${metrics['stock_value']:>15,.2f}")
        print(f"Total Account Value:    ${metrics['total_value']:>15,.2f}")
        print(f"")
        print(f"Total Profit:           ${metrics['total_profit']:>15,.2f}")
        print(f"Total Return:           {metrics['total_return_pct']:>15.2f}%")
        print(f"Annualized Return:      {metrics['annualized_return_pct']:>15.2f}%")
        
        print(f"\n💰 PROFIT BREAKDOWN")
        print(f"{'-'*70}")
        print(f"Total Premiums:         ${metrics['total_premiums']:>15,.2f}")
        print(f"Realized Stock Gains:   ${metrics['total_stock_gains']:>15,.2f}")
        print(f"Unrealized Gains:       ${metrics['unrealized_gain']:>15,.2f}")
        
        print(f"\n📈 BUY & HOLD COMPARISON")
        print(f"{'-'*70}")
        print(f"Buy & Hold Value:       ${metrics['buy_hold_value']:>15,.2f}")
        print(f"Buy & Hold Profit:      ${metrics['buy_hold_profit']:>15,.2f}")
        print(f"Buy & Hold Return:      {metrics['buy_hold_return_pct']:>15.2f}%")
        print(f"")
        print(f"Wheel Outperformance:   ${metrics['outperformance']:>15,.2f}")
        
        if metrics['outperformance'] > 0:
            print(f"✅ Wheel Strategy BEAT buy-and-hold by ${metrics['outperformance']:,.2f}")
        else:
            print(f"❌ Buy-and-hold BEAT Wheel Strategy by ${abs(metrics['outperformance']):,.2f}")
        
        print(f"\n📊 TRADE STATISTICS")
        print(f"{'-'*70}")
        print(f"Total Weeks Traded:     {metrics['total_weeks']:>15}")
        print(f"Put Contracts Sold:     {metrics['put_trades']:>15}")
        print(f"Call Contracts Sold:    {metrics['call_trades']:>15}")
        print(f"Times Assigned:         {metrics['times_assigned']:>15}")
        print(f"Times Called Away:      {metrics['times_called_away']:>15}")
        print(f"Avg Weekly Premium:     ${metrics['avg_weekly_premium']:>15,.2f}")
        
        print(f"\n📈 STOCK PERFORMANCE")
        print(f"{'-'*70}")
        print(f"Starting Price:         ${metrics['starting_price']:>15,.2f}")
        print(f"Ending Price:           ${metrics['ending_price']:>15,.2f}")
        print(f"Stock Return:           {metrics['stock_return_pct']:>15.2f}%")
        print(f"Currently Own Stock:    {'Yes' if metrics['owns_stock_at_end'] else 'No':>15}")
        
        print(f"\n⏱️  TIME METRICS")
        print(f"{'-'*70}")
        print(f"Days in Trade:          {metrics['days_held']:>15}")
        print(f"Years:                  {metrics['years_held']:>15.2f}")
        
        print(f"\n{'='*70}\n")
    
    def plot_results(self, trades_df: pd.DataFrame, metrics: Dict):
        """Create visualization of backtest results."""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Wheel Strategy Backtest: {self.ticker}\n'
                     f'{self.start_date.strftime("%Y-%m-%d")} to {self.end_date.strftime("%Y-%m-%d")}',
                     fontsize=16, fontweight='bold')
        
        # 1. Stock Price and Strikes
        ax1.plot(self.data.index, self.data['Close'], label='Stock Price', linewidth=2, color='blue')
        
        # Plot put strikes
        put_trades = trades_df[trades_df['type'] == 'SELL_PUT']
        ax1.scatter(put_trades['date'], put_trades['strike'], 
                   color='green', marker='v', s=100, alpha=0.6, label='Put Strikes')
        
        # Plot call strikes
        call_trades = trades_df[trades_df['type'] == 'SELL_CALL']
        ax1.scatter(call_trades['date'], call_trades['strike'],
                   color='red', marker='^', s=100, alpha=0.6, label='Call Strikes')
        
        # Mark assignments
        assigned = trades_df[trades_df['status'] == 'ASSIGNED']
        ax1.scatter(assigned['date'], assigned['assignment_price'],
                   color='orange', marker='o', s=200, label='Assigned', zorder=5)
        
        # Mark called away
        called = trades_df[trades_df['status'] == 'CALLED_AWAY']
        ax1.scatter(called['date'], called['sale_price'],
                   color='purple', marker='s', s=200, label='Called Away', zorder=5)
        
        ax1.set_title('Stock Price & Option Strikes', fontweight='bold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Cumulative Premiums
        trades_df['cumulative_premium'] = trades_df['premium'].cumsum()
        ax2.plot(trades_df['date'], trades_df['cumulative_premium'], 
                linewidth=2, color='green')
        ax2.fill_between(trades_df['date'], 0, trades_df['cumulative_premium'], 
                         alpha=0.3, color='green')
        ax2.set_title(f'Cumulative Premium Income\nTotal: ${metrics["total_premiums"]:,.2f}',
                     fontweight='bold')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Cumulative Premiums ($)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Portfolio Value Over Time
        portfolio_values = []
        for idx, row in trades_df.iterrows():
            trade_date = row['date']
            # Find stock price at this date
            stock_price = self.data.loc[trade_date, 'Close'] if trade_date in self.data.index else self.data['Close'].iloc[-1]
            
            # Calculate portfolio value (simplified)
            cash_at_trade = row['cash']
            if row['type'] == 'SELL_CALL' and row['status'] != 'CALLED_AWAY':
                # Owns stock
                stock_val = stock_price * 100
                portfolio_values.append(cash_at_trade + stock_val)
            else:
                portfolio_values.append(cash_at_trade)
        
        trades_df['portfolio_value'] = portfolio_values
        
        ax3.plot(trades_df['date'], trades_df['portfolio_value'], 
                linewidth=2, color='blue', label='Wheel Strategy')
        
        # Add buy-and-hold line
        initial_shares = metrics['initial_capital'] / metrics['starting_price']
        buy_hold_values = self.data['Close'] * initial_shares
        ax3.plot(self.data.index, buy_hold_values, 
                linewidth=2, color='gray', linestyle='--', label='Buy & Hold', alpha=0.7)
        
        ax3.axhline(y=metrics['initial_capital'], color='red', linestyle=':', 
                   label='Initial Capital', alpha=0.5)
        ax3.set_title(f'Portfolio Value\nFinal: ${metrics["total_value"]:,.2f} ({metrics["total_return_pct"]:.1f}%)',
                     fontweight='bold')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Portfolio Value ($)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Weekly Premium Distribution
        ax4.hist(trades_df['premium'], bins=30, color='green', alpha=0.7, edgecolor='black')
        ax4.axvline(x=metrics['avg_weekly_premium'], color='red', linestyle='--', 
                   linewidth=2, label=f'Average: ${metrics["avg_weekly_premium"]:.2f}')
        ax4.set_title('Weekly Premium Distribution', fontweight='bold')
        ax4.set_xlabel('Premium ($)')
        ax4.set_ylabel('Frequency')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def export_trades(self, trades_df: pd.DataFrame, filename: str = None):
        """Export trade history to CSV."""
        if filename is None:
            filename = f'wheel_backtest_{self.ticker}_{self.start_date.strftime("%Y%m%d")}_{self.end_date.strftime("%Y%m%d")}.csv'
        
        trades_df.to_csv(filename, index=False)
        print(f"\n📁 Trade history exported to: {filename}")
        return filename


def run_backtest(ticker: str, start_date: str, end_date: str, 
                initial_capital: float = 50000,
                show_plot: bool = True,
                export_csv: bool = True) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to run a complete backtest.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    start_date : str
        Start date 'YYYY-MM-DD'
    end_date : str
        End date 'YYYY-MM-DD'
    initial_capital : float
        Starting capital
    show_plot : bool
        Whether to display plots
    export_csv : bool
        Whether to export results to CSV
    
    Returns:
    --------
    trades_df : pd.DataFrame
        DataFrame of all trades
    metrics : dict
        Performance metrics
    """
    
    # Initialize and run backtest
    backtest = WheelStrategyBacktest(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )
    
    trades_df = backtest.run_backtest()
    metrics = backtest.calculate_metrics(trades_df)
    backtest.print_results(metrics)
    
    if show_plot:
        fig = backtest.plot_results(trades_df, metrics)
        plt.savefig(f'wheel_backtest_{ticker}_{start_date}_{end_date}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    if export_csv:
        backtest.export_trades(trades_df)
    
    return trades_df, metrics


# Example usage
if __name__ == "__main__":
    
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                  WHEEL STRATEGY BACKTESTER                        ║
    ║                                                                   ║
    ║  This script backtests the Wheel Options Strategy:               ║
    ║  1. Sell cash-secured puts weekly (5% OTM)                       ║
    ║  2. Get assigned and own stock if it drops                       ║
    ║  3. Sell covered calls weekly (5% OTM) while holding             ║
    ║  4. Get called away when stock rises                             ║
    ║  5. Repeat the cycle                                             ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Example 1: Tesla 2025
    print("\nExample 1: TESLA (TSLA) - Full Year 2025")
    print("=" * 70)
    trades_tsla, metrics_tsla = run_backtest(
        ticker='TSLA',
        start_date='2025-01-01',
        end_date='2025-12-31',
        initial_capital=40000
    )
    
    # Example 2: Apple 2024
    print("\n\nExample 2: APPLE (AAPL) - Full Year 2024")
    print("=" * 70)
    trades_aapl, metrics_aapl = run_backtest(
        ticker='AAPL',
        start_date='2024-01-01',
        end_date='2024-12-31',
        initial_capital=20000
    )
    
    # Example 3: Custom stock
    print("\n\n" + "=" * 70)
    print("TO RUN YOUR OWN BACKTEST:")
    print("=" * 70)
    print("""
    from wheel_strategy_backtest import run_backtest
    
    trades, metrics = run_backtest(
        ticker='YOUR_TICKER',      # e.g., 'NVDA', 'HOOD', 'AFRM'
        start_date='2024-01-01',   # Start date
        end_date='2024-12-31',     # End date
        initial_capital=50000      # Starting capital
    )
    
    # Access specific metrics
    print(f"Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"Total Premiums: ${metrics['total_premiums']:,.2f}")
    print(f"Beat Buy-Hold by: ${metrics['outperformance']:,.2f}")
    """)
