# Backend Architecture

**Module:** `strategy_review_manager.py`
**Purpose:** Backend logic for strategy review and backtest management
**Version:** Phase 1 MVP
**Storage:** Flat file system (logs/ and Outputs/Strategies/)

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Class: StrategyLoader](#class-strategyloader)
4. [Class: BacktestManager](#class-backtestmanager)
5. [Utility Functions](#utility-functions)
6. [Data Flow](#data-flow)
7. [Error Handling](#error-handling)
8. [Performance Considerations](#performance-considerations)

---

## Overview

The backend module provides abstraction layer for accessing strategy files and backtest results.

**Key Responsibilities:**
- Discover and parse strategy .py files
- Find and load backtest output files
- Parse JSON/CSV data into usable formats
- Handle missing/corrupt files gracefully
- Provide consistent interface for UI layer

**Design Principles:**
- **Separation of concerns:** Backend doesn't know about UI
- **Error tolerance:** Missing files return None, not exceptions
- **Future-proof:** Easy to swap file access with database queries
- **Type consistency:** Always return same types (dict, DataFrame, None)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Streamlit UI Layer                  │
│  (pages/2_Review_Strategies.py)             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      strategy_review_manager.py             │
│  ┌─────────────────┬──────────────────────┐ │
│  │ StrategyLoader  │  BacktestManager     │ │
│  │                 │                      │ │
│  │ - list()        │  - list()            │ │
│  │ - get_info()    │  - load_results()    │ │
│  │ - extract()     │  - get_tearsheet()   │ │
│  │                 │  - get_metrics()     │ │
│  │                 │  - get_trades()      │ │
│  └─────────────────┴──────────────────────┘ │
│  ┌──────────────────────────────────────┐   │
│  │     Utility Functions                │   │
│  │  - parse_run_id()                    │   │
│  │  - format_metric()                   │   │
│  └──────────────────────────────────────┘   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         File System                         │
│  ┌──────────────────┬──────────────────┐   │
│  │ Outputs/         │  logs/           │   │
│  │   Strategies/    │    *.html        │   │
│  │     *.py         │    *.csv         │   │
│  │                  │    *.json        │   │
│  └──────────────────┴──────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Class: StrategyLoader

**Purpose:** Discover and parse Lumibot strategy files

### Class Definition

```python
class StrategyLoader:
    """
    Handles loading and parsing of Lumibot strategy files.

    Responsibilities:
    - List all strategy .py files in Outputs/Strategies/
    - Extract strategy metadata (name, class, parameters)
    - Parse parameters dictionary from strategy code
    """
```

### Methods

#### `list_strategies() -> List[str]`

**Description:** (TODO: Fill during implementation)

**Parameters:** None

**Returns:**
- Type: `List[str]`
- Description: (TODO: List of strategy filenames)

**Raises:**
- `OSError`: (TODO: If directory doesn't exist)

**Implementation Notes:** (TODO: Add during implementation)

**Example:**
```python
# TODO: Add example during implementation
```

---

#### `get_strategy_info(filepath: str) -> Dict[str, Any]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `filepath` (str): (TODO: Absolute path to strategy .py file)

**Returns:**
- Type: `Dict[str, Any]`
- Description: (TODO: Dictionary with strategy metadata)
- Structure:
  ```python
  {
      "name": str,           # TODO: Strategy filename
      "class_name": str,     # TODO: Strategy class name
      "description": str,    # TODO: Docstring or ""
      "parameters": dict,    # TODO: Parameters dict
      "file_path": str,      # TODO: Absolute path
      "file_size": int,      # TODO: Size in bytes
      "modified_date": str   # TODO: Last modified ISO date
  }
  ```

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Add during implementation)

---

#### `extract_parameters(filepath: str) -> Dict[str, Any]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `filepath` (str): (TODO: Path to strategy file)

**Returns:**
- Type: `Dict[str, Any]`
- Description: (TODO: Parameters dictionary from strategy)

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Explain parsing approach - regex vs AST)

---

## Class: BacktestManager

**Purpose:** Load and parse backtest result files

### Class Definition

```python
class BacktestManager:
    """
    Handles loading and parsing of backtest result files.

    Responsibilities:
    - Find all backtest runs for a strategy
    - Load backtest output files (JSON, CSV, HTML)
    - Parse metrics and trades data
    - Provide consistent data structures to UI
    """
```

### Methods

#### `list_backtests(strategy_name: str) -> List[Dict[str, Any]]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `strategy_name` (str): (TODO: Strategy class name to search for)

**Returns:**
- Type: `List[Dict[str, Any]]`
- Description: (TODO: List of backtest run metadata)
- Structure:
  ```python
  [
      {
          "run_id": str,          # TODO: Unique run identifier
          "date": str,            # TODO: Run date (YYYY-MM-DD)
          "time": str,            # TODO: Run time (HH:MM)
          "symbol": str,          # TODO: Traded symbol
          "start_date": str,      # TODO: Backtest start
          "end_date": str,        # TODO: Backtest end
          "total_return": float,  # TODO: % return
          "sharpe": float,        # TODO: Sharpe ratio
          "max_drawdown": float,  # TODO: % drawdown
          "has_html": bool,       # TODO: Tearsheet exists?
          "has_trades": bool      # TODO: Trades file exists?
      },
      ...
  ]
  ```

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Explain filename parsing)

---

#### `load_backtest_results(run_id: str) -> Dict[str, Any]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `run_id` (str): (TODO: Run identifier from list_backtests())

**Returns:**
- Type: `Dict[str, Any]`
- Description: (TODO: All backtest data)
- Structure:
  ```python
  {
      "settings": dict,       # TODO: From settings.json
      "metrics_df": DataFrame,# TODO: From tearsheet.csv
      "trades_df": DataFrame, # TODO: From trades.csv
      "stats_df": DataFrame,  # TODO: From stats.csv
      "html_path": str,       # TODO: Path to HTML file
      "run_metadata": dict    # TODO: Extracted from files
  }
  ```

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Add during implementation)

---

#### `get_tearsheet_html(run_id: str) -> Optional[str]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `run_id` (str): (TODO: Run identifier)

**Returns:**
- Type: `Optional[str]`
- Description: (TODO: HTML content or None if missing)

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Add during implementation)

---

#### `get_metrics_df(run_id: str) -> Optional[pd.DataFrame]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `run_id` (str): (TODO: Run identifier)

**Returns:**
- Type: `Optional[pd.DataFrame]`
- Description: (TODO: Metrics from tearsheet.csv)
- Columns:
  - `Metric`: Metric name
  - `SPY`: Benchmark value
  - `Strategy`: Strategy value

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Add during implementation)

---

#### `get_trades_df(run_id: str) -> Optional[pd.DataFrame]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `run_id` (str): (TODO: Run identifier)

**Returns:**
- Type: `Optional[pd.DataFrame]`
- Description: (TODO: Trades from trades.csv)
- Columns: (TODO: List column names)

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Handle empty CSV case)

