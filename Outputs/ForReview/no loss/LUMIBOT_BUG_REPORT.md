# Bug Report: PolygonDataBacktesting Ignores Date Range and Runs Single Iteration

**Lumibot Version**: 3.18.2
**Python Version**: 3.x
**OS**: Windows 10/11
**Date Reported**: October 26, 2025

---

## Summary

When using `PolygonDataBacktesting` with `Strategy.run_backtest()`, the backtesting engine:
1. **Ignores the requested date range** and always uses November 1, 2024 as the start date
2. **Runs only 1 iteration** instead of the expected 60+ trading days
3. **Returns no trades dataframe** (tuple result has no `.trades_df` attribute)
4. **Does not create new CSV log files** for subsequent runs

This occurs consistently across multiple different requested date ranges and makes it impossible to backtest strategies over custom time periods.

---

## Environment

```python
import lumibot
print(f"Lumibot version: {lumibot.__version__}")
# Output: Lumibot version 3.18.2
```

**Polygon.io Plan**: Options Starter ($29/month, 2-year historical data)
**API Key**: Valid and working (tested with direct Polygon API calls)

---

## Steps to Reproduce

### Minimal Reproducible Example

```python
#!/usr/bin/env python3
"""
Minimal reproduction of PolygonDataBacktesting date range bug
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from lumibot.strategies import Strategy
from lumibot.backtesting import PolygonDataBacktesting

load_dotenv()

class MinimalStrategy(Strategy):
    """Minimal strategy that just buys and holds SPY"""

    def initialize(self):
        self.sleeptime = "1D"
        print(f"\n{'='*70}")
        print(f"Strategy Initialized")
        print(f"{'='*70}\n")

    def on_trading_iteration(self):
        current_date = self.get_datetime().date()
        print(f"\n--- Iteration: {current_date} ---")

        # Just buy 1 share of SPY if we don't have it
        position = self.get_position("SPY")
        if not position or position.quantity == 0:
            print("Buying 1 share of SPY")
            self.create_order("SPY", 1, "buy")
        else:
            print(f"Already holding {position.quantity} shares")


if __name__ == "__main__":
    # TEST 1: Request Jan-Mar 2024 (Q1 2024)
    print("="*70)
    print("TEST 1: Requesting Jan 1 - Mar 31, 2024 (Q1 2024, 3 months)")
    print("="*70)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)

    print(f"Requested Start: {start_date.strftime('%Y-%m-%d')}")
    print(f"Requested End: {end_date.strftime('%Y-%m-%d')}")
    print(f"Expected iterations: ~60 trading days")
    print()

    results = MinimalStrategy.run_backtest(
        PolygonDataBacktesting,
        start_date,
        end_date,
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
        polygon_has_paid_subscription=True,
        show_plot=False,
        show_tearsheet=False,
        show_indicators=False,
    )

    print("\n" + "="*70)
    print("TEST 1 RESULTS")
    print("="*70)
    print(f"Results type: {type(results)}")
    print(f"Has trades_df: {hasattr(results, 'trades_df')}")

    # TEST 2: Request different date range (Sept-Oct 2024)
    print("\n\n" + "="*70)
    print("TEST 2: Requesting Sept 1 - Oct 31, 2024 (2 months)")
    print("="*70)

    start_date2 = datetime(2024, 9, 1)
    end_date2 = datetime(2024, 10, 31)

    print(f"Requested Start: {start_date2.strftime('%Y-%m-%d')}")
    print(f"Requested End: {end_date2.strftime('%Y-%m-%d')}")
    print(f"Expected iterations: ~40 trading days")
    print()

    results2 = MinimalStrategy.run_backtest(
        PolygonDataBacktesting,
        start_date2,
        end_date2,
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
        polygon_has_paid_subscription=True,
        show_plot=False,
        show_tearsheet=False,
        show_indicators=False,
    )

    print("\n" + "="*70)
    print("TEST 2 RESULTS")
    print("="*70)
    print(f"Results type: {type(results2)}")
    print(f"Has trades_df: {hasattr(results2, 'trades_df')}")
```

