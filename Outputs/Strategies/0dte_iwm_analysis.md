# 0DTE IWM Options Strategy - Detailed Lumibot Specification

**Analysis Date**: 2025-10-26
**Strategy Type**: Zero-Day-To-Expiration (0DTE) Options Premium Collection
**Asset**: IWM (iShares Russell 2000 ETF)
**Data Provider**: Polygon.io
**Complexity**: Moderate
**Risk Level**: High (naked options selling)

---

## Executive Summary

This strategy sells out-of-the-money (OTM) PUT and CALL options on IWM with same-day expiration (0DTE). The goal is to collect premium by selling options that expire worthless or can be bought back at a fraction of the entry price.

**Core Mechanics:**
- Sell 10 PUT contracts at ~$183 strike (OTM)
- Sell 5 CALL contracts at ~$191 strike (OTM)
- Sell 5 CALL contracts at ~$190 strike (OTM)
- Enter within 30 minutes of market open
- Exit when premium decays to specific thresholds

---

## Strategy Classification

| Attribute | Value |
|-----------|-------|
| **Type** | Multi-leg Options (Premium Collection) |
| **Timeframe** | Intraday (0DTE = same-day expiration only) |
| **Execution Frequency** | Daily (check every 15-30 minutes) |
| **Complexity** | Moderate (multiple option legs) |
| **Risk Level** | High (unlimited risk on naked calls/puts) |
| **Capital Required** | High (margin requirements for naked options) |
| **Backtesting Data Source** | PolygonDataBacktesting (requires paid subscription) |

---

## Entry Conditions - Detailed Specification

### Timing Requirement

**Rule**: Enter trades within 30 minutes of market open

**Lumibot Implementation:**
```python
from datetime import datetime, time, timedelta

def on_trading_iteration(self):
    current_time = self.get_datetime()
    market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    entry_window_end = market_open + timedelta(minutes=30)

    # Only enter if within 30-minute window and no existing positions
    if market_open <= current_time <= entry_window_end:
        if not self._has_positions():
            self._enter_positions()
```

**Method Used:** `self.get_datetime()` - Returns current datetime in backtest or live

### Strike Selection Logic

**Challenge**: Strategy specifies approximate strikes (~$183, ~$190, ~$191) but needs dynamic selection based on current IWM price.

#### Method 1: Fixed Dollar Offset (Recommended)

**PUT Strike (~$183):**
- Calculate offset from current price
- Find closest available strike below offset

**CALL Strikes (~$190, ~$191):**
- Calculate offsets from current price
- Find two closest available strikes above offset

**Implementation:**
```python
def _select_put_strike(self, chains, expiry, current_price):
    """
    Select PUT strike approximately $183
    Dynamically adjust based on current IWM price

    Logic: If IWM ~$187, then $183 is ~$4 below
    Use 2-3% OTM as approximation
    """
    strikes = chains.strikes(expiry, "PUT")

    # Calculate target (e.g., 2% below current price)
    target_strike = current_price * 0.98  # 2% OTM

    # Find closest strike below target
    otm_strikes = [s for s in strikes if s <= target_strike]
    if not otm_strikes:
        return None

    return max(otm_strikes)  # Highest strike below target

def _select_call_strikes(self, chains, expiry, current_price):
    """
    Select two CALL strikes approximately $190 and $191

    Logic: If IWM ~$187, then $190 is ~$3 above, $191 is ~$4 above
    Use strikes 1.5-2% OTM
    """
    strikes = chains.strikes(expiry, "CALL")

    # Target 1: ~1.5% above current price
    target1 = current_price * 1.015
    # Target 2: ~2% above current price
    target2 = current_price * 1.02

    otm_strikes = sorted([s for s in strikes if s >= current_price])

    # Find two closest strikes
    strike1 = min(otm_strikes, key=lambda x: abs(x - target1)) if otm_strikes else None
    strike2 = min(otm_strikes, key=lambda x: abs(x - target2)) if otm_strikes else None

    return (strike1, strike2)  # Returns tuple of two strikes
```

#### Method 2: Absolute Strike Selection (Alternative)

If the strategy **always** uses specific strikes regardless of IWM price:

```python
def _get_fixed_strike(self, chains, expiry, option_type, target_strike):
    """
    Try to find exact strike (e.g., 183, 190, 191)
    If not available, find closest available strike
    """
    strikes = chains.strikes(expiry, option_type)

    # Try exact match first
    if target_strike in strikes:
        return target_strike

    # Find closest available strike
    return min(strikes, key=lambda x: abs(x - target_strike))
```

