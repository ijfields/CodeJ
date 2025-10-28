#!/usr/bin/env python3
"""
Test Zero Loss Butterfly Strategy with SPY - Q1 2024 Data
Using PolygonDataBacktesting with Polygon Options Starter plan

Period: Jan 1 - Mar 31, 2024 (3 months, well within 2-year window)
Symbol: SPY (most liquid ETF)
Expected: Good options data coverage with paid Polygon plan ($29/month)
Note: Today is Oct 27, 2025 - Q1 2024 is 6-9 months ago, should have complete data
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from glob import glob

# Load .env from project root and change working directory
# This prevents Lumibot's "No .env file found" warning
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / '.env'
load_dotenv(env_path)

# Change to project root so Lumibot can also find .env
os.chdir(project_root)

from lumibot.brokers import Alpaca
from lumibot.backtesting import PolygonDataBacktesting

# Add current script directory to path to import strategy and validator
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from zero_loss_butterfly import ZeroLossButterfly
from backtest_validator import validate_backtest
from backtest_config import get_backtest_dates, get_polygon_config, get_strategy_params, print_config_summary

def main():
    print("="*70)
    print("ZERO LOSS BUTTERFLY BACKTEST - SPY")
    print("="*70)
    print()

    # Get configuration from centralized config (reads .env)
    print_config_summary()

    start_date, end_date = get_backtest_dates()
    polygon_config = get_polygon_config()
    strategy_params = get_strategy_params(
        symbol="SPY",
        put_offset=-10,      # SPY at ~520: PUT at 510
        center_offset=-5,    # Center CALL at 515
        upper_offset=5,      # Upper CALL at 525
    )

    print("Strategy: Stock + Married Put + Call Butterfly")
    print("="*70)
    print()

    # Run backtest with PolygonDataBacktesting
    print("Starting backtest...")
    print("(This may take several minutes depending on data retrieval)")
    print()

    try:
        results = ZeroLossButterfly.run_backtest(
            PolygonDataBacktesting,
            start_date,
            end_date,
            parameters=strategy_params,
            polygon_api_key=polygon_config["api_key"],
            polygon_has_paid_subscription=polygon_config["has_paid_subscription"],
            show_plot=True,
            show_tearsheet=True,
            save_tearsheet=True,
            show_indicators=False,
            benchmark_asset="SPY"
        )

        print()
        print("="*70)
        print("BACKTEST COMPLETED SUCCESSFULLY")
        print("="*70)
        print()
        print(f"Results type: {type(results)}")

        if results:
            # Check if we have trades
            if hasattr(results, 'trades_df') and results.trades_df is not None:
                trades_count = len(results.trades_df)
                print(f"Total Trades: {trades_count}")

                if trades_count > 0:
                    # Count option vs stock trades
                    option_trades = results.trades_df[results.trades_df['asset.strike'] > 0]
                    stock_trades = results.trades_df[results.trades_df['asset.strike'] == 0]

                    print(f"Stock Trades: {len(stock_trades)}")
                    print(f"Option Trades: {len(option_trades)}")

                    # Check for canceled orders
                    canceled = results.trades_df[results.trades_df['status'] == 'canceled']
                    filled = results.trades_df[results.trades_df['status'] == 'fill']

                    print()
                    print(f"Filled Orders: {len(filled)}")
                    print(f"Canceled Orders: {len(canceled)}")

                    if len(canceled) > 0:
                        print()
                        print("WARNING: Some orders were canceled!")
                        print("Canceled orders breakdown:")
                        print(canceled[['symbol', 'side', 'asset.strike', 'asset.right']].to_string())

                    if len(filled) > 0:
                        print()
                        print("SUCCESS: Orders were filled!")
                        print("Sample filled orders:")
                        print(filled[['symbol', 'side', 'asset.strike', 'asset.right', 'filled_quantity']].head(10).to_string())
                else:
                    print("WARNING: No trades were executed!")
            else:
                print("WARNING: No trades dataframe available")

            # Portfolio stats
            if hasattr(results, 'portfolio_value'):
                print()
                print(f"Final Portfolio Value: ${results.portfolio_value:,.2f}")

        print()
        print("Check the following files for detailed results:")
        print("  - tearsheet HTML file")
        print("  - trades CSV file")
        print("  - strategy log file")
        print()

        # Find the most recent trades CSV file and validate it
        print("="*70)
        print("RUNNING BACKTEST VALIDATION")
        print("="*70)
        print()

        # Look for the most recent trades CSV file
        logs_dir = script_dir / "logs"
        if logs_dir.exists():
            csv_files = sorted(logs_dir.glob("ZeroLossButterfly_*_trades.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
            if csv_files:
                latest_csv = csv_files[0]
                print(f"Validating: {latest_csv.name}")
                print()

                # Run validation
                validation_passed = validate_backtest(str(latest_csv), expected_stock_shares=100)

                if validation_passed:
                    print()
                    print("="*70)
                    print("SUCCESS: Backtest validation passed!")
                    print("="*70)
                else:
                    print()
                    print("="*70)
                    print("WARNING: Backtest validation detected issues!")
                    print("Please review the validation report above.")
                    print("="*70)
            else:
                print("No trades CSV files found in logs/")
        else:
            print("logs/ directory not found")

        print()

    except Exception as e:
        print()
        print("="*70)
        print("ERROR DURING BACKTEST")
        print("="*70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Possible causes:")
        print("  1. Polygon API key not set or invalid")
        print("  2. No options data available for this date range")
        print("  3. Network connectivity issues")
        print()

if __name__ == "__main__":
    main()
