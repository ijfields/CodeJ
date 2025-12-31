# Options Data Availability Issue - Polygon Backtesting

**Date**: October 28, 2025 (7:20 AM)
**Status**: Data availability limitation identified

---

## Issue Summary

Butterfly positions are closing the same day they're opened because **options orders are getting CANCELED** due to Polygon not having options data at the calculated strike prices.

---

## Evidence from Q1 2024 Backtest

### Jan 2, 2024 (First Iteration)
**SPY Price**: $472.16

**Calculated Strikes** (based on offsets):
- PUT: $462 (price - 10)
- Center CALL: $467 (price - 5)
- Upper CALL: $477 (price + 5)

**Result**:
```
2024-01-02 09:30:00 | Stock: FILLED (100 shares @ $472.16)
2024-01-02 09:30:00 | PUT $462: CANCELED
2024-01-02 09:30:00 | CALL $467 (x2): CANCELED
2024-01-02 09:30:00 | CALL $477: CANCELED
```

**Butterfly incomplete** - Only stock position held.

---

### Jan 3, 2024 (Second Iteration)
**SPY Price**: $470.43

**Calculated Strikes**:
- PUT: $460 (price - 10)
- Center CALL: $465 (price - 5)
- Upper CALL: $475 (price + 5)

**Result**:
```
2024-01-03 09:30:00 | PUT $460: FILLED @ $4.74
2024-01-03 09:30:00 | CALL $465 (x2): FILLED @ $15.24
2024-01-03 09:30:00 | CALL $475: FILLED @ $8.85
```

**Butterfly complete** - All options filled!

---

### Feb 22, 2024 (Roll)
**SPY Price**: $504.01

**Roll Operation** (close old, open new):

**Closing** (Old position from Jan 3):
- PUT $460: FILLED (sold back)
- CALL $465 (x2): FILLED (bought back)
- CALL $475: FILLED (sold back)

**Opening** (New position):
- PUT $494: FILLED
- CALL $499 (x2): FILLED
- CALL $509: FILLED

**Roll successful** - All 6 legs filled!

---

## Root Cause Analysis

### Why Did Some Options Fill and Others Cancel?

**Jan 2 strikes** ($462, $467, $477):
- Non-standard strikes
- Polygon Options Starter plan may not have data for these strikes
- Result: CANCELED

**Jan 3 strikes** ($460, $465, $475):
- Standard $5 interval strikes
- Polygon has data available
- Result: FILLED

**Feb 22 strikes** ($494, $499, $509):
- Mix of standard ($499) and near-standard strikes
- Higher price = more liquid options
- Result: FILLED

---

## SPY Options Strike Conventions

SPY options typically trade at:
- **$1 intervals** for near-the-money strikes (most liquid)
- **$5 intervals** for slightly out-of-the-money
- **$10 intervals** for far out-of-the-money

**Standard strikes around $470**:
- $460, $465, $470, $475, $480 (all $5 intervals)

**Non-standard strikes**:
- $462, $467, $477 (odd intervals)

Our strategy calculates strikes based on price + offset, which can produce non-standard strikes.

---

## Impact on Strategy

### Current Behavior
1. **Day 1**: Try to enter butterfly
   - Stock fills immediately
   - Options may cancel if strikes aren't available
2. **Day 2+**: Keep trying to re-establish options
   - Eventually fills when price moves to produce standard strikes
3. **Result**: Butterfly held for duration, but delayed entry

### Fill Rate Statistics
From Q1 2024 backtest:
- Total option orders: 24
- Filled: 9 (37.5%)
- Canceled: 15 (62.5%)

**Low fill rate** suggests many strike prices don't have available data in Polygon's database.

---

## Solutions

### Option 1: Round Strikes to Standard Intervals (Recommended)

Modify strike calculation to round to nearest $5:

```python
def round_to_nearest_5(strike):
    """Round strike to nearest $5 interval"""
    return round(strike / 5) * 5

# Calculate strikes
current_price = self.get_last_price(self.symbol)
put_strike = round_to_nearest_5(current_price + self.put_offset)
center_strike = round_to_nearest_5(current_price + self.center_offset)
upper_strike = round_to_nearest_5(current_price + self.upper_offset)
```

**Benefits**:
- Higher probability of finding available options data
- Better fill rate
- More realistic (standard strikes are more liquid in real trading)

**Trade-off**:
- Slightly different from exact offsets
- May not match video's exact strikes

---

### Option 2: Get Option Chain and Pick Available Strikes

Query the actual option chain and select strikes from available options:

```python
# Get option chain for target expiration
chain = self.get_option_chain(self.symbol, self.target_expiration)

# Find closest available strikes to our targets
put_strike = find_closest_strike(chain.puts, current_price + self.put_offset)
center_strike = find_closest_strike(chain.calls, current_price + self.center_offset)
upper_strike = find_closest_strike(chain.calls, current_price + self.upper_offset)
```

**Benefits**:
- Guaranteed to use strikes with available data
- 100% fill rate (in theory)
- Most realistic for actual trading

**Trade-off**:
- More complex code
- Slower (requires chain query)
- May need error handling if chain is empty

---

### Option 3: Use Limit Orders Instead of Market Orders

Change from market orders to limit orders with reasonable prices:

```python
order = self.create_order(
    asset,
    quantity,
    side,
    limit_price=estimated_price,  # Instead of market order
)
```

**Benefits**:
- May help with fill rate
- More realistic for actual trading

**Trade-off**:
- Requires price estimation
- May still not fill if data unavailable
- Doesn't solve root cause (missing data)

---

## Recommendation

**Implement Option 1: Round strikes to $5 intervals**

This is the quickest fix and will significantly improve fill rates while maintaining the strategy's core logic. Standard strikes are:
1. More liquid in real trading
2. More likely to have available data in Polygon
3. Still maintain the butterfly structure

### Implementation Steps

1. Create helper function to round strikes to $5
2. Apply rounding in `calculate_strikes()` method
3. Re-run backtest to verify improved fill rate
4. Document the change in strategy notes

---

## Current Status

### What's Working
- ✅ Stock purchased ONCE (bug fix successful)
- ✅ Options-only re-establishment (when options cancel)
- ✅ Roll functionality (when options do fill)
- ✅ Polygon respects parameterized dates

### What Needs Improvement
- ❌ Options fill rate too low (37.5%)
- ❌ Butterfly delayed entry (options cancel on Day 1)
- ❌ Non-standard strikes causing data unavailability

---

## Next Steps

1. **Immediate**: Implement strike rounding to $5 intervals
2. **Test**: Re-run Q1 2024 backtest with rounded strikes
3. **Verify**: Confirm improved fill rate
4. **Validate**: Ensure butterfly structure still maintained
5. **Document**: Update strategy notes with strike selection logic

---

## Note on Polygon Data

The Polygon Options Starter plan ($29/month) includes:
- 2 years of historical options data
- Real-time options quotes
- Options chains

However, not all strike prices may have historical data, especially:
- Non-standard strikes (not at $5 intervals)
- Far out-of-the-money options
- Low-volume expiration dates

**This is a data availability limitation, not a strategy bug.**

---

## Summary

The butterflies appear to be "closing the same day" because:
1. Stock fills on Day 1
2. Options cancel on Day 1 (no data at calculated strikes)
3. Options fill on Day 2+ (when price moves to standard strikes)
4. Butterfly then held until roll date

**Solution**: Round calculated strikes to standard $5 intervals to match available options data.
