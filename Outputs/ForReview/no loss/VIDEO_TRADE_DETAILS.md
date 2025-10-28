# Zero Loss Butterfly - Video Trade Details

**Video Source**: "Zero Loss Butterfly Strategy" YouTube video
**Strategy**: Zero Loss Butterfly (Stock + Married Put + Call Butterfly)

---

## Confirmed Trade from Video

### Trade Date and Symbol
- **Entry Date**: August 21, 2025
- **Symbol**: VISA (V)
- **Stock Price at Entry**: ~$343
- **Expiration**: October 17, 2025 (57 DTE)

### The 4-Leg Structure

**LEG 1: Buy 100 shares of VISA**
- Quantity: 100 shares
- Price: ~$343/share
- Cost: ~$34,300

**LEG 2: Buy 1x PUT @ $330** (Married Put / Floor Protection)
- Strike: $330
- Type: PUT
- Quantity: 1 contract (100 shares)
- Purpose: Protective floor - guarantees minimum recovery of $33,000

**LEG 3: Sell 2x CALL @ $340** (Short Calls - Income Generation)
- Strike: $340 (slightly below stock price)
- Type: CALL
- Quantity: 2 contracts (200 shares) - **KEY: Short 2 contracts**
- Purpose: Generate premium income to offset costs

**LEG 4: Buy 1x CALL @ $350** (Long Call - Cap Protection)
- Strike: $350
- Type: CALL
- Quantity: 1 contract (100 shares)
- Purpose: Cap losses if stock rises above short call strikes

---

## Strike Selection Logic

**Stock Price**: $343

**Strikes**:
- PUT: $330 ($13 below stock = 3.8% OTM)
- Center CALL: $340 ($3 below stock = 0.9% OTM / Near ATM)
- Upper CALL: $350 ($7 above stock = 2.0% OTM)

**Butterfly Width**: $10 on each side ($330 PUT → $340 → $350)

**Structure**:
- PUT protects downside to $330
- Stock at $343 is between PUT ($330) and short CALLs ($340)
- Short CALLs generate premium
- Long CALL caps risk above $350

---

## Zero-Loss Guarantee

**Floor Protection**:
- Stock cost: $34,300
- PUT guarantees recovery of: $33,000 (strike × 100)
- Maximum stock loss: $1,300

**Premium from Butterfly**:
- Sell 2x $340 CALLs: High premium (ATM/slightly OTM)
- Buy 1x $330 PUT: Moderate cost (OTM)
- Buy 1x $350 CALL: Low cost (OTM)
- **Net credit estimated**: $1,300+

**Zero-Loss Math**:
- Stock max loss: $1,300
- Option net credit: $1,300+
- **Total risk**: $0 (or small profit even in worst case)

---

## Test Date Ranges

### 1. Match Confirmed Trade (Highest Priority)
```python
# Test the exact period from video
backtesting_start = datetime(2025, 8, 21)  # Entry date
backtesting_end = datetime(2025, 10, 17)   # Expiration
symbol = "V"  # VISA
```

**Expected Results**:
- Entry on Aug 21, 2025
- Position held through Oct 17, 2025
- Expiration handling on Oct 17
- Approximate DTE: 57 days

### 2. Extended Test (Lower Priority)
```python
# Test longer period to see multiple cycles
backtesting_start = datetime(2025, 8, 1)   # Full month before
backtesting_end = datetime(2025, 11, 30)   # Month after expiration
symbol = "V"
```

### 3. Historical Data Test (Alternative)
Since Oct 2025 is in the FUTURE (today is Oct 28, 2025), we can't test the actual video trade yet.

**Alternative historical period**:
```python
# Use 2024 data with same structure
backtesting_start = datetime(2024, 8, 21)
backtesting_end = datetime(2024, 10, 17)
symbol = "V"  # or "SPY" for more liquidity
```

---

## Strategy Parameters for Video Trade

```python
strategy_params = {
    "symbol": "V",               # VISA
    "shares_per_position": 100,
    "dte_target": 57,            # Target ~57 days (Aug 21 → Oct 17)
    "dte_min": 50,               # Allow 50-65 DTE range
    "dte_max": 65,
    "strike_width": 10,          # $10 between strikes
    "put_offset": -13,           # PUT $13 below stock ($330 vs $343)
    "center_offset": -3,         # Center $3 below stock ($340 vs $343)
    "upper_offset": 7,           # Upper $7 above stock ($350 vs $343)
    "roll_days_before_exp": 7,
    "check_frequency": "1D",
    "max_cost_vs_protection": 1.0,
}
```

**With $5 Strike Rounding** (for backtesting):
```python
# These offsets will round to standard $5 strikes
# At $343: $330 PUT, $340 CALL, $350 CALL
# All are standard strikes with good data availability
```

---

## Screenshots Available

Located in: `Outputs\ForReview\no loss\screenshots\`

1. Screenshot 2025-10-26 064257.png
2. Screenshot 2025-10-26 064429.png
3. Screenshot 2025-10-26 064450.png
4. Screenshot 2025-10-26 064616.png
5. Screenshot 2025-10-26 064700.png - Shows "V Aug29'25 350 CALL"
6. Screenshot 2025-10-26 065118.png
7. Screenshot 2025-10-26 065159.png

---

## Key Differences from Standard Butterfly

**Standard Call Butterfly**:
- Buy 1x low CALL
- Sell 2x middle CALL
- Buy 1x high CALL
- All calls, no stock

**Zero-Loss (Stock + Married Put + Call Butterfly)**:
1. **Buy 100 shares** - Core position
2. **Buy 1x PUT** - Changes bottom wing from CALL to PUT (floor protection)
3. **Sell 2x CALL** - Same as standard (income)
4. **Buy 1x CALL** - Same as standard (cap risk)

**Key Innovation**:
- PUT at $330 guarantees minimum $33,000 recovery
- Premium from selling 2 CALLs offsets the difference
- Result: No net risk, potential for profit

---

## Testing Priority

### Priority 1: Match Video Trade (2024 Data)
```python
# Can't test 2025 yet, use 2024 equivalent
backtesting_start = datetime(2024, 8, 21)
backtesting_end = datetime(2024, 10, 17)
symbol = "V"
```

### Priority 2: Test with SPY (More Liquid)
```python
# Same dates, more liquid options
backtesting_start = datetime(2024, 8, 21)
backtesting_end = datetime(2024, 10, 17)
symbol = "SPY"
```

### Priority 3: Longer Historical Period
```python
# Test Q3 2024 (3 months)
backtesting_start = datetime(2024, 7, 1)
backtesting_end = datetime(2024, 9, 30)
symbol = "SPY"
```

---

## Expected Backtest Validation

When testing the video trade equivalent:

**Stock Purchases**: Should be 1 (not 40+)
**Options Fill Rate**: Should be high (>80%) with $5 rounding
**Butterfly Structure**: 1 PUT + 2 short CALLs + 1 long CALL
**Position Duration**: Held from entry through expiration
**Zero-Loss Result**: Final P&L should be positive or near $0

---

## Summary

**Video Trade**:
- Date: Aug 21, 2025
- Symbol: VISA (V) @ $343
- Expiration: Oct 17, 2025
- Strikes: $330 PUT / $340 CALL (x2) / $350 CALL
- Structure: Stock + Married Put + Call Butterfly
- Result: Zero loss guarantee with profit potential

**For Backtesting**:
- Use 2024 equivalent dates (Aug 21 - Oct 17, 2024)
- Test with V or SPY
- Apply $5 strike rounding for better fills
- Validate structure matches video
