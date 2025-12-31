# PolygonDataBacktesting Ignores Date Range and Runs Single Iteration

## Description

`PolygonDataBacktesting` does not respect the `backtesting_start` and `backtesting_end` parameters passed to `Strategy.run_backtest()`. Instead, it always:
- Uses **November 1, 2024** as the start date (regardless of requested dates)
- Runs only **1 iteration** instead of the expected 40-60+ trading days
- Returns a tuple **without a `trades_df` attribute**
- Does **not create new CSV log files** for subsequent runs

This makes it impossible to backtest strategies over custom date ranges using Polygon data.

## Environment

- **Lumibot Version**: 3.18.2
- **Python Version**: 3.11.x
- **OS**: Windows 10/11
- **Polygon Plan**: Options Starter ($29/month, paid subscription)

## Minimal Reproducible Example

```python
#!/usr/bin/env python3
import os
from datetime import datetime
from lumibot.strategies import Strategy
from lumibot.backtesting import PolygonDataBacktesting

class MinimalStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"

    def on_trading_iteration(self):
        current_date = self.get_datetime().date()
        print(f"Iteration: {current_date}")

        position = self.get_position("SPY")
        if not position or position.quantity == 0:
            self.create_order("SPY", 1, "buy")

# TEST: Request Jan-Mar 2024 (should be ~60 trading days)
results = MinimalStrategy.run_backtest(
    PolygonDataBacktesting,
    datetime(2024, 1, 1),   # Requested start
    datetime(2024, 3, 31),  # Requested end
    polygon_api_key=os.getenv("POLYGON_API_KEY"),
    polygon_has_paid_subscription=True,
    show_plot=False,
)
```

**Full script**: [minimal_polygon_bug_reproduction.py](https://gist.github.com/...) *(I can provide this if needed)*

## Expected Behavior

- First iteration should show: `Iteration: 2024-01-01` (or next trading day)
- Should run **~60 iterations** (one per trading day from Jan 1 - Mar 31, 2024)
- Should return results object with `.trades_df` attribute
- Should create new CSV file in `logs/` directory with trades

## Actual Behavior

```
Iteration: 2024-11-01
Results type: <class 'tuple'>
Has trades_df: False
```

**Issues:**
1. ✗ Date is `2024-11-01` (not the requested Jan 1)
2. ✗ Only **1 iteration** runs (not 60)
3. ✗ No `trades_df` attribute
4. ✗ No new CSV files created

## Additional Tests

I tested multiple different date ranges:

| Test | Requested Start | Requested End | Actual Start | Iterations |
|------|----------------|---------------|--------------|------------|
| 1 | 2024-01-01 | 2024-03-31 | 2024-11-01 | 1 |
| 2 | 2024-09-01 | 2024-10-31 | 2024-11-01 | 1 |
| 3 | 2023-06-01 | 2023-08-31 | 2024-11-01 | 1 |
| 4 | 2025-01-01 | 2025-03-31 | 2024-11-01 | 1 |

**All tests use the same hardcoded date (2024-11-01) with only 1 iteration.**

## Verification

To confirm this isn't a Polygon API issue, I tested the API directly:

```python
from polygon import RESTClient
client = RESTClient(os.getenv("POLYGON_API_KEY"))

bars = client.get_aggs(
    ticker="SPY",
    multiplier=1,
    timespan="day",
    from_="2024-01-01",
    to="2024-01-31",
)

print(f"Bars retrieved: {len(list(bars))}")
# Output: Bars retrieved: 21  ✓ Works correctly
```

**The Polygon API itself works fine and returns data for requested date ranges.** The issue is in Lumibot's integration.

## Workarounds Attempted

- ❌ Clearing cache directories
- ❌ Using `date` objects instead of `datetime`
- ❌ Explicit timezone handling
- ✅ Using `YahooDataBacktesting` works correctly (but lacks options data)

## Impact

This bug prevents users from:
- Backtesting strategies over custom time periods
- Testing across different market conditions
- Generating performance metrics for specific timeframes
- Using Polygon's paid options data for historical backtesting

## Potential Root Cause

Based on reviewing `lumibot/backtesting/polygon_backtesting.py`, possibilities include:

1. `datetime_start`/`datetime_end` not being passed correctly from `run_backtest()` to `PolygonDataBacktesting.__init__()`
2. Cached data from a previous request being reused
3. A default date range overriding user input
4. Date calculation logic error (START_BUFFER doesn't explain 11-month shift)

## Request

Could you help us understand:
1. Can you reproduce this issue with the minimal example?
2. Is there a known limitation with Polygon date ranges?
3. Is there a correct way to specify date ranges that differs from documentation?
4. Could this be related to paid vs free subscription handling?

Happy to provide additional debug info or test patches!

## Checklist

- [x] Minimal reproducible example provided
- [x] Verified Polygon API works directly
- [x] Tested multiple date ranges
- [x] Checked latest Lumibot version (3.18.2)
- [x] Reviewed documentation
- [x] Confirmed issue persists across restarts

---

Thank you for building Lumibot! We love the framework and want to help improve it.
