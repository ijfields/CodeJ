# 0DTE IWM Premium Collection Strategy

## Overview

This is a production-ready implementation of a **0DTE (Zero Days To Expiration) options premium collection strategy** on IWM (iShares Russell 2000 ETF).

**File Location**: `C:\Data\Cousin Ingrid\Git Hub\CodeJ\Outputs\Strategies\0dte_iwm_premium_collection.py`

## Strategy Summary

### What It Does

The strategy **sells out-of-the-money (OTM) options** at market open and buys them back when the premium decays to target levels during the same trading day.

### Position Structure

**Entry (within first 30 minutes of market open):**
- Sell 10 PUT contracts ($5 below current price)
- Sell 5 CALL contracts at higher strike ($191 or dynamic)
- Sell 5 CALL contracts at mid strike ($190 or dynamic)

**Exit (when premium decays to target):**
- Buy back PUTs when premium <= $0.02
- Buy back high CALLs when premium <= $0.15
- Buy back mid CALLs when premium <= $0.07

**Force Close:**
- All positions auto-closed 15 minutes before market close

## Key Features

### 1. Complete Error Handling
- Try/except wrappers around all critical sections
- Comprehensive data validation
- Graceful degradation on errors
- Detailed error logging with stack traces

### 2. Extensive Logging
Every decision and action is logged:
- Market data retrieval
- Option contract selection
- Premium values (entry and current)
- Order execution
- Position monitoring
- Exit conditions

### 3. Edge Case Handling
- **No 0DTE Available**: Strategy skips entry if no same-day expiration found
- **Strikes Not Found**: Falls back to dynamic strike selection if fixed strikes unavailable
- **Invalid Premiums**: Validates all price data before using
- **Missing Data**: Checks for None/empty data and returns gracefully
- **New Trading Day**: Automatically resets state each day

### 4. Flexible Configuration
All parameters are configurable:
```python
parameters = {
    "symbol": "IWM",
    "num_puts": 10,
    "num_calls_high": 5,
    "num_calls_mid": 5,
    "put_strike_offset": 5,
    "call_strike_high": 191,      # Fixed strike
    "call_strike_mid": 190,        # Fixed strike
    "call_high_offset": 3,         # Dynamic fallback
    "call_mid_offset": 2,          # Dynamic fallback
    "exit_put_premium": 0.02,
    "exit_call_high_premium": 0.15,
    "exit_call_mid_premium": 0.07,
    "entry_time_minutes": 30,
    "check_frequency_minutes": 5,
    "enable_dynamic_strikes": True,
}
```

### 5. State Management
Tracks all critical state across iterations:
- Entry status
- Entry premiums for each position type
- Option contracts (Asset objects)
- Position close status
- Current trading day

### 6. Polygon.io Integration
- Uses PolygonDataBacktesting for accurate historical options data
- Imports credentials from `credentials.py`
- Requires paid Polygon subscription for options backtesting

## Architecture

### Class Structure
```
ZeroDTE_IWM_PremiumCollection(Strategy)
├── initialize()                          # One-time setup
├── on_trading_iteration()                # Main loop (every 5 min)
├── _execute_trading_logic()              # Core logic wrapper
├── _reset_daily_state()                  # Reset for new day
├── _is_within_entry_window()             # Check if can enter
├── _should_close_all_positions()         # Check if must exit
├── _enter_positions()                    # Execute entry orders
├── _monitor_and_exit_positions()         # Check exit conditions
├── _close_position()                     # Close specific position
├── _force_close_all_positions()          # EOD force close
├── _get_0dte_put_contract()              # Find 0DTE put
└── _get_0dte_call_contract()             # Find 0DTE call
```

### Main Logic Flow

```
on_trading_iteration()
│
├─> Check New Trading Day
│   └─> Reset state if new day
│
├─> Get Current Market Data
│   └─> Validate price
│
├─> Check Entry Window
│   └─> Within first 30 min?
│
├─> Entry Logic (if not entered and in window)
│   ├─> Get 0DTE PUT contract
│   ├─> Get 0DTE CALL contracts (high/mid)
│   ├─> Validate all contracts
│   ├─> Get current premiums
│   ├─> SELL PUT options (10 contracts)
│   ├─> SELL CALL options (5 high + 5 mid)
│   └─> Store entry premiums
│
├─> Exit Logic (if positions entered)
│   ├─> Monitor PUT position
│   │   └─> Close if premium <= $0.02
│   ├─> Monitor HIGH CALL position
│   │   └─> Close if premium <= $0.15
│   └─> Monitor MID CALL position
│       └─> Close if premium <= $0.07
│
└─> Force Close (if near EOD)
    └─> Close all positions 15 min before close
```