### Expected Behavior

**TEST 1** (Jan 1 - Mar 31, 2024):
- First iteration should show: `--- Iteration: 2024-01-01 ---` (or next trading day)
- Should run ~60 iterations (one per trading day)
- Should take 30-60 seconds to complete
- Should return results object with `.trades_df` attribute
- Should create new CSV file in `logs/` directory

**TEST 2** (Sept 1 - Oct 31, 2024):
- First iteration should show: `--- Iteration: 2024-09-01 ---` (or next trading day)
- Should run ~40 iterations
- Should create DIFFERENT results than TEST 1

### Actual Behavior

**Both TEST 1 and TEST 2 produce identical output:**

```
======================================================================
Strategy Initialized
======================================================================

Progress ||   1.26%  [Elapsed: 0:00:10 ETA: 0:13:00]

--- Iteration: 2024-11-01 ---
Buying 1 share of SPY

Progress || 100.00%  [Elapsed: 0:00:30 ETA: 0:00:00]

Results type: <class 'tuple'>
Has trades_df: False
```

**Issues observed:**
1. ✗ Date is `2024-11-01` for BOTH tests (neither Jan 1 nor Sept 1)
2. ✗ Only 1 iteration runs (not 60 or 40)
3. ✗ Completes in ~30 seconds (too fast for 60 days of data retrieval)
4. ✗ No `trades_df` attribute on results
5. ✗ No new CSV files created in `logs/` directory

---

## Additional Testing

### Test 3: Different Year (2023)

```python
start_date = datetime(2023, 6, 1)
end_date = datetime(2023, 8, 31)
```

**Result**: Still shows `--- Iteration: 2024-11-01 ---`

### Test 4: Recent Dates (2025)

```python
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 3, 31)
```

**Result**: Still shows `--- Iteration: 2024-11-01 ---`

### Conclusion

**The date 2024-11-01 appears to be hardcoded or cached somewhere in the Polygon backtesting integration.** It does not change regardless of requested start/end dates.

---

## Investigation

### Polygon API Direct Test

To verify this is not a Polygon API issue, we tested the API directly:

```python
from polygon import RESTClient
import os

client = RESTClient(os.getenv("POLYGON_API_KEY"))

# Test: Get SPY price bars for Jan 2024
bars = client.get_aggs(
    ticker="SPY",
    multiplier=1,
    timespan="day",
    from_="2024-01-01",
    to="2024-01-31",
)

bar_list = list(bars)
print(f"Retrieved {len(bar_list)} bars for Jan 2024")
# Output: Retrieved 21 bars for Jan 2024  ✓ WORKS
```

**Conclusion**: The Polygon API itself works correctly and returns data for requested date ranges. The issue is in Lumibot's `PolygonDataBacktesting` integration.

### Potential Root Causes

Based on reviewing `lumibot/backtesting/polygon_backtesting.py`:

1. **Date Calculation Issue**: The `START_BUFFER` (5 days) is applied, but this doesn't explain an 11-month shift
2. **Caching Problem**: Polygon might be caching data from an initial request and reusing it
3. **Parameter Passing**: `run_backtest()` might not be correctly passing `datetime_start`/`datetime_end` to `PolygonDataBacktesting.__init__()`
4. **Default Date**: There might be a default date range that overrides user input when certain conditions are met

---

## Code Review Findings

### Expected Flow

From Lumibot documentation:

```python
results = Strategy.run_backtest(
    PolygonDataBacktesting,  # Pass the CLASS
    backtesting_start,       # Should become datetime_start
    backtesting_end,         # Should become datetime_end
    polygon_api_key=api_key,
)
```

Expected: `PolygonDataBacktesting(datetime_start=backtesting_start, datetime_end=backtesting_end, api_key=polygon_api_key)`

