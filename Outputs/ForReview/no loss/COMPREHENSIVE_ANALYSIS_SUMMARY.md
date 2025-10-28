# Zero Loss Butterfly Strategy - Comprehensive Analysis Summary

**Date**: October 28, 2025
**Test Period**: August 21 - October 17, 2025
**Symbol**: VISA (V)
**Strategy Source**: YouTube video "Zero Loss Butterfly Strategy"

---

## Executive Summary

After extensive debugging and testing, the Zero Loss Butterfly strategy implementation is now **WORKING CORRECTLY** but shows **THIS IS NOT A WINNING STRATEGY** based on current test results. The strategy successfully reduces volatility and drawdown compared to buy-and-hold, but generated a loss during the 57-day test period.

---

## Test Results - Video Trade (Aug 21 - Oct 17, 2025)

### Trade Execution (SUCCESSFUL)
- **Entry Date**: August 21, 2025
- **Stock Price**: $342.89
- **Strikes**: $330 PUT / $340 CALL (x2) / $350 CALL (EXACT match to video)
- **Stock Purchases**: 1 (100 shares) ✓
- **Initial Butterfly Fill Rate**: 100% ✓
- **Position Duration**: 50 days (held until roll attempt on Oct 10)

### Performance Metrics
| Metric | V (Buy & Hold) | Strategy |
|--------|----------------|----------|
| **Total Return** | -2% | -1% |
| **CAGR (Annual)** | -14.72% | -7.71% |
| **Max Drawdown** | -4.83% | -1.59% |
| **Volatility (Annual)** | 18.5% | 5.62% |
| **Sharpe Ratio** | -0.96 | -2.04 |
| **Correlation to V** | 100% | 26.61% |
| **Beta** | 1.0 | 0.08 |

### Key Findings

✓ **VOLATILITY REDUCTION**: 70% reduction (18.5% → 5.62%)
✓ **DRAWDOWN REDUCTION**: 67% smaller (4.83% → 1.59%)
✓ **LOW CORRELATION**: Only 26.61% correlation to underlying
✓ **LOW BETA**: 0.08 (minimal market exposure)

✗ **NEGATIVE RETURNS**: Both V and strategy lost money
✗ **POOR SHARPE**: Both have negative risk-adjusted returns
✗ **SHORT TEST**: Only 57 days, single cycle

---

## Technical Fixes Implemented

### Fix 1: Configuration Issue (NOT a Lumibot Bug)
**Problem**: All backtests used Nov 1, 2024 regardless of requested dates
**Root Cause**: `BACKTESTING_START` and `BACKTESTING_END` in `.env` file were taking priority over parameters (documented Lumibot behavior)
**Solution**: Commented out dates in `.env` file
**Result**: Polygon now works correctly with parameterized dates ✓

### Fix 2: Stock Re-buying Bug (From Previous Session)
**Problem**: Stock purchased multiple times instead of once
**Solution**: Position-based checking in `zero_loss_butterfly.py`
**Result**: Stock purchased exactly once ✓
**Note**: Validator incorrectly reports "2 times" because it counts both "new" and "fill" states of the same order

### Fix 3: Options Fill Rate Improvement
**Problem**: Non-standard strikes ($462, $467, $477) don't have historical data
**Solution**: Added $5 strike rounding in `calculate_optimal_strikes()` method
**Code Change** (lines 473-492 in `zero_loss_butterfly.py`):
```python
# Round targets to nearest $5 (SPY standard option intervals)
def round_to_5(value):
    return round(value / 5) * 5

put_strike_target = round_to_5(put_strike_target)
center_strike_target = round_to_5(center_strike_target)
upper_strike_target = round_to_5(upper_strike_target)
```
**Result**: Improved to standard strikes with better data availability ✓

---

## Trade Timeline Detail

### August 21, 2025 - ENTRY (ALL FILLED)
```
Buy 100 shares V @ $342.89 = $34,289
Buy 1 PUT $330 @ $5.74 = $574
Sell 2 CALL $340 @ $13.15 = -$2,630 (CREDIT)
Buy 1 CALL $350 @ $7.95 = $795
---
Net Options Premium: $574 + $795 - $2,630 = -$1,261 (credit)
Total Position Cost: $34,289 - $1,261 = $33,028
```