## Helper Methods Detail

### `_get_0dte_put_contract(current_price)`
1. Gets option chains for IWM
2. Filters for PUT expirations
3. Selects 0DTE expiration (expires today)
4. Gets available strikes
5. Selects strike $5 below current price
6. Creates and returns Asset object

### `_get_0dte_call_contract(current_price, call_type)`
1. Gets option chains for IWM
2. Filters for CALL expirations
3. Selects 0DTE expiration
4. Gets available strikes
5. Selects strike based on type:
   - **"high"**: Uses fixed $191 or dynamic offset (+$3)
   - **"mid"**: Uses fixed $190 or dynamic offset (+$2)
6. Creates and returns Asset object

### `_monitor_and_exit_positions()`
Monitors each position independently:
- Checks current premium vs. entry premium
- Logs premium decay progress
- Closes position when target reached
- Marks position as closed to prevent re-closing

## Usage

### Running Backtest

```python
python C:\Data\Cousin Ingrid\Git Hub\CodeJ\Outputs\Strategies\0dte_iwm_premium_collection.py
```

**Requirements:**
- `IS_BACKTESTING = True` in `credentials.py`
- Valid Polygon API key in `.env`
- Polygon PAID subscription (for options data)

### Customizing Parameters

Edit the `parameters` dict in the backtest section:

```python
parameters={
    "symbol": "IWM",
    "num_puts": 10,              # Adjust position size
    "exit_put_premium": 0.02,    # Adjust exit target
    # ... other parameters
}
```

### Integration with Live Trading

To use for paper/live trading:
1. Set `IS_BACKTESTING = False` in `credentials.py`
2. Configure broker credentials (Tradier or Alpaca)
3. Create strategy instance with broker
4. Run strategy (see Lumibot docs for live trading setup)

## Important Notes

### Options Backtesting
- Requires Polygon.io PAID subscription
- Historical options data necessary for accurate backtesting
- Free tier does NOT include options data

### Risk Warnings
- 0DTE options are highly volatile
- Selling options has unlimited risk (especially calls)
- Strategy assumes no major market moves intraday
- Use appropriate position sizing
- Test thoroughly before live trading

### Performance Considerations
- Checks positions every 5 minutes (configurable)
- Entry window: first 30 minutes after market open
- Auto-closes 15 minutes before market close
- One trading cycle per day (new positions each day)

## Testing & Validation

### Data Validation Checks
- ✓ Validates `get_last_price()` returns valid number
- ✓ Validates option chains are available
- ✓ Validates 0DTE expirations exist
- ✓ Validates strikes are available
- ✓ Validates premiums are valid before entry
- ✓ Validates positions exist before closing

### Error Handling
- ✓ Try/except around entire `on_trading_iteration()`
- ✓ Try/except around each order submission
- ✓ Try/except around contract selection
- ✓ Graceful handling of missing data
- ✓ Detailed logging of all errors with stack traces

### Edge Cases Covered
- ✓ No 0DTE options available
- ✓ Fixed strikes not available (fallback to dynamic)
- ✓ No suitable strikes found
- ✓ Invalid premiums
- ✓ Position already closed
- ✓ New trading day detection
- ✓ Force close before EOD

## File Structure

```
0dte_iwm_premium_collection.py
├── Imports & Configuration
├── Class Definition
│   ├── parameters (dict)
│   ├── initialize()
│   ├── on_trading_iteration()
│   ├── Helper Methods (11 methods)
│   └── Documentation
└── Backtest Execution
    └── __main__ block
```

## Dependencies

```python
from lumibot.strategies import Strategy
from lumibot.entities import Asset
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime, date, time, timedelta
import pandas as pd
import traceback
from credentials import IS_BACKTESTING, POLYGON_CONFIG
```

## Output Files

When running backtest, generates:
- `0dte_iwm_tearsheet.html` - Performance analysis
- Console logs with detailed execution trace

## Next Steps

1. **Test the backtest**: Run with different date ranges
2. **Optimize parameters**: Test different strike offsets and exit targets
3. **Analyze results**: Review tearsheet for performance metrics
4. **Paper trade**: Test in paper trading environment
5. **Risk management**: Add stop-loss and position limits
6. **Live trading**: Deploy with real broker (extreme caution)

## Support

For issues or questions:
- Check Lumibot documentation: https://lumibot.lumiwealth.com/
- Review Polygon.io API docs: https://polygon.io/docs/options
- Verify credentials in `credentials.py`

---

**Generated by**: lumibot-coder agent
**Date**: 2025-01-26
**Version**: 1.0.0