### Observed Behavior

The backtest runs from `2024-11-01` regardless of `backtesting_start`/`backtesting_end` values.

**Hypothesis**: Either:
- The date parameters are not being passed through correctly
- There's a cached date range that takes precedence
- The date calculation logic has a bug

---

## Impact

This bug makes it **impossible to backtest strategies over custom date ranges** using Polygon data, which is a core feature of Lumibot. Users cannot:

1. Test strategies across different market conditions
2. Validate strategies over specific historical periods
3. Generate performance metrics for custom timeframes
4. Compare results across different time periods

---

## Workarounds Attempted

### ❌ Workaround 1: Clear Cache

```python
import shutil
shutil.rmtree("polygon_data_cache", ignore_errors=True)
```

**Result**: No change

### ❌ Workaround 2: Use Different Date Formats

```python
# Try date objects instead of datetime
from datetime import date
start_date = date(2024, 1, 1)
end_date = date(2024, 3, 31)
```

**Result**: No change

### ❌ Workaround 3: Explicit Time Zones

```python
from datetime import datetime
import pytz
eastern = pytz.timezone('US/Eastern')
start_date = eastern.localize(datetime(2024, 1, 1, 9, 30))
end_date = eastern.localize(datetime(2024, 3, 31, 16, 0))
```

**Result**: No change

### ✅ Workaround 4: Use Different Data Source

Using `YahooDataBacktesting` works correctly and respects date ranges, but lacks options data.

---

## Expected Fix

The `PolygonDataBacktesting` class should:

1. Accept and respect the `datetime_start` and `datetime_end` parameters
2. Run backtests for ALL trading days in the specified range
3. Return results with a `.trades_df` attribute containing trade data
4. Create new log files for each backtest run
5. Allow different date ranges in consecutive runs

---

## System Information

```python
import sys
import platform

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Lumibot: {lumibot.__version__}")

# Python: 3.11.x
# Platform: Windows-10-...
# Lumibot: 3.18.2
```

**Dependencies:**
```
lumibot==3.18.2
polygon-api-client==1.x.x
python-dotenv==1.x.x
```

---

## Additional Context

### Working with Options

We're specifically trying to backtest an options strategy (Zero Loss Butterfly) which requires:
- Stock data (SPY) ✓ Available
- Options chain data ✓ Available from Polygon Options Starter plan
- Historical options pricing ✓ Available from paid plan

The direct Polygon API returns all required data correctly for our requested date ranges. The issue is purely with Lumibot's integration layer.

### Logs Directory

After multiple backtest runs with different date ranges, the `logs/` directory contains only ONE set of CSV files with the timestamp from the first run. Subsequent runs don't create new files, suggesting the backtest isn't actually running or is using cached results.

---

## Request for Lumibot Team

1. **Can you reproduce this issue?** Please run the minimal example above
2. **Is there a known limitation** with Polygon date ranges we should be aware of?
3. **Is there a correct way** to specify date ranges that differs from the documentation?
4. **Could this be related** to the paid vs free subscription handling?

We're happy to provide additional information, test patches, or help debug this issue.

---

## Files for Reference

If helpful, we can provide:
- Complete strategy code showing the issue
- CSV output files from the single iteration
- Debug logs with verbose output
- Screen recordings of the backtest running

---

## Contact

**GitHub**: (provide if creating GitHub issue)
**Forum**: (provide if posting to forum)
**Email**: (provide if needed)

---

## Checklist

- [x] Tested with minimal reproducible example
- [x] Verified Polygon API works directly
- [x] Tried multiple different date ranges
- [x] Checked for cached data
- [x] Reviewed Lumibot documentation
- [x] Tested with paid Polygon subscription
- [x] Confirmed issue persists across Python restarts

---

**Thank you for your time and for building Lumibot! We love the framework and want to help make it better.**