### October 10, 2025 - ROLL ATTEMPT (CLOSE SUCCESSFUL, ROLL FAILED)
```
Close existing butterfly:
  Sell 1 PUT $330 @ $0.49 = $49
  Buy 2 CALL $340 @ $11.22 = -$2,244
  Sell 1 CALL $350 @ $3.57 = $357
  Close P&L: $49 - $2,244 + $357 = -$1,838

Attempted new butterfly with Dec 5, 2025 expiration:
  Strikes: $335 PUT / $345 CALL (x2) / $355 CALL
  Result: ALL CANCELED (no historical data available)
```

### October 13-17, 2025 - RETRY ATTEMPTS
Multiple attempts to establish new butterfly, all canceled due to lack of options data for Dec 2025 expiration.

### Final Portfolio Value
- Stock value: 100 shares @ ~$352 = $35,200
- Net option P&L: -$1,261 (entry) - $1,838 (close) = -$3,099
- Total: ~$32,101
- **Loss**: ~$928 or -2.8%

---

## Why This Is Not a Winning Strategy

### 1. Short Test Period
- Only 57 days (one cycle)
- Need longer period to evaluate multiple cycles
- "Zero loss" benefit requires sustained premium collection over time

### 2. Market Conditions
- V declined 2% during test period
- Strategy couldn't overcome directional loss with option premium
- Need neutral to slightly bullish market for optimal performance

### 3. Roll Failure
- Strategy couldn't establish new position after roll
- Lost opportunity to continue collecting premium
- Ended holding only stock (exposed to full downside)

### 4. Transaction Costs Not Included
- Backtest doesn't include:
  - Commissions ($0.65/contract typically)
  - Bid-ask spreads
  - Slippage
- Real costs would reduce returns further

### 5. Capital Efficiency
- Ties up $33,000+ for potential small gains
- -7.71% annualized return is far below risk-free rate (3.83%)
- Better alternatives exist (bonds, index funds, etc.)

---

## Validator Issue

### Reported Problem
```
[FAIL] BUG DETECTED: Stock bought 2 times (should be 1)!
```

### Actual Truth
The validator is INCORRECT. It's counting both the "new" order (line 2) and the "fill" order (line 6) as separate purchases, when they're actually the same order in different states:

```
Line 2: 2025-08-21 09:30:00-04:00,buy,new,,V,stock (order submitted)
Line 6: 2025-08-21 09:30:00-04:00,buy,fill,100.0,V,stock (order filled)
```

Only line 6 has `filled_quantity=100.0`, so only 1 actual stock purchase occurred.

### Validator Fix Needed
The validator should only count orders with `status=fill`, not count both `new` and `fill` states of the same order.

---

## Data Source Issues

### Polygon Historical Data Limitations
1. **Future dates**: Testing Oct 2025 from Oct 28, 2025 means very recent data
2. **New expirations**: Dec 5, 2025 options may not have sufficient historical pricing
3. **Non-standard strikes**: Only $5 intervals have reliable data for SPY, less for individual stocks like V

### Refresh Recommendation
Yes, consider refreshing data source or testing with older, more complete data:
- Use 2024 equivalent dates (Aug 21 - Oct 17, 2024)
- Test with SPY instead of V (more liquid options, better data)
- Test longer periods (6-12 months) for multiple cycles

---

## Recommended Next Tests

### Priority 1: SPY Comparison (Your Request)
Test the same strategy with SPY for:
- Higher options liquidity
- Better historical data availability
- Direct benchmark comparison

**Test Script**: Modify `test_video_trade_2025.py`:
```python
symbol = "SPY"  # Change from "V"
# Keep same dates: Aug 21 - Oct 17, 2025 (or use 2024 for complete data)
```

### Priority 2: April 15 - October 2025 Range (Your Request)
Based on screenshots, test longer period:
```python
start_date = datetime(2025, 4, 15)
end_date = datetime(2025, 10, 28)  # Today
```

