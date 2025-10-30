# Future Enhancements

**Purpose:** Document planned features, improvements, and out-of-scope items
**Status:** Planning document for Phase 2, Phase 3, and beyond
**Last Updated:** 2025-10-29

---

## Table of Contents

1. [Phase 2: Run Backtests from UI](#phase-2-run-backtests-from-ui)
2. [Phase 3: Comparison Features](#phase-3-comparison-features)
3. [Database Migration](#database-migration)
4. [Advanced Analytics](#advanced-analytics)
5. [Performance Optimization](#performance-optimization)
6. [Out of Scope](#out-of-scope)

---

## Phase 2: Run Backtests from UI

**Status:** Planned
**Estimated Time:** 10-15 hours
**Priority:** High
**Dependencies:** Phase 1 must be complete

### Overview

Add capability to run new backtests directly from the Review Strategies page without using command line.

### Features

#### 2.1 Parameter Editor

**Objective:** Allow users to modify backtest parameters before running

**UI Components:**
- Symbol input field (dropdown with common symbols or text input)
- Date range picker (start date, end date)
- Initial capital input (numeric)
- Commission rate input (percentage)
- Strategy-specific parameters (dynamic based on strategy.parameters)

**Implementation:**
```python
# Parse current parameters from strategy file
params = StrategyLoader.extract_parameters(strategy_file)

# Display in Streamlit form
with st.form("backtest_params"):
    symbol = st.text_input("Symbol", value=params.get("symbol", "SPY"))
    start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
    end_date = st.date_input("End Date", value=datetime(2023, 12, 31))

    # Dynamic parameters
    for param_name, param_value in params.items():
        if param_name not in ["symbol", "timeframe"]:
            # Create appropriate input widget based on type
            pass

    submit = st.form_submit_button("Run Backtest")
```

**Validation:**
- Start date must be before end date
- Symbol must be valid (regex pattern)
- Numeric parameters must be in valid ranges
- Required parameters must be filled

#### 2.2 Background Execution

**Objective:** Run backtests without blocking UI

**Challenges:**
- Backtests can take 30 seconds to several minutes
- Streamlit reruns on every interaction
- Need to show progress without freezing

**Solution A: Subprocess with Monitoring**
```python
import subprocess
import time

# Write temporary backtest script
temp_script = create_temp_backtest_script(strategy, params)

# Run in subprocess
process = subprocess.Popen(
    [sys.executable, temp_script],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Store in session state
st.session_state['running_backtest'] = {
    'pid': process.pid,
    'strategy': strategy_name,
    'started': datetime.now(),
    'params': params
}

# Monitor logs/ directory for new files
while process.poll() is None:
    time.sleep(1)
    # Check for new files with current timestamp
    new_files = find_new_backtest_files(strategy_name, started_time)
    if new_files:
        st.success("Backtest complete!")
        break
```

**Solution B: Threading with Progress**
```python
from concurrent.futures import ThreadPoolExecutor
import threading

# Session state executor
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=1)

# Submit backtest
def run_backtest_task(strategy, params):
    # Import strategy class
    # Call .backtest() method
    # Return results
    pass

future = st.session_state.executor.submit(run_backtest_task, strategy, params)
st.session_state['backtest_future'] = future

# Check completion
if future.done():
    result = future.result()
    st.success("Complete!")
else:
    st.info("Running... " + get_elapsed_time())
```

**Recommended:** Solution A (subprocess) - more reliable, easier to cancel

#### 2.3 Progress Tracking

**Objective:** Show backtest progress to user

**UI Elements:**
- Progress bar (estimated % complete)
- Elapsed time
- Status messages
- Cancel button

**Implementation:**
```python
# Option 1: Estimate progress from file size
stats_file = f"logs/{expected_run_id}_stats.csv"
if os.path.exists(stats_file):
    # Count lines in stats.csv
    lines = count_lines(stats_file)
    total_days = (end_date - start_date).days
    progress = min(100, (lines / total_days) * 100)
    st.progress(progress / 100)

# Option 2: Parse log output
# Redirect stdout/stderr to log file
# Parse for progress indicators
```

#### 2.4 Result Notification

**Objective:** Alert user when backtest completes

**Approaches:**
- Auto-refresh page when files appear
- Success message with metrics preview
- Auto-select new run in results list

**Implementation:**
```python
# Auto-refresh every 5 seconds while running
if 'running_backtest' in st.session_state:
    time.sleep(5)
    st.rerun()

# When complete, show summary
st.success(f"""
Backtest Complete!
- Total Return: {metrics['total_return']}
- Sharpe Ratio: {metrics['sharpe']}
- Max Drawdown: {metrics['max_drawdown']}
""")

# Auto-select in dropdown
st.session_state['selected_backtest'] = new_run_id
```

### Deliverables

- Parameter editor UI
- Background execution system
- Progress tracking
- Error handling for failed backtests
- Updated documentation

### Estimated Time: 10-15 hours

---

## Phase 3: Comparison Features

**Status:** Planned
**Estimated Time:** 8-12 hours
**Priority:** Medium
**Dependencies:** Phase 1 complete, Phase 2 optional

### Overview

Compare multiple backtest runs side-by-side to analyze strategy performance across different parameters or time periods.

### Features

#### 3.1 Multi-Run Selection

**Objective:** Allow selecting 2+ runs for comparison

**UI Components:**
- Multi-select dropdown (select 2-5 runs)
- Filter by date range
- Filter by symbol
- Sort by performance metric

**Implementation:**
```python
# Multi-select widget
selected_runs = st.multiselect(
    "Select runs to compare",
    options=available_runs,
    format_func=lambda run: f"{run['date']} - {run['symbol']} ({run['total_return']})"
)

# Limit to 5 runs max
if len(selected_runs) > 5:
    st.error("Maximum 5 runs can be compared at once")
```

#### 3.2 Metrics Comparison Table

**Objective:** Display metrics side-by-side

**Layout:**
```
┌─────────────────┬──────────┬──────────┬──────────┐
│ Metric          │  Run 1   │  Run 2   │  Run 3   │
├─────────────────┼──────────┼──────────┼──────────┤
│ Total Return    │   5.2%   │   3.1%   │  -1.5%   │
│ Sharpe Ratio    │   0.85   │   0.62   │  -0.12   │
│ Max Drawdown    │  -12.3%  │  -15.7%  │  -8.9%   │
│ Win Rate        │   55%    │   52%    │   48%    │
│ Calmar Ratio    │   0.42   │   0.20   │  -0.17   │
└─────────────────┴──────────┴──────────┴──────────┘
```

**Implementation:**
```python
# Load metrics for each run
metrics_list = [get_metrics_df(run_id) for run_id in selected_runs]

# Combine into comparison table
comparison_df = pd.DataFrame({
    'Metric': metrics_list[0]['Metric'],
    'Run 1': metrics_list[0]['Strategy'],
    'Run 2': metrics_list[1]['Strategy'],
    # ...
})

# Highlight best/worst values
st.dataframe(comparison_df.style.highlight_max(axis=1, color='lightgreen')
                              .highlight_min(axis=1, color='lightcoral'))
```

#### 3.3 Parameter Difference Highlighting

**Objective:** Show which parameters differ between runs

**UI:**
```
Parameters:
  Symbol: SPY (all runs) ✓
  Fast EMA: 9 | 12 | 9  ⚠ differs
  Slow EMA: 21 (all runs) ✓
  Period: 2022-2023 | 2023-2024 | 2021-2022  ⚠ differs
```

**Implementation:**
```python
# Compare parameters
params_list = [get_settings(run_id)['parameters'] for run_id in selected_runs]

for param_name in param_keys:
    values = [p.get(param_name) for p in params_list]

    if all_same(values):
        st.success(f"{param_name}: {values[0]} (all runs)")
    else:
        st.warning(f"{param_name}: {' | '.join(map(str, values))} (differs)")
```

#### 3.4 Performance Charts

**Objective:** Overlay equity curves and drawdowns

**Charts:**
- Equity curve overlay (all runs on same chart)
- Drawdown comparison
- Monthly returns heatmap comparison
- Risk/return scatter plot

**Implementation:**
```python
import plotly.graph_objects as go

# Load stats.csv for each run
stats_list = [pd.read_csv(f"logs/{run_id}_stats.csv") for run_id in selected_runs]

# Create overlay chart
fig = go.Figure()

for i, stats in enumerate(stats_list):
    fig.add_trace(go.Scatter(
        x=stats['datetime'],
        y=stats['portfolio_value'],
        name=f"Run {i+1}",
        mode='lines'
    ))

fig.update_layout(
    title="Equity Curve Comparison",
    xaxis_title="Date",
    yaxis_title="Portfolio Value"
)

st.plotly_chart(fig)
```

#### 3.5 Export Comparison Report

**Objective:** Download comparison as PDF/Excel

**Formats:**
- CSV: Metrics comparison table
- Excel: Multiple sheets (metrics, parameters, trades)
- PDF: Full report with charts (future)

**Implementation:**
```python
# Excel export with multiple sheets
with pd.ExcelWriter('comparison.xlsx') as writer:
    metrics_df.to_excel(writer, sheet_name='Metrics')
    params_df.to_excel(writer, sheet_name='Parameters')

    for i, run_id in enumerate(selected_runs):
        trades_df = get_trades_df(run_id)
        trades_df.to_excel(writer, sheet_name=f'Trades Run {i+1}')

# Download button
with open('comparison.xlsx', 'rb') as f:
    st.download_button(
        label="Download Comparison Report",
        data=f,
        file_name="backtest_comparison.xlsx",
        mime="application/vnd.ms-excel"
    )
```

### Deliverables

- Multi-run selection UI
- Comparison table with highlighting
- Parameter diff display
- Performance overlay charts
- Export functionality

### Estimated Time: 8-12 hours

---

## Database Migration

**Status:** Future Enhancement
**Priority:** Low (Phase 1 MVP works well with flat files)
**Timing:** Consider after 50+ backtest runs or when queries slow down

### Rationale

**When to Migrate:**
- More than 100 backtest runs
- Search/filter operations become slow
- Need aggregation across all runs
- Multi-user access required
- Want historical trend analysis

**Why SQLite:**
- Single file database (easy backup)
- No server required (embedded in Python)
- Fast queries with indexing
- Standard SQL interface
- Easy to add later without breaking existing code

### Database Schema

#### Table: strategies
```sql
CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,        -- e.g., "ema_crossover_test"
    class_name TEXT NOT NULL,         -- e.g., "EMACrossoverStrategy"
    file_path TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: backtests
```sql
CREATE TABLE backtests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,      -- e.g., "EMACrossoverStrategy_2025-10-29_14-05_FoWcfI"
    strategy_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital REAL,
    commission_rate REAL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Performance metrics (denormalized for fast queries)
    total_return REAL,
    cagr REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    max_drawdown REAL,
    volatility REAL,
    win_rate REAL,
    num_trades INTEGER,

    -- File paths
    settings_file TEXT,
    tearsheet_html_file TEXT,
    tearsheet_csv_file TEXT,
    trades_csv_file TEXT,
    stats_csv_file TEXT,

    FOREIGN KEY (strategy_id) REFERENCES strategies(id)
);

CREATE INDEX idx_backtests_strategy ON backtests(strategy_id);
CREATE INDEX idx_backtests_symbol ON backtests(symbol);
CREATE INDEX idx_backtests_date ON backtests(start_date, end_date);
CREATE INDEX idx_backtests_return ON backtests(total_return);
```

#### Table: backtest_parameters
```sql
CREATE TABLE backtest_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_id INTEGER NOT NULL,
    param_name TEXT NOT NULL,
    param_value TEXT,              -- JSON string for complex types

    FOREIGN KEY (backtest_id) REFERENCES backtests(id)
);

CREATE INDEX idx_params_backtest ON backtest_parameters(backtest_id);
```

#### Table: trades
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    side TEXT NOT NULL,            -- 'buy' or 'sell'
    symbol TEXT NOT NULL,
    quantity INTEGER,
    price REAL,
    trade_cost REAL,
    asset_type TEXT,               -- 'stock', 'option'
    strike REAL,                   -- for options
    expiration DATE,               -- for options

    FOREIGN KEY (backtest_id) REFERENCES backtests(id)
);

CREATE INDEX idx_trades_backtest ON trades(backtest_id);
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
```

### Migration Plan

#### Step 1: Add Database Layer (No Breaking Changes)

```python
class BacktestManager:
    def __init__(self, use_db=False):
        self.use_db = use_db
        if use_db:
            self.db = sqlite3.connect('backtest_results.db')
            self._init_schema()

    def list_backtests(self, strategy_name):
        if self.use_db:
            # Try database first
            results = self._list_from_db(strategy_name)
            if results:
                return results

        # Fallback to file parsing
        return self._list_from_files(strategy_name)
```

#### Step 2: One-Time Migration Script

```python
# migrate_to_db.py

import sqlite3
import glob
import json

db = sqlite3.connect('backtest_results.db')

# Scan all settings.json files
for settings_file in glob.glob("logs/*_settings.json"):
    run_id = parse_run_id(settings_file)

    # Parse settings
    with open(settings_file) as f:
        settings = json.load(f)

    # Parse tearsheet metrics
    tearsheet_csv = settings_file.replace('_settings.json', '_tearsheet.csv')
    if os.path.exists(tearsheet_csv):
        metrics = pd.read_csv(tearsheet_csv)

    # Insert into database
    db.execute("""
        INSERT INTO backtests (run_id, strategy_id, symbol, start_date, ...)
        VALUES (?, ?, ?, ?, ...)
    """, (...))

    # Parse and insert trades
    trades_csv = settings_file.replace('_settings.json', '_trades.csv')
    if os.path.exists(trades_csv):
        trades = pd.read_csv(trades_csv)
        for _, trade in trades.iterrows():
            db.execute("INSERT INTO trades (...) VALUES (...)", (...))

db.commit()
```

#### Step 3: Gradual Transition

- Keep both file access and DB access working
- New backtests auto-insert to DB
- Old backtests migrate on-demand when accessed
- Eventually phase out file parsing

### Benefits After Migration

**Fast Queries:**
```sql
-- Find best performing backtests
SELECT run_id, total_return, sharpe_ratio
FROM backtests
WHERE strategy_id = ?
ORDER BY total_return DESC
LIMIT 10;

-- Compare parameters across runs
SELECT b.run_id, p.param_name, p.param_value
FROM backtests b
JOIN backtest_parameters p ON b.id = p.backtest_id
WHERE b.strategy_id = ?;

-- Aggregate statistics
SELECT symbol,
       AVG(total_return) as avg_return,
       AVG(sharpe_ratio) as avg_sharpe,
       COUNT(*) as num_runs
FROM backtests
GROUP BY symbol;
```

**Advanced Features:**
- Search by performance thresholds
- Parameter optimization (grid search results)
- Historical trend analysis
- Multi-strategy comparison

### Estimated Time: 15-20 hours

---

## Advanced Analytics

**Status:** Future Ideas
**Priority:** Low
**Dependencies:** Phase 3 comparison features

### Features

#### Performance Dashboard
- Aggregate metrics across all strategies
- Best/worst performing periods
- Strategy win rate over time
- Risk-adjusted return rankings

#### Parameter Optimization
- Grid search results visualization
- Parameter sensitivity analysis
- Optimal parameter discovery
- Walk-forward optimization

#### Risk Analytics
- Value at Risk (VaR) analysis
- Stress testing scenarios
- Correlation analysis between strategies
- Portfolio-level metrics

#### Alerts and Notifications
- Email when backtest completes
- Alert on performance thresholds
- Scheduled backtests (daily/weekly)
- Performance degradation warnings

### Estimated Time: 20-30 hours

---

## Performance Optimization

**Status:** Future Improvements
**Priority:** Low (implement if performance issues arise)

### Caching Strategies

#### Client-Side Caching
```python
@st.cache_data(ttl=3600)
def load_backtest_results(run_id):
    # Cached for 1 hour
    return BacktestManager.load_backtest_results(run_id)
```

#### Server-Side Caching
```python
# LRU cache for frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=50)
def get_tearsheet_html(run_id):
    # Keep 50 most recent in memory
    ...
```

### Lazy Loading

- Load tearsheet HTML only when tab opened
- Paginate trades table for large result sets
- Stream large CSV files instead of loading entire file

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

# Load multiple backtests in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(load_backtest_results, run_ids))
```

### Estimated Time: 5-10 hours

---

## Out of Scope

**Items NOT planned for any phase:**

### Real-Time Trading
- Live strategy execution
- Broker integration
- Real-time position monitoring

*Rationale:* Lumibot already provides this via broker connectors. Review feature is for backtesting only.

### Strategy Development IDE
- Code editor in browser
- Syntax highlighting
- Interactive debugging

*Rationale:* Use VS Code or preferred IDE for development. Review feature is for analysis, not development.

### Machine Learning Integration
- Auto-strategy generation
- ML-based parameter optimization
- Neural network strategies

*Rationale:* Complex scope. Use separate tools for ML. Import generated strategies as .py files.

### Multi-User Collaboration
- Shared backtest repository
- Comments and annotations
- Access control

*Rationale:* Single-user tool. For teams, use git for collaboration.

### Mobile App
- iOS/Android app
- Mobile-optimized UI

*Rationale:* Streamlit web app is responsive. Full mobile app not justified for complexity.

---

**Last Updated:** 2025-10-29
**Status:** Planning Document
**Version:** 1.0
