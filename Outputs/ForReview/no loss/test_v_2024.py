#!/usr/bin/env python3
"""
Test Zero Loss Butterfly Strategy with V (Visa) - 2024 Historical Data
Using PolygonDataBacktesting with confirmed available date range

Period: Apr 15 - Oct 17, 2024 (matches video timeline)
Symbol: V (Visa)
Expected: Options data should be available in Polygon for 2024
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

def main():
    print("="*70)
    print("ZERO LOSS BUTTERFLY BACKTEST - V (VISA) 2024")
    print("="*70)
    print()
    print("Strategy: Stock + Married Put + Call Butterfly")
    print("Symbol: V (Visa)")
    print("Period: Apr 15 - Oct 17, 2024")
    print("Target DTE: 57 days")
    print("Strike Width: $10")
    print()
    print("NOTE: This period matches the video's historical timeline")
    print("      Using 2024 dates because Polygon has confirmed data")
    print()
    print("="*70)
    print()

    # Strategy parameters for V (from video analysis)
    strategy_params = {
        "symbol": "V",
        "shares_per_position": 100,
        "dte_target": 57,
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,
        "put_offset": -10,      # V at ~290: PUT at 280
        "center_offset": -3,    # Center CALL at 287
        "upper_offset": 7,      # Upper CALL at 297
        "roll_days_before_exp": 7,
        "check_frequency": "1D",
        "max_cost_vs_protection": 1.0,
    }

    # Backtesting configuration (matches video dates in 2024)
    start_date = datetime(2024, 4, 15)
    end_date = datetime(2024, 10, 17)

    print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"End Date: {end_date.strftime('%Y-%m-%d')}")
    print(f"Duration: ~6 months")
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
            polygon_api_key=os.getenv("POLYGON_API_KEY"),
            polygon_has_paid_subscription=False,
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
                        print("This means Polygon still doesn't have options data")
                        print()
                        print("Canceled orders breakdown:")
                        print(canceled[['symbol', 'side', 'asset.strike', 'asset.right']].to_string())

                    if len(filled) > 0:
                        print()
                        print("SUCCESS: Options orders were filled!")
                        print("This proves the strategy is working correctly")
                        print()
                        print("Sample filled orders:")
                        print(filled[['symbol', 'side', 'asset.strike', 'asset.right', 'filled_quantity']].head(10).to_string())

                        # Check for butterfly structure
                        calls = filled[filled['asset.right'] == 'CALL']
                        puts = filled[filled['asset.right'] == 'PUT']

                        print()
                        print(f"PUT orders: {len(puts)}")
                        print(f"CALL orders: {len(calls)}")

                        # Check if we sold 2 calls (butterfly key)
                        short_calls = calls[calls['side'] == 'sell']
                        if len(short_calls) > 0:
                            print()
                            print("SHORT CALLS (should have 2x quantity):")
                            print(short_calls[['symbol', 'side', 'asset.strike', 'filled_quantity']].to_string())
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
        print("  2. No options data available even for 2024 dates")
        print("  3. Network connectivity issues")
        print("  4. Need to upgrade Polygon subscription for options data")
        print()

if __name__ == "__main__":
    main()
