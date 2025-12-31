# Bug Fix Summary - Zero Loss Butterfly Strategy

**Date**: 2025-10-26
**Bug ID**: Stock Re-Buying Loop
**Severity**: CRITICAL
**Status**: FIXED

---

## Bug Description

The Zero Loss Butterfly strategy was re-purchasing stock on every iteration when options orders were canceled, leading to:

- **40 stock purchases** instead of 1
- **2,000 shares** accumulated instead of 100
- **-$1,000,000 negative balance**
- **Unreliable backtest results**

### Root Cause

The strategy used a single flag `has_stock_position` to track both stock AND options together. When options were canceled (due to missing Polygon data), the method `has_complete_position()` returned `False`, triggering a full 4-leg re-entry that ALWAYS included buying 100 more shares.

```python
# BUGGY CODE (BEFORE):
def on_trading_iteration(self):
    has_complete_position = self.has_complete_position()  # ← Checks stock + options together

    if not has_complete_position:
        self.enter_butterfly_position()  # ← ALWAYS buys stock again!
```

The strategy never checked: "Do we already OWN the stock?"

---

## Fix Implementation

### 1. Separate State Tracking

Added independent flags to track stock and options separately:

```python
# FIXED CODE:
def initialize(self):
    # Position tracking - CRITICAL: Track stock separately from options!
    self.stock_purchased = False       # Flag: Have we bought the 100 shares? (PERMANENT)
    self.stock_entry_price = None      # Price we paid for stock
    self.has_options_position = False  # Flag: Do we have all 3 option legs?
    self.current_expiration = None
    self.current_strikes = {...}
```

### 2. Updated Entry Logic

Modified `on_trading_iteration()` to check stock ownership first:

```python
def on_trading_iteration(self):
    # STEP 1: Check stock ownership (permanent position)
    if not self.stock_purchased:
        # INITIAL ENTRY: Buy stock + options together
        self.enter_butterfly_position()
        return

    # STEP 2: We have stock, check options
    has_complete_options = self.has_complete_options_position()

    if not has_complete_options:
        # Have stock, but missing options - re-establish options only
        self.establish_options_position()  # ← NEW METHOD: No stock purchase!
        return

    # STEP 3: Complete position - check if we need to roll
    if self.should_roll_position():
        self.roll_butterfly_position()
```

### 3. New Methods Created

**`has_complete_options_position()`** - Checks for 3 option legs only (excludes stock check)

**`establish_options_position()`** - Re-establishes options when stock already owned:
```python
def establish_options_position(self):
    """Establish ONLY the 3 option legs (does NOT buy stock)"""
    # Find expiration, calculate strikes, verify zero-loss structure
    success = self.execute_three_leg_options_entry(...)  # ← No stock!
```

**`execute_three_leg_options_entry()`** - Executes 3 option orders (no stock):
- LEG 1: Buy 1 PUT
- LEG 2: Sell 2 CALLs (center)
- LEG 3: Buy 1 CALL (upper)

### 4. Updated Flag Management

Ensured flags are set correctly after successful operations:

```python
if success:
    self.stock_purchased = True         # Mark stock as purchased
    self.has_options_position = True    # Mark options as established
```

---

## Validation

Created `backtest_validator.py` to prevent this bug in future:

### Validation Checks
1. **Stock Quantity**: Ensures stock bought ONCE (not 40 times)
2. **Balance**: Ensures no negative balance
3. **Butterfly Structure**: Verifies 1 PUT, 2 CALLs, 1 CALL
4. **Options Fill Rate**: Warns about data quality issues

### Test on Buggy Backtest

```
Stock BUY orders: 40                                    ← DETECTED!
Total shares bought: 2000.0                             ← DETECTED!
[FAIL] BUG DETECTED: Stock bought 40 times (should be 1)!
```

**Result**: Validator correctly detected the bug!

---

## Files Modified

### Core Strategy (Fixed)
- `zero_loss_butterfly.py`
  - `initialize()` - Added separate state flags
  - `on_trading_iteration()` - Updated entry logic
  - `enter_butterfly_position()` - Added flag setting
  - `has_complete_options_position()` - NEW METHOD
  - `establish_options_position()` - NEW METHOD
  - `execute_three_leg_options_entry()` - NEW METHOD
  - `roll_butterfly_position()` - Updated flag management

### Validation Tools (New)
- `backtest_validator.py` - NEW FILE
  - Automated sanity checks
  - Detects stock re-buying bug
  - Validates butterfly structure
  - Checks options fill rate

### Test Scripts (Updated)
- `test_spy_2024.py` - Added automatic validation after backtest
- `test_v_2024.py` - Added automatic validation after backtest

---

## Prevention Strategy

This bug could have been prevented by:

### 1. Enhanced Architecture Specification
- Explicitly state: "Buy stock ONCE at initialization, never again"
- Add state management requirements
- Define "initial entry" vs "options-only re-entry"

### 2. Pre-Backtest Validation
- Unit tests for position tracking
- Dry-run tests with mock orders
- Static analysis for re-buying patterns

### 3. Post-Backtest Validation
- Automated sanity checks (now implemented!)
- Trade count analysis
- Balance validation

### 4. Better Logging
- Log decision rationale: "Why am I buying stock?"
- Track state changes: "stock_purchased: False → True"

---

## Next Steps

1. ✅ Bug fixed in `zero_loss_butterfly.py`
2. ✅ Validator created and tested
3. ✅ Test scripts updated with automatic validation
4. ⏳ Run corrected backtest on SPY 2024 data
5. ⏳ Verify stock quantity = 100 (not 2,000!)
6. ⏳ Compare results with buggy backtest
7. ⏳ Document performance metrics

---

## Key Lessons

1. **Separate concerns**: Track stock and options independently
2. **Explicit state**: Use clear boolean flags for ownership
3. **Idempotency**: Operations should be safe to retry
4. **Validation**: Always validate backtest results before trusting them
5. **Root cause first**: Don't just fix symptoms, fix the underlying logic

---

## Related Documentation

- `INVESTIGATION_FINDINGS.md` - Analysis of why backtest failed
- `TESTING_STATUS.md` - Current testing status
- `zero_loss_butterfly_architecture.md` - Strategy specification
- `backtest_validator.py` - Validation tool source code
