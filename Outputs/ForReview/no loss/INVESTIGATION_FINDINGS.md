# Zero Loss Butterfly - Investigation Findings

**Date**: 2025-10-26
**Status**: CRITICAL ISSUES FOUND

---

## Executive Summary

Our Zero Loss Butterfly strategy **appears to work** but is actually **completely broken**. All option legs are being canceled, leaving us with an unhedged stock position.

### Critical Findings

❌ **ALL OPTION ORDERS CANCELED** - No butterfly protection exists
❌ **Wrong dates** - Running on 2024-11-01 instead of 2025-08-21
❌ **No Polygon data** - V options data doesn't exist for Aug/Nov 2024 or Aug 2025
✅ **trades.csv exists** - File generation works fine
✅ **Rolling implemented** - Code is correct, just can't execute

---

## Detailed Analysis

### Issue 1: Canceled Option Orders (CRITICAL)

**Evidence from trades.csv**:
```
2024-11-01 09:30:00 | V stock  | buy  | FILLED   | 100 shares @ $288.49
2024-11-01 09:30:00 | V PUT 277.5  | buy  | CANCELED |
2024-11-01 09:30:00 | V CALL 285 x2 | sell | CANCELED |
2024-11-01 09:30:00 | V CALL 295    | buy  | CANCELED |
```

**Root Cause** (from Lumibot source):
```python
# File: backtesting_broker.py, line 801-802
if ohlc is None or ohlc.df.empty:
    self.cancel_order(order)
```

**Why it happens**:
1. Lumibot tries to get price data (OHLC) for each option contract
2. Polygon API has **NO OPTIONS DATA** for V on these dates
3. When Lumibot can't find prices, it cancels the order
4. Stock order fills because stock data exists
5. Result: Naked long stock position with ZERO protection

**Impact**:
- No butterfly protection
- No zero-loss guarantee
- Just holding 100 shares of V unhedged
- Strategy return (2.4%) < benchmark (8%) because we missed the upside

---

### Issue 2: Date Mismatch

**Requested**:
```python
datetime(2025, 8, 21)  # Aug 21, 2025
datetime(2025, 10, 17) # Oct 17, 2025
```

**Actually Ran**:
```
2024-11-01  # Nov 1, 2024
```

**Why this happens**:
- Lumibot's PolygonDataBacktesting doesn't validate or enforce start dates
- It fetches data from Polygon and uses whatever date range Polygon returns
- Polygon likely redirects to "first available date with data"
- Since no V options data exists for Aug 2025, it falls back to Nov 2024
- But even Nov 2024 has no V options data!

**Polygon Data Availability** (tested via fetch_polygon_data.py):
- Aug 21, 2025: ❌ No V options data
- Aug 22, 2025: ❌ No V options data
- Aug 21, 2024: ❌ No V options data
- Aug 22, 2024: ❌ No V options data
- Nov 1, 2024: ❌ No V options data

---

### Issue 3: Why Console Said "Success"

Our code printed:
```
[OK] All 4 legs submitted successfully
[OK] Successfully entered butterfly position
```

**This is misleading!** Our code only checks if orders were **submitted**, not if they were **filled**.

```python
# Line 487 in zero_loss_butterfly.py
self.submit_order(upper_call_order)
print(f"[OK] All 4 legs submitted successfully")
return True  # ← Returns True even if orders get canceled later!
```

**Fix needed**: Check order status after submission.

---

## Why Lumibot's Backtest "Worked"

Even though options failed, the backtest ran because:
1. Stock order filled successfully (V stock data exists)
2. Portfolio grew from $100k → $102.6k (+2.6%)
3. V benchmark grew +8% (we underperformed because naked stock)
4. Tearsheet generated successfully
5. trades.csv shows the truth (canceled orders)

---

## Root Cause: Missing Polygon Options Data

The fundamental problem is **Polygon doesn't have options data for V (Visa)** in the periods we're testing.

### Why might this be?

**Possibility 1**: V might not be available on Polygon's options feed
- Check: Does Polygon even offer V options?
- Action: Test with SPY or QQQ which definitely have options data

**Possibility 2**: Wrong API endpoint
- Our fetcher uses: `/v3/snapshot/options/{ticker}`
- Lumibot might use: Different endpoint (aggregates, quotes, etc.)
- Action: Check what endpoint Lumibot actually uses