**Recommended Approach**: Use Method 1 (Fixed Dollar Offset) with dynamic adjustment based on IWM price, as fixed strikes may not be available or may not be appropriately OTM.

### 0DTE Expiration Filtering

**Rule**: Only trade options expiring TODAY (same trading day)

**Lumibot Implementation:**
```python
from datetime import date

def _get_0dte_expiration(self, chains, option_type):
    """
    Filter option chains for 0DTE (zero-day-to-expiration)
    Returns today's expiration date or None
    """
    expiries = chains.expirations(option_type)  # Get all expirations
    today = date.today()

    # Filter for exact match with today
    dte_0 = [exp for exp in expiries if exp == today]

    if not dte_0:
        self.log_message(f"No 0DTE {option_type} options available for {today}")
        return None

    return dte_0[0]  # Return today's date
```

**Important**: On backtesting, `date.today()` will return the current backtest date, ensuring proper 0DTE filtering.

### Complete Entry Logic

**Implementation:**
```python
def _enter_positions(self):
    """
    Execute all three option legs:
    - 10 PUT contracts at ~$183 strike
    - 5 CALL contracts at ~$191 strike
    - 5 CALL contracts at ~$190 strike
    """
    from lumibot.entities import Asset

    # Get current IWM price
    current_price = self.get_last_price("IWM")
    if current_price is None:
        return

    # Get option chains
    chains = self.get_chains(Asset("IWM"))
    if chains is None:
        self.log_message("No option chains available")
        return

    # Get 0DTE expiration for PUTs
    put_expiry = self._get_0dte_expiration(chains, "PUT")
    if put_expiry is None:
        return

    # Get 0DTE expiration for CALLs
    call_expiry = self._get_0dte_expiration(chains, "CALL")
    if call_expiry is None:
        return

    # Select strikes
    put_strike = self._select_put_strike(chains, put_expiry, current_price)
    call_strike1, call_strike2 = self._select_call_strikes(chains, call_expiry, current_price)

    if put_strike is None or call_strike1 is None or call_strike2 is None:
        self.log_message("Could not find appropriate strikes")
        return

    # Create Asset objects for options
    put_option = Asset(
        symbol="IWM",
        asset_type=Asset.AssetType.OPTION,
        expiration=put_expiry,
        strike=put_strike,
        right=Asset.OptionRight.PUT
    )

    call_option_1 = Asset(
        symbol="IWM",
        asset_type=Asset.AssetType.OPTION,
        expiration=call_expiry,
        strike=call_strike1,  # Lower strike (~$190)
        right=Asset.OptionRight.CALL
    )

    call_option_2 = Asset(
        symbol="IWM",
        asset_type=Asset.AssetType.OPTION,
        expiration=call_expiry,
        strike=call_strike2,  # Higher strike (~$191)
        right=Asset.OptionRight.CALL
    )

    # Store entry premiums for exit logic
    self.entry_premium_put = self.get_last_price(put_option)
    self.entry_premium_call1 = self.get_last_price(call_option_1)
    self.entry_premium_call2 = self.get_last_price(call_option_2)

    # Create and submit orders (SELL to open)
    put_order = self.create_order(put_option, 10, side="sell")
    call_order_1 = self.create_order(call_option_1, 5, side="sell")
    call_order_2 = self.create_order(call_option_2, 5, side="sell")

    self.submit_order(put_order)
    self.submit_order(call_order_1)
    self.submit_order(call_order_2)

    self.log_message(f"ENTRY: Sold 10 PUTs @ ${put_strike}, 5 CALLs @ ${call_strike1}, 5 CALLs @ ${call_strike2}")
```

---

## Exit Conditions - Detailed Specification

### Premium Decay Thresholds

**Rule**: Buy back options when premium falls to specific levels

| Option Type | Contracts | Exit Premium |
|-------------|-----------|--------------|
| PUT @ ~$183 | 10 | $0.02 or less |
| CALL @ ~$191 | 5 | $0.15 or less |
| CALL @ ~$190 | 5 | $0.07 or less |

**Logic**: These are absolute premium values, not percentages of entry premium.

### Exit Implementation

**Approach 1: Individual Leg Management** (Recommended)

