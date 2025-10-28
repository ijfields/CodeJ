---
title: Lumibot Framework Reference
description: Complete API reference for Lumibot trading framework
version: 3.x
last_updated: 2025-01-25
---

# Lumibot Framework Reference

Complete reference for building trading strategies with the Lumibot framework. This document covers all essential methods, patterns, and best practices.

## Table of Contents

1. [Strategy Basics](#strategy-basics)
2. [Lifecycle Methods](#lifecycle-methods)
3. [Data Methods](#data-methods)
4. [Order Management](#order-management)
5. [Options Trading](#options-trading)
6. [Position Management](#position-management)
7. [Strategy Properties](#strategy-properties)
8. [Backtesting](#backtesting)
9. [Common Patterns](#common-patterns)
10. [Troubleshooting](#troubleshooting)

---

## Strategy Basics

### Minimum Strategy Structure

```python
from lumibot.strategies import Strategy

class MyStrategy(Strategy):
    # Optional: default parameters
    parameters = {
        "symbol": "SPY",
        "timeframe": "1D"
    }

    def initialize(self):
        """REQUIRED: Called once at strategy start"""
        self.sleeptime = "1D"  # MUST set this

    def on_trading_iteration(self):
        """REQUIRED: Main trading logic"""
        pass
```

### Required Elements

1. **Inherit from Strategy**: `class MyStrategy(Strategy):`
2. **initialize() method**: Set `self.sleeptime` at minimum
3. **on_trading_iteration() method**: Main trading logic

---

## Lifecycle Methods

### initialize()

**Purpose**: One-time setup when strategy starts

**Called**: Once, before first trading iteration

**Common Use**:
```python
def initialize(self):
    # REQUIRED: Set trading frequency
    self.sleeptime = "1D"  # Options: "30S", "5M", "1H", "1D"

    # Optional: Market timing
    self.minutes_before_closing = 5
    self.minutes_before_opening = 0

    # Optional: Get parameters
    self.symbol = self.parameters.get("symbol", "SPY")

    # Optional: Initialize state
    self.entry_price = None
    self.position_count = 0
```

**sleeptime formats**:
- Seconds: `"30S"` = 30 seconds
- Minutes: `"5M"` = 5 minutes
- Hours: `"2H"` = 2 hours
- Days: `"1D"` = 1 day

### on_trading_iteration()

**Purpose**: Main trading logic executed repeatedly

**Called**: Every `self.sleeptime` interval during market hours

**Pattern**:
```python
def on_trading_iteration(self):
    # 1. Get data
    price = self.get_last_price("SPY")
    bars = self.get_historical_prices("SPY", 50, "1D")

    # 2. Validate data
    if bars is None or bars.df.empty:
        return

    # 3. Calculate indicators
    df = bars.df
    df['rsi'] = ta.rsi(df['close'], 14)

    # 4. Check position
    position = self.get_position("SPY")
    is_in_position = position is not None

    # 5. Entry logic
    if not is_in_position:
        if df['rsi'].iloc[-1] < 30:
            order = self.create_order("SPY", 10, "buy")
            self.submit_order(order)

    # 6. Exit logic
    elif is_in_position:
        if df['rsi'].iloc[-1] > 70:
            self.sell_all()
```

### Optional Lifecycle Methods

```python
def before_market_opens(self):
    """Called before market opens each day"""
    pass

def before_market_closes(self):
    """Called before market closes each day"""
    pass

def after_market_closes(self):
    """Called after market closes each day"""
    pass

def on_abrupt_closing(self):
    """Called if strategy is stopped unexpectedly"""
    pass
```

---

## Data Methods

### get_last_price()

**Purpose**: Get current price of an asset

**Signature**: `get_last_price(asset)`

**Usage**:
```python
# For stocks/ETFs
price = self.get_last_price("SPY")  # Returns float

# For Asset objects
asset = Asset("AAPL")
price = self.get_last_price(asset)

# Always validate
if price is None or price <= 0:
    self.log_message("Invalid price")
    return
```

**Returns**: `float` or `None`

### get_historical_prices()

**Purpose**: Get historical OHLCV data

**Signature**: `get_historical_prices(asset, length, timestep, **kwargs)`

**Parameters**:
- `asset`: Symbol string or Asset object
- `length`: Number of bars to retrieve (int)
- `timestep`: Timeframe ("1M", "5M", "1H", "1D", etc.)

**Usage**:
```python
# Get 50 daily bars for SPY
bars = self.get_historical_prices("SPY", 50, "1D")

# Always validate
if bars is None or bars.df.empty:
    self.log_message("No data available")
    return

# Access DataFrame
df = bars.df  # Pandas DataFrame

# Check minimum data
if len(df) < 20:
    self.log_message("Not enough data")
    return

# Available columns
# - df['open']
# - df['high']
# - df['low']
# - df['close']
# - df['volume']
# - df.index (datetime)
```

**Bars Object Methods**:
```python
# Get DataFrame
df = bars.df

# Filter by date range
filtered_bars = bars.filter(start=datetime(2023,1,1), end=datetime(2023,12,31))

# Get total volume
total_vol = bars.get_total_volume()

# Aggregate to different timeframe
hourly_bars = bars.aggregate_bars("1H")
```

**Timestep formats**:
- `"1M"`, `"5M"`, `"15M"`, `"30M"` - Minutes
- `"1H"`, `"4H"` - Hours
- `"1D"` - Daily

---

## Order Management

### create_order()

**Purpose**: Create an order object (doesn't execute yet)

**Signature**: `create_order(asset, quantity, side, **kwargs)`

**Parameters**:
- `asset`: Symbol string or Asset object
- `quantity`: Number of shares/contracts (int)
- `side`: `"buy"` or `"sell"` (REQUIRED)

**Usage**:
```python
# Create buy order
order = self.create_order(
    asset="SPY",
    quantity=10,
    side="buy"
)

# For options
option = Asset(
    symbol="SPY",
    asset_type=Asset.AssetType.OPTION,
    expiration=date(2025, 1, 17),
    strike=400,
    right=Asset.OptionRight.CALL
)
order = self.create_order(
    asset=option,
    quantity=1,
    side="sell"  # Sell to open
)
```

### submit_order()

**Purpose**: Submit order for execution

**Signature**: `submit_order(order)`

**Usage**:
```python
# Create and submit in one flow
order = self.create_order("SPY", 10, "buy")
self.submit_order(order)

# Or submit list of orders
orders = [
    self.create_order("SPY", 10, "buy"),
    self.create_order("QQQ", 5, "buy")
]
for order in orders:
    self.submit_order(order)
```

### sell_all()

**Purpose**: Close all positions immediately

**Signature**: `sell_all()`

**Usage**:
```python
# Close all positions
self.sell_all()

# Common in exit logic
if exit_condition:
    self.sell_all()
    self.log_message("Exited all positions")
```

### cancel_order()

**Purpose**: Cancel a specific order

**Signature**: `cancel_order(order)`

### cancel_open_orders()

**Purpose**: Cancel all open (unfilled) orders

**Signature**: `cancel_open_orders()`

---

## Options Trading

### get_chains()

**Purpose**: Get option chain data for an underlying

**Signature**: `get_chains(asset)`

**Usage**:
```python
# Get chains for SPY
chains = self.get_chains(Asset("SPY"))

# Always validate
if chains is None:
    self.log_message("No option chains available")
    return

# Get expirations
call_expiries = chains.expirations("CALL")  # List of dates
put_expiries = chains.expirations("PUT")
all_expiries = chains.expirations()  # Defaults to CALL

# Get strikes for an expiration
expiry = call_expiries[0]
strikes = chains.strikes(expiry, "CALL")  # List of floats

# Get multiplier
multiplier = chains.multiplier  # Usually 100 for equity options
```

### Asset Creation for Options

**Full Example**:
```python
from lumibot.entities import Asset
from datetime import date

# Method 1: Using enums (recommended)
option = Asset(
    symbol="SPY",
    asset_type=Asset.AssetType.OPTION,
    expiration=date(2025, 1, 17),
    strike=400.0,
    right=Asset.OptionRight.CALL
)

# Method 2: Using strings
option = Asset(
    symbol="SPY",
    asset_type="option",
    expiration=date(2025, 1, 17),
    strike=400.0,
    right="CALL"  # or "PUT"
)
```

### 0DTE (Zero-Day-To-Expiration) Pattern

```python
from datetime import date

def _get_0dte_option(self, option_type="PUT"):
    """Get 0DTE option contract"""
    # Get chains
    chains = self.get_chains(Asset(self.symbol))
    if chains is None:
        return None

    # Get expirations
    expiries = chains.expirations(option_type)
    today = date.today()

    # Filter for 0DTE
    dte_0 = [exp for exp in expiries if exp == today]
    if not dte_0:
        self.log_message("No 0DTE options available")
        return None

    expiry = dte_0[0]

    # Get strikes
    strikes = chains.strikes(expiry, option_type)
    current_price = self.get_last_price(self.symbol)

    # Select OTM strike (example: $5 below for puts)
    if option_type == "PUT":
        otm_strikes = [s for s in strikes if s < current_price - 5]
        target_strike = max(otm_strikes) if otm_strikes else None
    else:  # CALL
        otm_strikes = [s for s in strikes if s > current_price + 5]
        target_strike = min(otm_strikes) if otm_strikes else None

    if not target_strike:
        return None

    # Create option Asset
    return Asset(
        symbol=self.symbol,
        asset_type=Asset.AssetType.OPTION,
        expiration=expiry,
        strike=target_strike,
        right=Asset.OptionRight.PUT if option_type == "PUT" else Asset.OptionRight.CALL
    )
```

### Strike Selection Patterns

```python
def select_strike_by_delta(self, chains, expiry, target_delta=0.30):
    """Select strike closest to target delta"""
    # Note: get_greeks() requires real-time data
    # For backtesting, use approximation
    pass

def select_strike_by_moneyness(self, chains, expiry, option_type, percent_otm=0.05):
    """Select strike based on % out-of-the-money"""
    strikes = chains.strikes(expiry, option_type)
    current_price = self.get_last_price(self.symbol)

    if option_type == "PUT":
        target_strike = current_price * (1 - percent_otm)
        # Find closest strike
        otm_strikes = [s for s in strikes if s < target_strike]
        return max(otm_strikes) if otm_strikes else None
    else:  # CALL
        target_strike = current_price * (1 + percent_otm)
        otm_strikes = [s for s in strikes if s > target_strike]
        return min(otm_strikes) if otm_strikes else None

def select_strike_by_price_offset(self, chains, expiry, option_type, offset=5):
    """Select strike based on fixed dollar offset"""
    strikes = chains.strikes(expiry, option_type)
    current_price = self.get_last_price(self.symbol)

    if option_type == "PUT":
        target = current_price - offset
        otm_strikes = [s for s in strikes if s < target]
        return max(otm_strikes) if otm_strikes else None
    else:
        target = current_price + offset
        otm_strikes = [s for s in strikes if s > target]
        return min(otm_strikes) if otm_strikes else None
```

---

## Position Management

### get_position()

**Purpose**: Get current position for an asset

**Signature**: `get_position(asset)`

**Usage**:
```python
# Get position
position = self.get_position("SPY")

# Check if in position
is_in_position = position is not None and position.quantity > 0

# Access position attributes
if position:
    quantity = position.quantity  # Number of shares/contracts
    avg_price = position.avg_price  # Average entry price
    current_value = position.quantity * self.get_last_price("SPY")

    # Calculate PnL
    pnl_per_share = self.get_last_price("SPY") - position.avg_price
    total_pnl = pnl_per_share * position.quantity
    pnl_pct = (pnl_per_share / position.avg_price) * 100

    self.log_message(f"Position: {quantity} @ ${avg_price:.2f}, PnL: {pnl_pct:.2f}%")
```

### get_positions()

**Purpose**: Get all current positions

**Returns**: List of Position objects

```python
all_positions = self.get_positions()

for position in all_positions:
    symbol = position.asset.symbol
    qty = position.quantity
    self.log_message(f"{symbol}: {qty} shares")
```

---

## Strategy Properties

### Available Properties

```python
# Portfolio information
self.portfolio_value  # Total portfolio value (cash + positions)
self.cash            # Available cash (use get_cash() method instead)

# Iteration tracking
self.first_iteration  # True on first iteration only
self.last_on_trading_iteration_datetime  # Datetime of last iteration

# Configuration
self.sleeptime       # Trading frequency
self.minutes_before_closing  # Stop trading N minutes before close
self.minutes_before_opening  # Start trading N minutes after open

# Mode detection
self.is_backtesting  # True if running backtest, False if live

# Parameters
self.parameters      # Dict of strategy parameters

# Name
self.name           # Strategy name
```

### get_cash()

**Purpose**: Get available cash

**Usage**:
```python
cash = self.get_cash()
self.log_message(f"Available cash: ${cash:.2f}")

# Use for position sizing
max_position_value = cash * 0.95  # Use 95% of cash
```

---

## Backtesting

### Yahoo Finance (Free)

```python
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime

# Run backtest
MyStrategy.backtest(
    YahooDataBacktesting,
    datetime(2023, 1, 1),
    datetime(2023, 12, 31),
    parameters={"symbol": "SPY"},
    benchmark_asset="SPY"
)
```

### Polygon.io (Paid, Better Data)

```python
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.entities import TradingFee

# Run backtest with fees
MyStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2023, 1, 1),
    datetime(2023, 12, 31),
    parameters={"symbol": "SPY"},
    polygon_api_key="your_key_here",
    polygon_has_paid_subscription=True,
    buy_trading_fees=[TradingFee(percent_fee=0.001)],  # 0.1%
    sell_trading_fees=[TradingFee(percent_fee=0.001)],
    benchmark_asset="SPY"
)
```

---

## Common Patterns

### Pattern 1: Simple RSI Strategy

```python
import pandas_ta as ta

class RSIStrategy(Strategy):
    parameters = {
        "symbol": "SPY",
        "rsi_period": 14,
        "rsi_low": 30,
        "rsi_high": 70
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.symbol = self.parameters.get("symbol")

    def on_trading_iteration(self):
        # Get data
        bars = self.get_historical_prices(self.symbol, 50, "1D")
        if bars is None or bars.df.empty:
            return

        df = bars.df
        df['rsi'] = ta.rsi(df['close'], self.parameters['rsi_period'])

        current_rsi = df['rsi'].iloc[-1]
        position = self.get_position(self.symbol)

        # Entry
        if not position and current_rsi < self.parameters['rsi_low']:
            cash = self.get_cash()
            price = self.get_last_price(self.symbol)
            qty = int((cash * 0.95) / price)
            order = self.create_order(self.symbol, qty, "buy")
            self.submit_order(order)

        # Exit
        elif position and current_rsi > self.parameters['rsi_high']:
            self.sell_all()
```

### Pattern 2: 0DTE Options Premium Collection

```python
from datetime import date

class ZeroDTE_Strategy(Strategy):
    parameters = {
        "symbol": "SPY",
        "num_contracts": 10,
        "strike_offset": 5,
        "exit_premium_pct": 0.50
    }

    def initialize(self):
        self.sleeptime = "15M"  # Check every 15 minutes
        self.symbol = self.parameters["symbol"]
        self.entry_premium = None

    def on_trading_iteration(self):
        position = self.get_position(self.symbol)

        if not position:
            # Try to sell 0DTE puts
            option = self._get_0dte_put()
            if option:
                order = self.create_order(
                    option,
                    self.parameters["num_contracts"],
                    "sell"  # Sell to open
                )
                self.submit_order(order)
                premium = self.get_last_price(option)
                self.entry_premium = premium
                self.log_message(f"SOLD {self.parameters['num_contracts']} puts @ ${premium:.2f}")

        else:
            # Check exit: buy back at 50% profit
            current_price = self.get_last_price(position.asset)
            if self.entry_premium and current_price <= self.entry_premium * 0.5:
                self.sell_all()  # Buy to close
                self.log_message(f"CLOSED at 50% profit")

    def _get_0dte_put(self):
        chains = self.get_chains(Asset(self.symbol))
        if not chains:
            return None

        expiries = chains.expirations("PUT")
        today = date.today()
        dte_0 = [e for e in expiries if e == today]

        if not dte_0:
            return None

        strikes = chains.strikes(dte_0[0], "PUT")
        current_price = self.get_last_price(self.symbol)
        otm_strikes = [s for s in strikes if s < current_price - self.parameters["strike_offset"]]

        if not otm_strikes:
            return None

        return Asset(
            symbol=self.symbol,
            asset_type=Asset.AssetType.OPTION,
            expiration=dte_0[0],
            strike=max(otm_strikes),
            right=Asset.OptionRight.PUT
        )
```

---

## Troubleshooting

### Issue: "AttributeError: 'NoneType' object has no attribute 'df'"

**Cause**: `get_historical_prices()` returned `None`

**Fix**:
```python
bars = self.get_historical_prices(symbol, 50, "1D")
if bars is None or bars.df.empty:  # ALWAYS validate
    return
df = bars.df
```

### Issue: "TypeError: create_order() missing 1 required positional argument: 'side'"

**Cause**: Didn't specify `side` parameter

**Fix**:
```python
# Wrong
order = self.create_order("SPY", 10)

# Correct
order = self.create_order("SPY", 10, side="buy")
```

### Issue: "ValueError: Option asset missing required attribute"

**Cause**: Option Asset missing `expiration`, `strike`, or `right`

**Fix**:
```python
option = Asset(
    symbol="SPY",
    asset_type=Asset.AssetType.OPTION,
    expiration=date(2025, 1, 17),  # Required
    strike=400.0,                   # Required
    right=Asset.OptionRight.CALL    # Required
)
```

### Issue: "Insufficient data for indicators"

**Cause**: Not enough bars for indicator calculation

**Fix**:
```python
bars = self.get_historical_prices("SPY", 50, "1D")
df = bars.df

# Check length BEFORE calculating
if len(df) < 20:  # RSI(14) needs at least 14-20 bars
    self.log_message("Not enough data")
    return

df['rsi'] = ta.rsi(df['close'], 14)

# Check for NaN
if pd.isna(df['rsi'].iloc[-1]):
    self.log_message("RSI not ready")
    return
```

---

## Best Practices

### ✅ DO:

1. **Always validate data**:
   ```python
   if bars is None or bars.df.empty:
       return
   ```

2. **Check for NaN in indicators**:
   ```python
   if pd.isna(df['rsi'].iloc[-1]):
       return
   ```

3. **Use try/except in main logic**:
   ```python
   def on_trading_iteration(self):
       try:
           self._execute_logic()
       except Exception as e:
           self.log_message(f"ERROR: {str(e)}")
   ```

4. **Log important actions**:
   ```python
   self.log_message(f"ENTRY: {qty} shares @ ${price:.2f}")
   ```

5. **Set self.sleeptime in initialize()**:
   ```python
   def initialize(self):
       self.sleeptime = "1D"  # REQUIRED
   ```

### ❌ DON'T:

1. **Don't access .df without validation**
2. **Don't forget `side` parameter in create_order()**
3. **Don't hardcode values - use parameters**
4. **Don't skip error handling**
5. **Don't use magic numbers without comments**

---

## Resources

- **Official Docs**: https://lumibot.lumiwealth.com/
- **GitHub**: https://github.com/Lumiwealth/lumibot
- **Discord**: https://discord.gg/lumibot
- **Examples**: https://github.com/Lumiwealth/lumibot/tree/master/lumibot/example_strategies

---

Last updated: 2025-01-25