**Possibility 3**: Paid subscription required
- Some Polygon data requires paid subscription
- Our POLYGON_CONFIG has a key but might not have right tier
- Action: Verify subscription level

---

## Testing Results

### Test 1: Polygon Direct API (via fetch_polygon_data.py)
```bash
python fetch_polygon_data.py --tickers V --start-date 2025-08-21 --end-date 2025-08-22
Result: 0/2 successful, 2 failed
ERROR: "No valid options records for V on 2025-08-21"
```

### Test 2: Lumibot Backtest (via zero_loss_butterfly.py)
```bash
python test_butterfly_aug_oct_2025.py
Result: Ran on 2024-11-01 (wrong date), all options CANCELED
Portfolio: $100k → $102.6k (naked stock only)
```

### Test 3: trades.csv Analysis
```
Stock: FILLED
PUT: CANCELED
CALL x2: CANCELED
CALL: CANCELED
```

---

## Recommended Solutions

### Solution 1: Use SPY Instead of V (QUICK FIX)

SPY has the most liquid options market and Polygon definitely has data:

```python
parameters = {
    "symbol": "SPY",  # Change from V to SPY
    "shares_per_position": 100,
    ...
}
```

**Pros**: Should work immediately
**Cons**: Not testing the exact video strategy

---

### Solution 2: Check Video Symbol is Actually V

From screenshots:
- Screenshot 1: Shows "V APR15 0LOSS"
- Screenshot 4: Shows V price and payoff diagram
- Screenshot 5: Shows "V Aug29'25 350 CALL"

Video definitely uses V (Visa). But maybe we need to:
- Use correct date range (Apr 15 - Oct 17, not Aug 21 - Oct 17)
- Check if Polygon has Apr-Jul 2025 data for V

---

### Solution 3: Different Data Provider

If Polygon doesn't have V options, try:
- **ThetaData** (Lumibot supports this via `ThetaDataBacktesting`)
- **Interactive Brokers** (via `InteractiveBrokersRestBacktesting`)
- **Custom data** (download from ThinkorSwim, import to Pandas)

---

### Solution 4: Paper Trading Instead of Backtest

If historical data doesn't exist:
1. Run strategy in **paper trading** mode (forward testing)
2. Use current dates (today forward)
3. This would use live Polygon data
4. Slower but would actually test the strategy

---

## Next Steps (Recommended Order)

### Step 1: Test with SPY (5 minutes)
Change symbol to SPY and run backtest. If options fill, we know it's a V-specific data issue.

### Step 2: Test Extended Date Range (10 minutes)
Try Apr 15 - Oct 17, 2025 (6 months) to match video exactly.

### Step 3: Check Lumibot GitHub Issues (10 minutes)
Search for:
- "options canceled"
- "Polygon options data"
- "V ticker"

### Step 4: Add Order Validation (20 minutes)
Update our code to:
```python
def execute_four_leg_entry(...):
    # Submit all orders
    stock_order = self.submit_order(...)

    # Wait for fills
    time.sleep(1)

    # Verify all orders filled
    if stock_order.status != "fill":
        logger.error("Stock order didn't fill!")
        return False

    if put_order.status == "canceled":
        logger.error("PUT order canceled - no data available!")
        return False

    # etc.
```

### Step 5: Create Diagnostic Strategy (30 minutes)
Build a simple strategy that:
1. Checks what options data IS available for V
2. Prints all expirations
3. Prints all strikes
4. Tries to place 1 simple option order
5. Reports why it fails

---

## Files Generated

✅ **trades.csv**: `ZeroLossButterfly_2025-10-26_06-38_lx4hKM_trades.csv`
✅ **tearsheet.csv**: `ZeroLossButterfly_2025-10-26_06-38_lx4hKM_tearsheet.csv`
✅ **tearsheet.html**: `zero_loss_butterfly_tearsheet.html`
✅ **Strategy code**: `zero_loss_butterfly.py` (675 lines, fully implemented)

---

## Conclusion

Our implementation is **technically correct** but **can't execute** due to missing options data for V on Polygon.

**Current State**:
- ✅ Code implements correct butterfly (sell 2 calls at center)
- ✅ Rolling logic fully implemented
- ✅ All files generate properly
- ❌ Can't get options data for V from Polygon
- ❌ All option orders canceled
- ❌ Strategy runs as naked long stock (no protection!)

**Recommended Action**: Test with SPY first, then investigate V-specific data issues.
