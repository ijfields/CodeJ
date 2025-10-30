# Data Schemas

**Purpose:** Document file structures, naming patterns, and data formats
**Version:** Phase 1 MVP (Flat File Storage)
**Last Updated:** 2025-10-29

---

## Table of Contents

1. [File Naming Patterns](#file-naming-patterns)
2. [Strategy Files](#strategy-files)
3. [Backtest Output Files](#backtest-output-files)
4. [Directory Structure](#directory-structure)
5. [Data Type Reference](#data-type-reference)

---

## File Naming Patterns

### Backtest Output Files

**Pattern:**
```
{StrategyClassName}_{YYYY-MM-DD}_{HH-MM}_{6-char-hash}_{type}.{ext}
```

**Components:**
- `StrategyClassName`: Python class name from strategy file (e.g., `EMACrossoverStrategy`)
- `YYYY-MM-DD`: Date the backtest was run
- `HH-MM`: Time the backtest was run (24-hour format)
- `6-char-hash`: Random hash for uniqueness (e.g., `FoWcfI`)
- `type`: File type identifier (`settings`, `tearsheet`, `trades`, `stats`)
- `ext`: File extension (`.json`, `.csv`, `.html`)

**Examples:**
```
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_settings.json
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_tearsheet.html
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_tearsheet.csv
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_trades.csv
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_trades.html
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_stats.csv
```

**Run ID:**
The "run ID" is everything before the file type:
```
EMACrossoverStrategy_2025-10-29_14-05_FoWcfI
```

This ID is used to find all files for a specific backtest run.

---

## Strategy Files

### Location
```
Outputs/Strategies/{strategy_name}.py
```

### Structure

**Minimal Required Structure:**
```python
from lumibot.strategies import Strategy

class StrategyClassName(Strategy):
    """
    Strategy description goes here.
    """

    parameters = {
        "symbol": "SPY",
        "timeframe": "1D",
        # ... other parameters
    }

    def initialize(self):
        # Setup code
        pass

    def on_trading_iteration(self):
        # Trading logic
        pass

if __name__ == "__main__":
    # Backtest configuration
    StrategyClassName.backtest(...)
```

**Key Elements:**
- Class inherits from `Strategy`
- Class name matches filename (snake_case → PascalCase)
- `parameters` dictionary contains all strategy parameters
- Docstring contains strategy description

### Parameters Dictionary Schema

(TODO: Fill with actual parameters after analyzing generated strategies)

```python
{
    "symbol": str,      # TODO: Trading symbol (e.g., "SPY")
    "timeframe": str,   # TODO: Bar timeframe (e.g., "1D", "1H")
    # ... other parameters specific to strategy type
}
```

---

## Backtest Output Files

### 1. settings.json

**Purpose:** Stores backtest configuration and parameters

**Location:** `logs/{run_id}_settings.json`

**Schema:**
```json
{
  "name": "string",                    // Strategy name
  "strategy_class": "string",          // Python class name
  "module": "string",                  // Module path
  "parameters": {                      // Strategy parameters
    "symbol": "string",
    "timeframe": "string",
    // ... strategy-specific parameters
  },
  "backtesting_start": "string",       // ISO datetime (e.g., "2022-01-01T00:00:00-05:00")
  "backtesting_end": "string",         // ISO datetime
  "budget": number,                    // Initial capital
  "benchmark_asset": "string",         // Benchmark symbol
  "quote_asset": "object",             // Asset object
  "risk_free_rate": number,            // Annual risk-free rate (decimal)
  "starting_positions": []             // Initial positions array
}
```

**Example:**
```json
{
  "name": "EMACrossoverStrategy",
  "strategy_class": "EMACrossoverStrategy",
  "parameters": {
    "symbol": "SPY",
    "timeframe": "1D",
    "fast_ema_period": 9,
    "slow_ema_period": 21,
    "cash_allocation": 1.0
  },
  "backtesting_start": "2022-01-01T00:00:00-05:00",
  "backtesting_end": "2023-12-31T00:00:00-05:00",
  "budget": 100000,
  "benchmark_asset": "SPY",
  "risk_free_rate": 0.0524
}
```

---

### 2. tearsheet.csv

**Purpose:** Summary performance metrics

**Location:** `logs/{run_id}_tearsheet.csv`

**Schema:**
```csv
Metric,SPY,Strategy
Risk-Free Rate,5.24%,5.24%
Time in Market,69.0%,0.0%
Total Return,3%,0%
CAGR% (Annual Return),1.34%,0.0%
Sharpe,-0.1,-
Max Drawdown,-24.47%,-
... (70+ metrics total)
```

**Columns:**
- `Metric`: Metric name (string)
- `SPY`: Benchmark value (string with formatting)
- `Strategy`: Strategy value (string with formatting)

**Key Metrics** (TODO: Complete list during implementation):
- Total Return
- CAGR% (Annual Return)
- Sharpe
- Sortino
- Max Drawdown
- Volatility (ann.)
- Win Days%
- Best Day / Worst Day
- Beta, Alpha, Correlation

**Data Types:**
- Percentages: Stored as strings with "%" symbol
- Ratios: Stored as strings, may be "-" if undefined
- Dates: Stored as integers (days)

---

### 3. tearsheet.html

**Purpose:** Visual performance report

**Location:** `logs/{run_id}_tearsheet.html`

**Format:** HTML generated by QuantStats library

**Contents:**
- Performance summary table
- Equity curve chart
- Drawdown chart
- Monthly returns heatmap
- Distribution plots
- Rolling metrics charts

**Size:** Typically 300KB - 1MB

**Display:** Can be embedded in iframe or opened in browser

---

### 4. trades.csv

**Purpose:** Complete trade log

**Location:** `logs/{run_id}_trades.csv`

**Schema:**
```csv
time,side,status,filled_quantity,symbol,asset.asset_type,asset.right,asset.strike,asset.expiration,price,type,asset.multiplier,trade_cost
```

**Columns:**
- `time`: Trade timestamp (ISO format)
- `side`: "buy" or "sell"
- `status`: Trade status (e.g., "filled")
- `filled_quantity`: Number of shares/contracts
- `symbol`: Trading symbol
- `asset.asset_type`: "stock", "option", etc.
- `asset.right`: For options: "call" or "put"
- `asset.strike`: For options: strike price
- `asset.expiration`: For options: expiration date
- `price`: Execution price
- `type`: Order type (e.g., "market")
- `asset.multiplier`: Contract multiplier
- `trade_cost`: Commission/fees

**Empty File Case:**
If strategy makes no trades, CSV has only headers (no data rows).

**Example Row:**
```csv
2022-05-15 09:30:00,buy,filled,100,SPY,stock,,,455.23,market,1,10.00
```

---

### 5. trades.html

**Purpose:** Visual trade log

**Location:** `logs/{run_id}_trades.html`

**Format:** HTML table with all trades

**Size:** Varies based on number of trades (can be large)

---

### 6. stats.csv

**Purpose:** Time-series portfolio metrics

**Location:** `logs/{run_id}_stats.csv`

**Schema:**
```csv
datetime,portfolio_value,cash,positions,return
```

**Columns:**
- `datetime`: Timestamp (ISO format)
- `portfolio_value`: Total portfolio value
- `cash`: Available cash
- `positions`: JSON array of positions
- `return`: Cumulative return (decimal)

**Example Rows:**
```csv
2022-01-03 09:30:00-05:00,100000.0,100000.0,[],0.0
2022-01-04 09:30:00-05:00,100000.0,95000.0,"[{'symbol':'SPY','quantity':100,'price':455.23}]",0.0
```

**Positions Format:**
```python
[
    {
        "symbol": "SPY",
        "quantity": 100,
        "price": 455.23
    }
]
```

---

## Directory Structure

### Current File Organization

```
CodeJ/
├── Outputs/
│   ├── Inscructions/           # Strategy instruction files
│   │   ├── ema_crossover_test_instructions.txt
│   │   └── TEMPLATE_zero_loss_butterfly.txt
│   │
│   └── Strategies/             # Generated strategy code
│       ├── ema_crossover_test.py
│       ├── zero_loss_butterfly.py
│       └── ...
│
└── logs/                       # Backtest results (flat structure)
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_settings.json
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_tearsheet.html
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_tearsheet.csv
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_trades.csv
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_trades.html
    ├── EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_stats.csv
    │
    ├── ZeroLossButterfly_2025-10-27_22-22_gPTe82_settings.json
    └── ... (all other backtest files)
```

### Finding Files

**To find all backtests for a strategy:**
```python
import glob
pattern = f"logs/{strategy_class_name}_*_settings.json"
files = glob.glob(pattern)
```

**To find all files for a specific run:**
```python
run_id = "EMACrossoverStrategy_2025-10-29_14-05_FoWcfI"
settings = f"logs/{run_id}_settings.json"
tearsheet_html = f"logs/{run_id}_tearsheet.html"
tearsheet_csv = f"logs/{run_id}_tearsheet.csv"
trades_csv = f"logs/{run_id}_trades.csv"
stats_csv = f"logs/{run_id}_stats.csv"
```

---

## Data Type Reference

### Common Types

**Percentage Values:**
- Stored as: String with "%" (e.g., "12.34%")
- Display as: Formatted string
- Parse with: `float(value.rstrip('%')) / 100`

**Decimal Values:**
- Stored as: String or float
- Display as: Formatted to 2-4 decimals
- Parse with: `float(value)`

**Currency Values:**
- Stored as: Float (dollars)
- Display as: `f"${value:,.2f}"`

**Dates:**
- Stored as: ISO 8601 string (e.g., "2022-01-01T00:00:00-05:00")
- Display as: Formatted date string
- Parse with: `datetime.fromisoformat(value)`

**Undefined Metrics:**
- Stored as: "-" (dash string)
- Display as: "-" or "N/A"
- Parse as: None

---

## Future: Database Schema

**Status:** Out of scope for Phase 1 MVP

See: `Docs/Enhancements.md` for database migration plan

---

**Last Updated:** 2025-10-29 (Template Created)
**Status:** TODO - Will be filled during Step 1 implementation
**Version:** 1.0 (Template)
