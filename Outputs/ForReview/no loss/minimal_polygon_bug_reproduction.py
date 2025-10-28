#!/usr/bin/env python3
"""
Minimal Reproduction of PolygonDataBacktesting Date Range Bug

This script demonstrates that PolygonDataBacktesting ignores requested
date ranges and always uses November 1, 2024 as the start date.

To run this test:
1. Set POLYGON_API_KEY in your environment or .env file
2. Run: python minimal_polygon_bug_reproduction.py
3. Observe that BOTH tests show "Iteration: 2024-11-01" despite requesting different dates

Expected: Each test should run for 40-60 trading days starting from the requested date
Actual: Both tests run 1 iteration on 2024-11-01
"""

import os
from datetime import datetime
from pathlib import Path

# Try to load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from lumibot.strategies import Strategy
from lumibot.backtesting import PolygonDataBacktesting


class MinimalStrategy(Strategy):
    """
    Minimal strategy that just buys and holds SPY.
    Prints each iteration date to show the actual backtest range.
    """

    def initialize(self):
        self.sleeptime = "1D"
        self.iteration_count = 0
        print(f"\n{'='*70}")
        print(f"Strategy Initialized")
        print(f"{'='*70}\n")

    def on_trading_iteration(self):
        self.iteration_count += 1
        current_date = self.get_datetime().date()
        print(f"Iteration #{self.iteration_count}: {current_date}")

        # Just buy 1 share of SPY if we don't have it
        position = self.get_position("SPY")
        if not position or position.quantity == 0:
            print("  -> Buying 1 share of SPY")
            order = self.create_order("SPY", 1, "buy")
            self.submit_order(order)
        else:
            print(f"  -> Already holding {position.quantity} shares")


def run_test(test_name, start_date, end_date, expected_days):
    """Run a single backtest and report results"""
    print("\n" + "="*70)
    print(f"{test_name}")
    print("="*70)
    print(f"Requested Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"Requested End:   {end_date.strftime('%Y-%m-%d')}")
    print(f"Expected Days:   ~{expected_days} trading days")
    print("="*70)

    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("\nERROR: POLYGON_API_KEY not set in environment!")
        print("Set it with: export POLYGON_API_KEY='your_key_here'")
        print("Or create a .env file with: POLYGON_API_KEY=your_key_here")
        return None

    # Run the backtest
    results = MinimalStrategy.run_backtest(
        PolygonDataBacktesting,
        start_date,
        end_date,
        polygon_api_key=api_key,
        polygon_has_paid_subscription=True,  # Set to False if you have free tier
        show_plot=False,
        show_tearsheet=False,
        show_indicators=False,
    )

    # Report results
    print("\n" + "-"*70)
    print(f"{test_name} - RESULTS")
    print("-"*70)
    print(f"Results type:     {type(results)}")
    print(f"Has trades_df:    {hasattr(results, 'trades_df')}")

    if hasattr(results, 'trades_df') and results.trades_df is not None:
        print(f"Trades count:     {len(results.trades_df)}")
    else:
        print(f"Trades count:     N/A (no trades dataframe)")

    # Check for log files
    logs_dir = Path("logs")
    if logs_dir.exists():
        csv_files = list(logs_dir.glob("MinimalStrategy_*_trades.csv"))
        print(f"CSV files created: {len(csv_files)}")
        if csv_files:
            latest = sorted(csv_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
            print(f"Latest CSV:       {latest.name}")
    else:
        print(f"CSV files created: 0 (logs/ directory doesn't exist)")

    print("-"*70)
    return results


def main():
    print("\n" + "="*70)
    print("LUMIBOT POLYGON BACKTESTING - DATE RANGE BUG REPRODUCTION")
    print("="*70)
    print()
    print("This script tests whether PolygonDataBacktesting respects requested dates.")
    print("Expected: Each test should use different date ranges and run multiple iterations.")
    print("Actual: You'll see both tests use 2024-11-01 with only 1 iteration.")
    print()

    # TEST 1: Q1 2024 (Jan-Mar)
    test1_results = run_test(
        "TEST 1: Q1 2024 (Jan-Mar)",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 3, 31),
        expected_days=60
    )

    # TEST 2: Q3 2024 (Sept-Oct)
    test2_results = run_test(
        "TEST 2: Sept-Oct 2024",
        start_date=datetime(2024, 9, 1),
        end_date=datetime(2024, 10, 31),
        expected_days=40
    )

    # TEST 3: Different year (2023)
    test3_results = run_test(
        "TEST 3: Mid-2023 (Jun-Aug)",
        start_date=datetime(2023, 6, 1),
        end_date=datetime(2023, 8, 31),
        expected_days=60
    )

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print()
    print("If the bug exists, you should see:")
    print("  - All 3 tests show 'Iteration #1: 2024-11-01'")
    print("  - Only 1 iteration per test (not 40-60)")
    print("  - No trades_df attribute on results")
    print("  - Same CSV file used for all tests")
    print()
    print("Expected behavior:")
    print("  - TEST 1: First iteration ~2024-01-01, 60 iterations")
    print("  - TEST 2: First iteration ~2024-09-01, 40 iterations")
    print("  - TEST 3: First iteration ~2023-06-01, 60 iterations")
    print("  - Different CSV files for each test")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