---

#### `get_settings(run_id: str) -> Optional[Dict[str, Any]]`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `run_id` (str): (TODO: Run identifier)

**Returns:**
- Type: `Optional[Dict[str, Any]]`
- Description: (TODO: Settings from settings.json)

**Raises:**
- (TODO: Document exceptions)

**Implementation Notes:** (TODO: Add during implementation)

---

## Utility Functions

### `parse_run_id(filename: str) -> str`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `filename` (str): (TODO: Backtest filename)

**Returns:**
- Type: `str`
- Description: (TODO: Extracted run ID)

**Example:**
```python
# TODO: Add example
# Input: "EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_settings.json"
# Output: "EMACrossoverStrategy_2025-10-29_14-05_FoWcfI"
```

---

### `format_metric(value: Any, metric_type: str) -> str`

**Description:** (TODO: Fill during implementation)

**Parameters:**
- `value` (Any): (TODO: Metric value to format)
- `metric_type` (str): (TODO: Type: 'percent', 'decimal', 'currency')

**Returns:**
- Type: `str`
- Description: (TODO: Formatted string for display)

**Example:**
```python
# TODO: Add examples
# format_metric(0.1234, 'percent') -> "12.34%"
# format_metric(1.5678, 'decimal') -> "1.57"
```

---

## Data Flow

### Loading a Strategy's Backtest Results

```
User selects strategy in UI
         │
         ▼
StrategyLoader.list_strategies()
   → Returns: ["ema_crossover_test.py", ...]
         │
         ▼
User selects "ema_crossover_test.py"
         │
         ▼
BacktestManager.list_backtests("EMACrossoverStrategy")
   → Searches logs/ for pattern: EMACrossoverStrategy_*_settings.json
   → Parses each settings.json
   → Returns: List of run metadata
         │
         ▼
User selects specific run
         │
         ▼
BacktestManager.load_backtest_results(run_id)
   → Loads all files for run
   → Parses JSON/CSV
   → Returns: Complete results dict
         │
         ▼
UI displays results in tabs
```

---

## Error Handling

### Strategy

**Philosophy:** Fail gracefully, log errors, return None instead of crashing

### Missing Files

```python
# TODO: Add error handling examples during implementation

def get_tearsheet_html(run_id):
    html_path = f"logs/{run_id}_tearsheet.html"

    if not os.path.exists(html_path):
        # TODO: Log warning
        return None

    try:
        with open(html_path, 'r') as f:
            return f.read()
    except Exception as e:
        # TODO: Log error
        return None
```

### Corrupt Files

(TODO: Add examples during implementation)

### Invalid Parameters

(TODO: Add examples during implementation)

---

## Performance Considerations

### Caching Strategy

(TODO: Fill during implementation)

**Areas to cache:**
- Strategy list (refresh on button click)
- Backtest list per strategy (refresh on strategy change)
- Loaded backtest results (refresh on run change)

### Lazy Loading

(TODO: Fill during implementation)

**What to lazy load:**
- Tearsheet HTML (only when Results tab opened)
- Trades DataFrame (only when Trades tab opened)

### Optimization Opportunities

(TODO: Fill during implementation)

---

## Future Enhancements

*See: Docs/Enhancements.md for detailed plans*

**Database Integration:**
- Replace file parsing with SQL queries
- Keep file access for backward compatibility
- Hybrid approach during migration

**Advanced Features:**
- Backtest execution from UI
- Parameter optimization
- Multi-run comparison

---

**Last Updated:** 2025-10-29 (Template Created)
**Status:** TODO - Will be filled during Step 1 implementation
**Version:** 1.0 (Template)
