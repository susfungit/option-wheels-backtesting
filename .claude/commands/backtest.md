# Wheel Strategy Backtest

Run a wheel options strategy backtest on the specified stock ticker.

## Arguments

$ARGUMENTS - The stock ticker, start date, and end date (e.g., "TSLA 2024-01-01 2024-12-31")

## Instructions

1. Parse the arguments to extract:
   - `ticker`: Stock symbol (required)
   - `start_date`: Start date in YYYY-MM-DD format (required)
   - `end_date`: End date in YYYY-MM-DD format (required)

2. If any arguments are missing, ask the user to provide them.

3. Run the backtest using the CLI:
   ```bash
   cd /Users/sushant/python/option-wheels-backtester && uv run python main.py <ticker> <start_date> <end_date>
   ```

4. Present the results to the user, highlighting:
   - Total return percentage
   - Annualized return
   - Premium income collected
   - Buy-and-hold comparison
   - Number of trades executed

5. If the user wants to see the generated chart, read and display the PNG file that was created.

6. If the user wants to analyze the trades in detail, read the CSV file that was exported.
