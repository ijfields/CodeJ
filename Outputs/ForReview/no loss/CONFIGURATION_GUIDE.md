# Backtesting Configuration Guide

## Overview

All backtest scripts now use a **centralized configuration system** via `backtest_config.py`. This ensures consistency across all test scripts and makes it easy to change settings in one place.

---

## Quick Start

### 1. Set Your Dates in .env

Edit `C:\Data\Cousin Ingrid\Git Hub\CodeJ\.env`:

```bash
# Backtesting Dates (YYYY-MM-DD format)
BACKTESTING_START=2024-11-01
BACKTESTING_END=2024-11-29

# Polygon Configuration
POLYGON_API_KEY=your_api_key_here
POLYGON_IS_PAID_SUBSCRIPTION=true

# Backtesting Flag
IS_BACKTESTING=true
```

### 2. Run Any Test Script

```bash
cd "Outputs/ForReview/no loss"
python test_spy_2024.py
```

The script will automatically:
- Load dates from `.env`
- Load Polygon configuration from `.env`
- Use consistent strategy parameters
- Display a configuration summary before running

---

## Configuration Priority

The system uses a **3-level priority** for date configuration:

```
1. Parameter Overrides (highest priority)
   ↓
2. Environment Variables (.env file)
   ↓
3. Sensible Defaults (Q1 2024: Jan 1 - Mar 31)
```

### Examples

**Using .env (recommended)**:
```python
from backtest_config import get_backtest_dates

start, end = get_backtest_dates()
# Uses BACKTESTING_START/END from .env
```

**With parameter override**:
```python
from datetime import datetime
from backtest_config import get_backtest_dates

custom_start = datetime(2023, 6, 1)
custom_end = datetime(2023, 8, 31)

start, end = get_backtest_dates(custom_start, custom_end)
# Uses parameter overrides, ignores .env
```

**Fallback to defaults**:
```python
# If .env has no dates set:
start, end = get_backtest_dates()
# Returns: 2024-01-01 to 2024-03-31
```

---

## Configuration Functions

### `get_backtest_dates(start_override=None, end_override=None)`

Returns: `(start_date, end_date)` tuple of datetime objects

**Priority**:
1. `start_override` and `end_override` parameters
2. `BACKTESTING_START` and `BACKTESTING_END` from `.env`
3. Default: Jan 1 - Mar 31, 2024

**Example**:
```python
start, end = get_backtest_dates()
print(f"Backtesting from {start} to {end}")
```

---

### `get_polygon_config()`

Returns: Dictionary with Polygon.io settings

**Keys**:
- `api_key`: Your Polygon API key (from `POLYGON_API_KEY` in `.env`)
- `has_paid_subscription`: Boolean (from `POLYGON_IS_PAID_SUBSCRIPTION` in `.env`)

**Example**:
```python
config = get_polygon_config()

results = Strategy.run_backtest(
    PolygonDataBacktesting,
    start,
    end,
    polygon_api_key=config["api_key"],
    polygon_has_paid_subscription=config["has_paid_subscription"]
)
```

---

### `get_strategy_params(symbol="SPY", **overrides)`

Returns: Dictionary of strategy parameters

**Default Parameters**:
```python
{
    "symbol": "SPY",
    "shares_per_position": 100,
    "dte_target": 57,
    "dte_min": 50,
    "dte_max": 65,
    "strike_width": 10,
    "put_offset": -10,
    "center_offset": -5,
    "upper_offset": 5,
    "roll_days_before_exp": 7,
    "check_frequency": "1D",
    "max_cost_vs_protection": 1.0,
}
```

**Example with overrides**:
```python
params = get_strategy_params(
    symbol="AAPL",
    dte_target=45,
    strike_width=5
)
# Returns defaults with symbol="AAPL", dte_target=45, strike_width=5
```

---

### `print_config_summary()`

Prints a formatted summary of all configuration settings.

**Output**:
```
======================================================================
BACKTESTING CONFIGURATION SUMMARY
======================================================================

Date Range:
  Start: 2024-11-01
  End:   2024-11-29
  Days:  28 calendar days (~20 trading days)

Polygon Configuration:
  API Key: ✓ Set
  Paid Plan: ✓ Yes

Environment:
  IS_BACKTESTING: true
======================================================================
```

---

## .env File Reference

### Required Variables

```bash
# Polygon API
POLYGON_API_KEY=your_key_here
```

### Optional Variables

```bash
# Backtesting Dates (if not set, defaults to Q1 2024)
BACKTESTING_START=2024-11-01
BACKTESTING_END=2024-11-29

# Polygon Subscription Level
POLYGON_IS_PAID_SUBSCRIPTION=true  # or false

# Backtesting Mode Flag
IS_BACKTESTING=true
```

### Date Format

**Always use**: `YYYY-MM-DD`

✅ Correct:
```bash
BACKTESTING_START=2024-11-01
```

❌ Incorrect:
```bash
BACKTESTING_START=11/01/2024  # Wrong!
BACKTESTING_START=2024/11/01  # Wrong!
BACKTESTING_START=Nov 1 2024  # Wrong!
```

---

## Usage Patterns

### Pattern 1: Standard Backtest (Uses .env)