Each option leg exits independently when its premium threshold is reached:

```python
def _check_exits(self):
    """
    Check each option position for exit conditions
    Exit each leg independently when premium decays to threshold
    """
    positions = self.get_positions()

    for position in positions:
        asset = position.asset

        # Only process option positions
        if asset.asset_type != Asset.AssetType.OPTION:
            continue

        current_premium = self.get_last_price(asset)
        if current_premium is None:
            continue

        # Determine exit threshold based on strike and option type
        exit_threshold = self._get_exit_threshold(asset)

        # Exit if premium at or below threshold
        if current_premium <= exit_threshold:
            # Create BUY order to close (buying back sold options)
            close_order = self.create_order(
                asset,
                position.quantity,
                side="buy"
            )
            self.submit_order(close_order)

            self.log_message(
                f"EXIT: Bought back {position.quantity} {asset.right} "
                f"@ ${asset.strike} for ${current_premium:.2f}"
            )

def _get_exit_threshold(self, option_asset):
    """
    Return exit premium threshold based on option characteristics

    Logic:
    - PUT options: exit at $0.02
    - CALL options at higher strike (~$191): exit at $0.15
    - CALL options at lower strike (~$190): exit at $0.07
    """
    if option_asset.right == Asset.OptionRight.PUT:
        return 0.02

    elif option_asset.right == Asset.OptionRight.CALL:
        # Distinguish between two CALL strikes
        # Assumption: Higher strike = higher exit threshold

        # Get both CALL strikes from stored values
        if hasattr(self, 'call_strike_high') and hasattr(self, 'call_strike_low'):
            if option_asset.strike == self.call_strike_high:
                return 0.15  # Higher strike (~$191)
            elif option_asset.strike == self.call_strike_low:
                return 0.07  # Lower strike (~$190)

        # Fallback: use average threshold
        return 0.11

    return 0.05  # Default fallback
```

**Approach 2: All-or-Nothing Exit** (Alternative)

Exit all positions only when ALL legs reach their thresholds:

```python
def _check_all_or_nothing_exit(self):
    """
    Exit all positions only when all legs meet exit criteria
    More conservative approach
    """
    positions = self.get_positions()
    all_ready_to_exit = True

    for position in positions:
        current_premium = self.get_last_price(position.asset)
        threshold = self._get_exit_threshold(position.asset)

        if current_premium > threshold:
            all_ready_to_exit = False
            break

    if all_ready_to_exit:
        self.sell_all()  # Close all positions
        self.log_message("EXIT: All legs reached thresholds")
```

**Recommendation**: Use **Approach 1** (Individual Leg Management) for more flexibility and earlier profit-taking on legs that decay faster.

### End-of-Day Exit

**Rule**: Close all positions before market close to avoid assignment risk

```python
def before_market_closes(self):
    """
    Force close all positions before market close
    Critical for 0DTE options to avoid assignment
    """
    positions = self.get_positions()

    if positions:
        self.log_message("Closing all positions before market close (0DTE)")
        self.sell_all()
```

**Set in initialize():**
```python
def initialize(self):
    self.sleeptime = "15M"  # Check every 15 minutes
    self.minutes_before_closing = 5  # Close positions 5 min before market close
```

---

## Position Sizing

| Leg | Option Type | Strike | Contracts |
|-----|-------------|--------|-----------|
| 1 | PUT | ~$183 | 10 |
| 2 | CALL | ~$191 | 5 |
| 3 | CALL | ~$190 | 5 |

**Total**: 20 contracts (10 PUTs + 10 CALLs)

**Risk Considerations:**
- Each option contract = 100 shares of IWM
- Naked PUT risk: If IWM drops below $183, potential loss = ($183 - final price) × 100 × 10 contracts
- Naked CALL risk: Unlimited if IWM rallies sharply above $190-191
- **Margin Requirements**: Substantial margin required for naked options (broker-dependent)

**Capital Requirements** (Estimate):
- Naked PUT margin: ~20% of underlying value per contract
- Naked CALL margin: ~20% of underlying value per contract
- Assuming IWM = $187, each contract ≈ $18,700 underlying value
- Margin per PUT: ~$3,740 × 10 = $37,400
- Margin per CALL: ~$3,740 × 10 = $37,400
- **Total Estimated Margin**: ~$75,000

**Note**: Actual margin varies by broker and account type (Portfolio Margin vs. Reg-T).

