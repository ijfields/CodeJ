#!/usr/bin/env python3
"""
Test Zero Loss Butterfly Strategy with Local Pandas Data

Uses the custom PandasOptionsDataSource to backtest with converted
Barchart/Yahoo Finance data in data/lumibot/

This tests the FIXED strategy code with actual options data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env from project root and change working directory
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / '.env'
load_dotenv(env_path)
os.chdir(project_root)

# Add paths for imports
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(project_root))

from zero_loss_butterfly import ZeroLossButterfly
from backtest_validator import validate_backtest
from pandas_backtesting import PandasBacktesting


def main():
    print("="*70)
    print("ZERO LOSS BUTTERFLY BACKTEST - LOCAL DATA")
    print("="*70)
    print()
    print("Strategy: Stock + Married Put + Call Butterfly")
    print("Symbol: SPY")
    print("Data Source: PandasOptionsDataSource (local data)")
    print("Data Location: data/lumibot/")
    print()
    print("NOTE: Using converted Barchart stock + Yahoo options data")
    print("      Date range: March 2024 - October 2025")
    print()
    print("="*70)
    print()

    try:
        # Strategy parameters
        strategy_params = {
            "symbol": "SPY",
            "shares_per_position": 100,
            "dte_target": 57,
            "dte_min": 50,
            "dte_max": 65,
            "strike_width": 10,
            "put_offset": -10,
            "center_offset": -5,
            "upper_offset": 5,
        }

        print("Strategy Parameters:")
        for key, value in strategy_params.items():
            print(f"  {key}: {value}")
        print()

        # Set backtest date range (based on available data)
        # From metadata: 2024-03-28 to 2025-10-24
        # Testing recent period with options data available
        start_date = datetime(2025, 10, 1)
        end_date = datetime(2025, 10, 24)

        print(f"Backtest Period:")
        print(f"  Start Date: {start_date.date()}")
        print(f"  End Date: {end_date.date()}")
        print()

        print("Starting backtest...")
        print("(This may take several minutes)")
        print()

        # Use ZeroLossButterfly.run_backtest() with our custom backtesting class
        results = ZeroLossButterfly.run_backtest(
            PandasBacktesting,
            start_date,
            end_date,
            parameters=strategy_params,
            data_dir="data/lumibot",
            show_plot=False,
            show_tearsheet=True,
            save_tearsheet=True
        )

        print()
        print("="*70)
        print("BACKTEST COMPLETED SUCCESSFULLY")
        print("="*70)
        print()

        # Check for results
        if results:
            if hasattr(results, 'stats_dict'):
                print("Performance Summary:")
                stats = results.stats_dict
                if 'total_return' in stats:
                    print(f"  Total Return: {stats['total_return']:.2%}")
                if 'max_drawdown' in stats:
                    print(f"  Max Drawdown: {stats['max_drawdown']:.2%}")

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
            csv_files = sorted(logs_dir.glob("ZeroLossButterfly_*_trades.csv"),
                             key=lambda p: p.stat().st_mtime, reverse=True)
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
                    print()
                    print("CRITICAL CHECK: Stock was purchased exactly ONCE")
                    print("BUG FIX VERIFIED: No re-buying loop detected")
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
        print(f"{type(e).__name__}: {e}")
        print()

        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