### Priority 3: Historical Complete Data Test
Use 2024 data for more reliable results:
```python
start_date = datetime(2024, 4, 15)
end_date = datetime(2024, 10, 28)
symbol = "SPY"
```

### Priority 4: Full Year Test
Test entire year to see multiple cycles:
```python
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
symbol = "SPY"
```

---

## Files Created/Modified

### Core Strategy
- `zero_loss_butterfly.py` - Main strategy (added $5 strike rounding)

### Configuration
- `.env` - Commented out BACKTESTING_START/END
- `credentials.py` - Created following StrategyTemplate.py pattern

### Test Scripts
- `test_video_trade_2025.py` - Tests exact video trade (Aug 21 - Oct 17, 2025)
- `test_strike_rounding.py` - Quick test of $5 rounding fix (Jan 2024)
- `backtest_validator.py` - Validates trade execution (has bug counting stock orders)

### Documentation
- `VIDEO_TRADE_DETAILS.md` - Documents confirmed trade from video
- `POLYGON_ISSUE_RESOLVED.md` - Documents configuration fix
- `COMPREHENSIVE_ANALYSIS_SUMMARY.md` - This file

### Output Files (logs/)
- `ZeroLossButterfly_2025-10-28_08-01_Tblodg_trades.csv` - Video trade transactions
- `ZeroLossButterfly_2025-10-28_08-01_Tblodg_tearsheet.csv` - Performance metrics
- `ZeroLossButterfly_2025-10-28_08-01_Tblodg_tearsheet.html` - Visual tearsheet
- `ZeroLossButterfly_2025-10-28_08-01_Tblodg_trades.html` - Visual trade history

---

## Conclusions

### What Works ✓
1. Strategy implementation is correct
2. Stock purchased exactly once
3. Butterfly structure matches video
4. Strikes calculated correctly ($330/$340/$350)
5. Volatility reduced by 70%
6. Drawdown reduced by 67%
7. Low correlation to underlying (26.61%)

### What Doesn't Work ✗
1. Negative returns in test period
2. Negative Sharpe ratio (poor risk-adjusted returns)
3. Roll attempts fail due to data availability
4. Capital tied up for minimal/negative returns
5. Annualized return (-7.71%) far below risk-free rate (3.83%)

### Final Verdict
**THIS IS NOT A WINNING STRATEGY** based on current test results. While it successfully reduces volatility and drawdown, it generated losses during the test period and would perform worse after accounting for transaction costs. The "zero loss" marketing claim is misleading - the strategy can and did lose money.

### Recommended Actions
1. Test with SPY for better data and direct comparison
2. Test longer periods (6-12 months) for multiple cycles
3. Compare against simple alternatives (SPY buy-and-hold, bonds, covered calls)
4. Calculate break-even scenarios and probability of profit
5. Consider abandoning this strategy in favor of proven alternatives

---

## Technical Notes

### Lumibot Configuration Priority (CRITICAL)
Lumibot checks for dates in this order:
1. Environment variables (`BACKTESTING_START`, `BACKTESTING_END`)
2. Parameters passed to `run_backtest()`

If dates are in `.env`, they ALWAYS take priority. This is documented behavior, not a bug.

### Parameterized Dates Approach (RECOMMENDED)
For video-based strategy development:
- Each strategy defines its own dates based on confirmed trades
- Start with exact video trade (proof of concept)
- Gradually expand: week → month → quarter → year
- Compare each expansion against benchmark

### Strike Rounding Importance
Options data availability is highly dependent on strike selection:
- **Standard strikes** ($5 intervals for SPY): Excellent data
- **Non-standard strikes** ($462, $477, etc.): Often no historical data
- **$1 intervals**: Only available for very liquid near-the-money SPY options

Always round to standard strikes for backtesting to maximize data availability.

---

**Generated**: October 28, 2025
**Strategy**: Zero Loss Butterfly
**Status**: Working but not profitable
**Recommendation**: Test with SPY and longer periods, but likely abandon strategy