---

## Lumibot Methods Required

### Core Methods

1. **`self.get_datetime()`**
   - Get current datetime (backtest or live)
   - Used for: Entry timing (within 30 min of open)

2. **`self.get_last_price(asset)`**
   - Get current price of underlying or option
   - Used for: Strike selection, premium monitoring, exit conditions

3. **`self.get_chains(Asset("IWM"))`**
   - Get option chain data
   - Returns: Chains object with expirations and strikes
   - Used for: Finding 0DTE options, available strikes

4. **`chains.expirations(option_type)`**
   - Get list of expiration dates
   - Parameters: "CALL" or "PUT"
   - Returns: List of datetime.date objects

5. **`chains.strikes(expiration, option_type)`**
   - Get list of strike prices for an expiration
   - Parameters: expiration date, "CALL" or "PUT"
   - Returns: List of float values

6. **`self.create_order(asset, quantity, side)`**
   - Create order object (doesn't execute)
   - Parameters:
     - asset: Asset object (for options)
     - quantity: Number of contracts (int)
     - side: "buy" or "sell" (REQUIRED)

7. **`self.submit_order(order)`**
   - Execute order
   - Parameters: Order object from create_order()

8. **`self.get_positions()`**
   - Get all current positions
   - Returns: List of Position objects

9. **`self.get_position(asset)`**
   - Get position for specific asset
   - Returns: Position object or None

10. **`self.sell_all()`**
    - Close all positions immediately
    - Used for: End-of-day exits

11. **`self.log_message(msg)`**
    - Log messages to strategy output
    - Used for: Debugging and trade tracking

### Asset Creation (Options-Specific)

```python
from lumibot.entities import Asset
from datetime import date

option = Asset(
    symbol="IWM",                        # Underlying symbol
    asset_type=Asset.AssetType.OPTION,   # Must specify OPTION type
    expiration=date(2025, 10, 26),       # datetime.date object
    strike=183.0,                        # Float
    right=Asset.OptionRight.PUT          # PUT or CALL enum
)
```

**Alternative String Format:**
```python
option = Asset(
    symbol="IWM",
    asset_type="option",     # String instead of enum
    expiration=date(2025, 10, 26),
    strike=183.0,
    right="PUT"              # String instead of enum
)
```

---

## Backtesting Configuration

### Data Source: PolygonDataBacktesting

**Why Polygon.io?**
- Options data requires high-quality provider
- Yahoo Finance does NOT provide options data
- Polygon.io has comprehensive options chains, strikes, and premiums

**Requirements:**
- Polygon.io API key
- Paid subscription for options data

### Backtest Setup

```python
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.entities import TradingFee
from datetime import datetime

# Configure strategy
class ZeroDTE_IWM_Strategy(Strategy):
    parameters = {
        "symbol": "IWM",
        # ... other parameters
    }

    # ... strategy implementation

# Run backtest
if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    ZeroDTE_IWM_Strategy.backtest(
        PolygonDataBacktesting,
        start_date,
        end_date,
        parameters={
            "symbol": "IWM"
        },
        polygon_api_key="YOUR_POLYGON_API_KEY",
        polygon_has_paid_subscription=True,  # Required for options
        buy_trading_fees=[TradingFee(percent_fee=0.0)],  # Options often have flat fees
        sell_trading_fees=[TradingFee(percent_fee=0.0)],
        benchmark_asset="IWM"
    )
```

**Trading Fees Note:**
- Options commissions are typically flat per contract (e.g., $0.50-$0.65 per contract)
- Use `TradingFee(flat_fee=0.65)` for per-contract fees
- Check broker fee structure

---

## Technical Indicators Required

**None** - This is a pure options premium collection strategy with no technical indicators.

However, potential enhancements could include:

**Optional Indicators for Entry Filtering:**
- **VIX (Volatility Index)**: Only enter when VIX > threshold (higher premium)
- **IWM RSI**: Avoid selling puts when RSI < 30 (oversold)
- **IWM Historical Volatility**: Trade only when HV > certain level

**Implementation Example:**
```python
def _should_enter_trades(self):
    """Optional: Filter entry based on volatility conditions"""
    # Get VIX
    vix = self.get_last_price("VIX")

    if vix is None:
        return True  # Proceed if VIX not available

    # Only trade when VIX > 15 (sufficient premium)
    if vix < 15:
        self.log_message(f"Skipping entry: VIX too low ({vix:.2f})")
        return False

    return True
```

---

## Strategy Lifecycle Flow

### 1. Initialize Phase

```python
def initialize(self):
    self.sleeptime = "15M"  # Check every 15 minutes
    self.minutes_before_closing = 5

    self.symbol = "IWM"

    # Track entry premiums for each leg
    self.entry_premium_put = None
    self.entry_premium_call1 = None
    self.entry_premium_call2 = None

    # Track strikes for exit threshold logic
    self.call_strike_high = None  # ~$191
    self.call_strike_low = None   # ~$190
    self.put_strike = None        # ~$183

    # Track entry status
    self.positions_opened_today = False
```

### 2. Trading Iteration Flow

```python
def on_trading_iteration(self):
    """
    Main logic called every 15 minutes
    """
    try:
        current_time = self.get_datetime()

        # Check if within entry window (first 30 min of trading day)
        if self._is_entry_window(current_time):
            if not self.positions_opened_today:
                self._enter_positions()
                self.positions_opened_today = True

        # Check exit conditions for existing positions
        self._check_exits()

    except Exception as e:
        self.log_message(f"ERROR in on_trading_iteration: {str(e)}")

def before_market_closes(self):
    """
    Close all positions before market close
    """
    positions = self.get_positions()
    if positions:
        self.log_message("Market closing soon - exiting all 0DTE positions")
        self.sell_all()

def before_market_opens(self):
    """
    Reset daily tracking at market open
    """
    self.positions_opened_today = False
```

### 3. Complete Strategy Structure

```python
from lumibot.strategies import Strategy
from lumibot.entities import Asset
from datetime import datetime, date, time, timedelta

class ZeroDTE_IWM_Strategy(Strategy):
    parameters = {
        "symbol": "IWM",
        "put_contracts": 10,
        "call1_contracts": 5,
        "call2_contracts": 5,
        "put_exit_premium": 0.02,
        "call_high_exit_premium": 0.15,
        "call_low_exit_premium": 0.07,
        "entry_window_minutes": 30
    }

    def initialize(self):
        # ... (see above)
        pass

    def on_trading_iteration(self):
        # ... (see above)
        pass

    def before_market_opens(self):
        # ... (see above)
        pass

    def before_market_closes(self):
        # ... (see above)
        pass

    def _is_entry_window(self, current_time):
        # ... (implementation above)
        pass

    def _enter_positions(self):
        # ... (implementation above)
        pass

    def _check_exits(self):
        # ... (implementation above)
        pass

    def _get_0dte_expiration(self, chains, option_type):
        # ... (implementation above)
        pass

    def _select_put_strike(self, chains, expiry, current_price):
        # ... (implementation above)
        pass

    def _select_call_strikes(self, chains, expiry, current_price):
        # ... (implementation above)
        pass

    def _get_exit_threshold(self, option_asset):
        # ... (implementation above)
        pass
```

---

## Special Considerations

### 1. 0DTE Options Availability

**Issue**: Not all trading days have 0DTE options for IWM.

**Traditional Schedule:**
- SPX: Daily 0DTE (Mon-Fri)
- SPY: Mon/Wed/Fri
- IWM: May vary by date

**Solution:**
```python
def _get_0dte_expiration(self, chains, option_type):
    expiries = chains.expirations(option_type)
    today = date.today()

    dte_0 = [exp for exp in expiries if exp == today]

    if not dte_0:
        self.log_message(f"No 0DTE options today ({today.strftime('%A')})")
        return None

    return dte_0[0]
```

**Backtesting Impact**: Strategy will only trade on days when 0DTE options are available.

### 2. Margin Requirements

**Critical**: Naked options require substantial margin.

**Broker Requirements:**
- Interactive Brokers: Portfolio Margin account recommended
- TD Ameritrade: Naked options approval (highest level)
- Minimum account size: $75,000+ recommended

**Backtesting**: Ensure backtester accounts for margin, not just cash.

### 3. Assignment Risk

**Risk**: Short options can be assigned early (American-style options).

**Mitigation:**
- Monitor positions closely
- Exit before market close (before expiration)
- Avoid holding ITM (in-the-money) options

### 4. Slippage and Liquidity

**Issue**: Options can have wide bid-ask spreads.

**Backtesting Considerations:**
- Polygon data may show mid-price, not executable price
- Real execution may be worse than backtest
- IWM options generally liquid but not as tight as SPY

**Recommendation**: Add slippage model to backtest:
```python
buy_trading_fees=[TradingFee(percent_fee=0.002)]  # 0.2% slippage estimate
```

### 5. Gamma Risk

**Risk**: As options approach expiration, gamma increases (delta changes rapidly).

**Impact**: If IWM moves sharply toward strike prices, losses can accelerate.

**Monitoring**: Consider adding delta/gamma monitoring (requires options pricing model).

### 6. Premium Collection vs. Risk

**Current Strategy Profile:**
- Max premium collected: ~$0.50-$2.00 per contract (estimate)
- Max loss per contract: Potentially $10,000+ on large moves
- Risk-to-reward ratio: Unfavorable for single-day disasters

**Enhancement Idea**: Add position size scaling based on VIX or IWM historical volatility.

---

## Risk Management Enhancements

The base strategy has minimal risk management. Consider adding:

### 1. Stop Loss on Total Portfolio

```python
def on_trading_iteration(self):
    # ... existing logic

    # Check portfolio-level stop loss
    if self.portfolio_value < self.initial_cash * 0.95:  # 5% drawdown
        self.log_message("Portfolio stop loss triggered")
        self.sell_all()
```

### 2. Delta Hedging (Advanced)

```python
def _hedge_delta(self):
    """
    Buy/sell IWM shares to neutralize portfolio delta
    Requires options pricing library (e.g., py_vollib)
    """
    # Calculate total portfolio delta from all option positions
    # Offset with long/short IWM shares
    pass
```

### 3. Early Exit on Directional Move

```python
def _check_directional_risk(self):
    """
    Exit early if IWM moves sharply toward strike prices
    """
    current_price = self.get_last_price("IWM")

    # If approaching PUT strike
    if current_price < self.put_strike * 1.02:  # Within 2% of PUT strike
        self.log_message("IWM approaching PUT strike - early exit")
        self.sell_all()

    # If approaching CALL strikes
    if current_price > self.call_strike_low * 0.98:  # Within 2% of CALL strike
        self.log_message("IWM approaching CALL strike - early exit")
        self.sell_all()
```

---

## Backtesting Considerations

### Data Requirements

**Essential:**
- Option chain data (strikes, expirations) - Polygon.io
- Option premium data (bid/ask/last) - Polygon.io
- Underlying price data (IWM) - Polygon.io

**Date Range:**
- Recommended: 6-12 months minimum
- Avoid sparse data periods (low liquidity days)

### Backtesting Limitations

**Known Issues:**
1. **Assignment not modeled**: Backtester assumes positions held until exit logic
2. **Bid-ask spread**: May use mid-price instead of actual executable price
3. **Margin calls**: Not typically modeled in backtests
4. **Early assignment**: Not modeled (options held to exit threshold)

**Mitigation:**
- Add conservative slippage assumptions
- Manually review positions that go ITM
- Stress test with historical volatility spikes

### Performance Metrics to Track

```python
# After backtest completes
results = ZeroDTE_IWM_Strategy.backtest(...)

# Key metrics:
# - Total return
# - Sharpe ratio
# - Max drawdown
# - Win rate
# - Average profit per trade
# - Average loss per trade
# - Number of trades
# - Profit factor (gross profit / gross loss)
```

---

## Example Full Strategy Code

```python
from lumibot.strategies import Strategy
from lumibot.entities import Asset
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime, date, time, timedelta

class ZeroDTE_IWM_Strategy(Strategy):
    """
    0DTE Options Premium Collection on IWM

    Entry: Sell 10 PUTs (~$183), 5 CALLs (~$191), 5 CALLs (~$190)
    Exit: Buy back when premium decays to thresholds
    Timeframe: Intraday, 0DTE only
    """

    parameters = {
        "symbol": "IWM",
        "put_contracts": 10,
        "call1_contracts": 5,
        "call2_contracts": 5,
        "put_exit_premium": 0.02,
        "call_high_exit_premium": 0.15,
        "call_low_exit_premium": 0.07,
        "entry_window_minutes": 30,
        "put_otm_percent": 0.02,    # 2% OTM for puts
        "call_otm_percent_low": 0.015,  # 1.5% OTM for lower call strike
        "call_otm_percent_high": 0.02   # 2% OTM for higher call strike
    }

    def initialize(self):
        self.sleeptime = "15M"
        self.minutes_before_closing = 5

        self.symbol = self.parameters["symbol"]

        # Entry tracking
        self.positions_opened_today = False

        # Store strikes for exit logic
        self.put_strike = None
        self.call_strike_low = None
        self.call_strike_high = None

        # Store initial cash for risk management
        self.initial_cash = self.get_cash()

    def before_market_opens(self):
        """Reset daily tracking"""
        self.positions_opened_today = False
        self.log_message("=== New Trading Day ===")

    def on_trading_iteration(self):
        """Main trading logic"""
        try:
            current_time = self.get_datetime()

            # Entry logic: within first 30 minutes
            if self._is_entry_window(current_time):
                if not self.positions_opened_today and not self._has_positions():
                    self._enter_positions()
                    self.positions_opened_today = True

            # Exit logic: check premium thresholds
            if self._has_positions():
                self._check_exits()

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

    def before_market_closes(self):
        """Force close all positions before market close"""
        if self._has_positions():
            self.log_message("Market closing - exiting all 0DTE positions")
            self.sell_all()

    def _is_entry_window(self, current_time):
        """Check if within 30-minute entry window after market open"""
        market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        window_end = market_open + timedelta(minutes=self.parameters["entry_window_minutes"])

        return market_open <= current_time <= window_end

    def _has_positions(self):
        """Check if any positions exist"""
        positions = self.get_positions()
        return len(positions) > 0

    def _enter_positions(self):
        """Execute all three option legs"""
        # Get current price
        current_price = self.get_last_price(self.symbol)
        if current_price is None:
            return

        # Get option chains
        chains = self.get_chains(Asset(self.symbol))
        if chains is None:
            self.log_message("No option chains available")
            return

        # Get 0DTE expirations
        put_expiry = self._get_0dte_expiration(chains, "PUT")
        call_expiry = self._get_0dte_expiration(chains, "CALL")

        if put_expiry is None or call_expiry is None:
            return

        # Select strikes
        put_strike = self._select_put_strike(chains, put_expiry, current_price)
        call_low, call_high = self._select_call_strikes(chains, call_expiry, current_price)

        if None in [put_strike, call_low, call_high]:
            self.log_message("Could not find appropriate strikes")
            return

        # Store strikes
        self.put_strike = put_strike
        self.call_strike_low = call_low
        self.call_strike_high = call_high

        # Create option Assets
        put_option = Asset(
            symbol=self.symbol,
            asset_type=Asset.AssetType.OPTION,
            expiration=put_expiry,
            strike=put_strike,
            right=Asset.OptionRight.PUT
        )

        call_option_low = Asset(
            symbol=self.symbol,
            asset_type=Asset.AssetType.OPTION,
            expiration=call_expiry,
            strike=call_low,
            right=Asset.OptionRight.CALL
        )

        call_option_high = Asset(
            symbol=self.symbol,
            asset_type=Asset.AssetType.OPTION,
            expiration=call_expiry,
            strike=call_high,
            right=Asset.OptionRight.CALL
        )

        # Submit sell orders (sell to open)
        self.submit_order(self.create_order(
            put_option,
            self.parameters["put_contracts"],
            side="sell"
        ))

        self.submit_order(self.create_order(
            call_option_low,
            self.parameters["call1_contracts"],
            side="sell"
        ))

        self.submit_order(self.create_order(
            call_option_high,
            self.parameters["call2_contracts"],
            side="sell"
        ))

        self.log_message(
            f"ENTRY: Sold {self.parameters['put_contracts']} PUTs @ ${put_strike:.2f}, "
            f"{self.parameters['call1_contracts']} CALLs @ ${call_low:.2f}, "
            f"{self.parameters['call2_contracts']} CALLs @ ${call_high:.2f}"
        )

    def _check_exits(self):
        """Check exit conditions for each position"""
        positions = self.get_positions()

        for position in positions:
            asset = position.asset

            if asset.asset_type != Asset.AssetType.OPTION:
                continue

            current_premium = self.get_last_price(asset)
            if current_premium is None:
                continue

            threshold = self._get_exit_threshold(asset)

            if current_premium <= threshold:
                # Buy to close
                self.submit_order(self.create_order(
                    asset,
                    position.quantity,
                    side="buy"
                ))

                self.log_message(
                    f"EXIT: {asset.right} @ ${asset.strike:.2f} "
                    f"| Premium: ${current_premium:.2f} <= ${threshold:.2f}"
                )

    def _get_0dte_expiration(self, chains, option_type):
        """Get today's expiration (0DTE)"""
        expiries = chains.expirations(option_type)
        today = date.today()

        dte_0 = [exp for exp in expiries if exp == today]

        if not dte_0:
            self.log_message(f"No 0DTE {option_type} options available")
            return None

        return dte_0[0]

    def _select_put_strike(self, chains, expiry, current_price):
        """Select PUT strike ~2% OTM"""
        strikes = chains.strikes(expiry, "PUT")
        target = current_price * (1 - self.parameters["put_otm_percent"])

        otm_strikes = [s for s in strikes if s <= target]
        return max(otm_strikes) if otm_strikes else None

    def _select_call_strikes(self, chains, expiry, current_price):
        """Select two CALL strikes ~1.5% and ~2% OTM"""
        strikes = sorted(chains.strikes(expiry, "CALL"))

        target_low = current_price * (1 + self.parameters["call_otm_percent_low"])
        target_high = current_price * (1 + self.parameters["call_otm_percent_high"])

        otm_strikes = [s for s in strikes if s >= current_price]

        if not otm_strikes:
            return (None, None)

        strike_low = min(otm_strikes, key=lambda x: abs(x - target_low))
        strike_high = min(otm_strikes, key=lambda x: abs(x - target_high))

        return (strike_low, strike_high)

    def _get_exit_threshold(self, option_asset):
        """Get exit premium threshold for an option"""
        if option_asset.right == Asset.OptionRight.PUT:
            return self.parameters["put_exit_premium"]

        elif option_asset.right == Asset.OptionRight.CALL:
            if option_asset.strike == self.call_strike_high:
                return self.parameters["call_high_exit_premium"]
            elif option_asset.strike == self.call_strike_low:
                return self.parameters["call_low_exit_premium"]

        return 0.05  # Fallback


if __name__ == "__main__":
    # Backtest configuration
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    ZeroDTE_IWM_Strategy.backtest(
        PolygonDataBacktesting,
        start_date,
        end_date,
        parameters={
            "symbol": "IWM"
        },
        polygon_api_key="YOUR_POLYGON_API_KEY",
        polygon_has_paid_subscription=True,
        benchmark_asset="IWM"
    )
```

---

## Summary Checklist

### Implementation Requirements

- [x] **Entry Timing**: Within 30 minutes of market open
- [x] **0DTE Filtering**: Only trade options expiring today
- [x] **Strike Selection**: Dynamic selection based on current IWM price
- [x] **Position Sizing**: 10 PUTs, 5 CALLs, 5 CALLs
- [x] **Exit Logic**: Individual premium thresholds per leg
- [x] **End-of-Day**: Force close before market close
- [x] **Data Source**: Polygon.io for options data
- [x] **Asset Creation**: Proper Option Asset objects
- [x] **Error Handling**: Validate chains, prices, strikes

### Lumibot Methods Used

- [x] `self.get_datetime()`
- [x] `self.get_last_price()`
- [x] `self.get_chains()`
- [x] `chains.expirations()`
- [x] `chains.strikes()`
- [x] `self.create_order()`
- [x] `self.submit_order()`
- [x] `self.get_positions()`
- [x] `self.sell_all()`
- [x] `self.log_message()`
- [x] `Asset()` creation with OPTION type

### Risk Warnings

- [ ] Naked options have unlimited loss potential
- [ ] Requires substantial margin ($75,000+)
- [ ] Early assignment risk on American options
- [ ] Wide bid-ask spreads can impact execution
- [ ] 0DTE options have extreme gamma risk
- [ ] Strategy may not trade every day (0DTE availability)

---

## Next Steps for Implementation

1. **Set up Polygon.io account** and obtain API key with options data access
2. **Implement base strategy** using code template above
3. **Add parameter tuning** (OTM percentages, exit thresholds)
4. **Backtest across multiple time periods** (different volatility regimes)
5. **Add risk management enhancements** (stop loss, delta hedging)
6. **Paper trade** before live deployment
7. **Verify margin requirements** with broker
8. **Monitor slippage** and adjust fee assumptions

---

**Document Version**: 1.0
**Author**: lumibot-researcher agent
**Date**: 2025-10-26
**Status**: Complete specification ready for implementation