```python
from backtest_config import (
    get_backtest_dates,
    get_polygon_config,
    get_strategy_params,
    print_config_summary
)

# Print configuration summary
print_config_summary()

# Get all configuration
start, end = get_backtest_dates()
polygon = get_polygon_config()
params = get_strategy_params("SPY")

# Run backtest
results = Strategy.run_backtest(
    PolygonDataBacktesting,
    start,
    end,
    parameters=params,
    polygon_api_key=polygon["api_key"],
    polygon_has_paid_subscription=polygon["has_paid_subscription"]
)
```

### Pattern 2: Custom Date Range

```python
from datetime import datetime
from backtest_config import get_backtest_dates, get_polygon_config

# Override dates for special test
custom_start = datetime(2023, 6, 1)
custom_end = datetime(2023, 8, 31)

start, end = get_backtest_dates(custom_start, custom_end)
polygon = get_polygon_config()

# Dates from parameters, other config from .env
results = Strategy.run_backtest(
    PolygonDataBacktesting,
    start,
    end,
    polygon_api_key=polygon["api_key"],
    polygon_has_paid_subscription=polygon["has_paid_subscription"]
)
```

### Pattern 3: Multiple Symbols

```python
from backtest_config import get_strategy_params

symbols = ["SPY", "QQQ", "AAPL"]

for symbol in symbols:
    params = get_strategy_params(symbol)
    # Run backtest with params
```

---

## Benefits

### ✅ Consistency
- All scripts use same configuration source
- No hardcoded dates in multiple files
- Single source of truth

### ✅ Flexibility
- Easy to change dates (just edit .env)
- Can override when needed
- Sensible defaults as fallback

### ✅ Clarity
- Configuration summary shows what will be used
- Clear priority order
- Warns when API key missing

### ✅ Lumibot Compatible
- Respects Lumibot's .env convention
- Works with both environment variables and parameters
- No conflicts with Lumibot's internal date handling

---

## Updating Dates

### To Test Different Periods

**Option 1: Edit .env** (recommended)
```bash
# In .env, change:
BACKTESTING_START=2024-01-01
BACKTESTING_END=2024-03-31

# Then run any test script
python test_spy_2024.py
```

**Option 2: Override in code** (for special cases)
```python
from datetime import datetime
from backtest_config import get_backtest_dates

# One-time override
start = datetime(2023, 6, 1)
end = datetime(2023, 8, 31)

dates = get_backtest_dates(start, end)
```

---

## Common Date Ranges

### Q1 2024 (January - March)
```bash
BACKTESTING_START=2024-01-01
BACKTESTING_END=2024-03-31
```

### Q2 2024 (April - June)
```bash
BACKTESTING_START=2024-04-01
BACKTESTING_END=2024-06-30
```

### Q3 2024 (July - September)
```bash
BACKTESTING_START=2024-07-01
BACKTESTING_END=2024-09-30
```

### Q4 2024 (October - December)
```bash
BACKTESTING_START=2024-10-01
BACKTESTING_END=2024-12-31
```

### Full Year 2024
```bash
BACKTESTING_START=2024-01-01
BACKTESTING_END=2024-12-31
```

### Last 30 Days (Example)
```bash
BACKTESTING_START=2024-10-28
BACKTESTING_END=2024-11-27
```

---

## Troubleshooting

### "Backtest uses wrong dates"

**Check**:
1. Is `BACKTESTING_START/END` set in `.env`?
2. Are dates in `YYYY-MM-DD` format?
3. Is `.env` in the project root?

**Solution**:
```bash
# Verify .env location
cd "C:\Data\Cousin Ingrid\Git Hub\CodeJ"
cat .env | grep BACKTESTING
```

### "API key not found"

**Check**:
1. Is `POLYGON_API_KEY` in `.env`?
2. Is the key value correct?

**Solution**:
```bash
# Add to .env
echo "POLYGON_API_KEY=your_key_here" >> .env
```

### "Dates from parameters ignored"

**Reason**: Lumibot prioritizes environment variables

**Solution**: Either:
1. Remove `BACKTESTING_START/END` from `.env`, OR
2. Use `backtest_config.py` which handles priority correctly

---

## Testing Configuration

Run the config module directly to test:

```bash
cd "Outputs/ForReview/no loss"
python backtest_config.py
```

**Output**:
```
Testing backtest_config.py

[Config] Using dates from .env: 2024-11-01 to 2024-11-29

Dates: 2024-11-01 00:00:00 to 2024-11-29 00:00:00

[Config] Polygon API key loaded (length: 32)
[Config] Paid subscription: True

Polygon config: {'api_key': '...', 'has_paid_subscription': True}

[Config] Strategy: SPY
[Config] Target DTE: 57 days

Strategy params: {...}

======================================================================
BACKTESTING CONFIGURATION SUMMARY
======================================================================
...
```

---

## Summary

**Before** (inconsistent):
- Dates hardcoded in each test script
- Polygon config repeated everywhere
- Hard to change test periods
- Unclear what configuration is used

**After** (consistent):
- Single source of truth (`.env`)
- All scripts use `backtest_config.py`
- Easy to change dates
- Clear configuration summary

**To change dates**: Just edit `.env` and run any test script!
