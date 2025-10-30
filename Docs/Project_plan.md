# Strategy Review Feature - Project Plan

## Overview

**Feature Name:** Strategy Review & Backtest Management
**Version:** Phase 1 MVP
**Start Date:** 2025-10-29
**Estimated Completion:** 9-13 hours

**Purpose:**
Add a "Review Strategies" page to the Streamlit app that allows users to:
- View all generated Lumibot strategies
- Browse previous backtest runs
- Display backtest results (tearsheets, metrics, trades)
- Download backtest output files

**Approach:**
- Phase 1 (MVP): Read-only review of existing backtests using flat file storage
- Future phases: Run new backtests, compare runs, migrate to database

---

## Phase 1: Strategy Review (MVP) - 8-12 hours

### Step 0: Documentation Setup (1 hour)

**Objective:** Create documentation structure for project tracking

**Action Items:**

- [x] Create Docs/ directory structure
- [ ] Create Docs/Project_plan.md template
- [ ] Create Docs/Changelog.md template
- [ ] Create Docs/Backend.md template
- [ ] Create Docs/Schemas.md template
- [ ] Create Docs/Enhancements.md template

**Deliverables:**
- 5 documentation template files
- Initial git commit

**Time Estimate:** 1 hour

---

### Step 1: Backend Module (3-4 hours)

**Objective:** Create `strategy_review_manager.py` module with strategy and backtest loading functionality

**Dependencies:** None

#### 1.1 Create Module File

**Action Items:**

- [ ] Create `strategy_review_manager.py` in project root
- [ ] Add module docstring
- [ ] Add import statements (glob, json, pandas, pathlib, re)
- [ ] Update Changelog: `feat: Initialize strategy review backend module`

**Time Estimate:** 15 minutes

#### 1.2 Implement StrategyLoader Class

**Action Items:**

- [ ] Create StrategyLoader class with docstring
- [ ] Implement `list_strategies()` method
  - Glob `Outputs/Strategies/*.py`
  - Return list of strategy filenames
  - Handle empty directory
- [ ] Implement `get_strategy_info(filepath)` method
  - Parse strategy file for class name
  - Extract docstring
  - Return dict with metadata
- [ ] Implement `extract_parameters(filepath)` method
  - Parse `parameters = {}` dictionary from file
  - Use regex or AST parsing
  - Return parameters dict
- [ ] Add error handling for missing/corrupt files
- [ ] Update Backend.md: Add StrategyLoader API specification
- [ ] Update Changelog: `feat: Add StrategyLoader class with strategy discovery`

**Time Estimate:** 1-1.5 hours

#### 1.3 Implement BacktestManager Class

**Action Items:**

- [ ] Create BacktestManager class with docstring
- [ ] Implement `list_backtests(strategy_name)` method
  - Glob `logs/{strategy_name}_*_settings.json`
  - Parse each settings.json for metadata
  - Return list of backtest runs with key metrics
- [ ] Implement `load_backtest_results(run_id)` method
  - Load all files for a run
  - Return dict with parsed data
- [ ] Implement `get_tearsheet_html(run_id)` method
  - Read HTML file
  - Return HTML string or None
- [ ] Implement `get_metrics_df(run_id)` method
  - Parse tearsheet.csv
  - Return pandas DataFrame
- [ ] Implement `get_trades_df(run_id)` method
  - Parse trades.csv
  - Return pandas DataFrame (empty if no trades)
- [ ] Implement `get_settings(run_id)` method
  - Parse settings.json
  - Return dict
- [ ] Update Backend.md: Add BacktestManager API specification
- [ ] Update Schemas.md: Document file naming patterns
- [ ] Update Changelog: `feat: Add BacktestManager class with result loading`

**Time Estimate:** 1.5-2 hours

#### 1.4 Add Utility Functions

**Action Items:**

- [ ] Implement `parse_run_id(filename)` function
  - Extract run ID from filename pattern
  - Return ID string
- [ ] Implement `format_metric(value, metric_type)` function
  - Format metrics for display (percentages, decimals)
  - Return formatted string
- [ ] Add comprehensive error handling
  - Missing files → log warning, return None
  - Corrupt JSON/CSV → log error, return default
- [ ] Update Backend.md: Document utility functions
- [ ] Update Changelog: `feat: Add utility functions for file parsing`

**Time Estimate:** 30-45 minutes

**Step 1 Deliverables:**
- `strategy_review_manager.py` (fully functional backend module)
- Updated Backend.md (complete API documentation)
- Updated Schemas.md (file patterns and structures)
- 4 Changelog entries
- 4 git commits

**Step 1 Total Time:** 3-4 hours

---

### Step 2: Review Page UI (4-5 hours)

**Objective:** Create Streamlit multi-page app with Review Strategies page

**Dependencies:** Step 1 (backend module must be complete)

#### 2.1 Create Multi-Page App Structure

**Action Items:**

- [ ] Create `pages/` directory
- [ ] Rename `lumibot_strategy_generator_enhanced.py` → `pages/1_Generate_Strategy.py`
- [ ] Update imports and paths in renamed file
- [ ] Test that existing app still works
- [ ] Create `pages/2_Review_Strategies.py` skeleton file
- [ ] Create `Home.py` (optional landing page with navigation)
- [ ] Update Changelog: `refactor: Convert to multi-page Streamlit app`

**Time Estimate:** 30 minutes

#### 2.2 Implement Page Header and Setup

**Action Items:**

- [ ] Add page config (title, icon, layout)
- [ ] Import strategy_review_manager
- [ ] Add page title and description
- [ ] Initialize session state variables
  - `selected_strategy`
  - `selected_backtest`
  - `backtest_cache`
- [ ] Update Changelog: `feat: Add Review Strategies page skeleton`

**Time Estimate:** 20 minutes

#### 2.3 Build Sidebar Controls

**Action Items:**

- [ ] Create strategy selector dropdown
  - Use StrategyLoader.list_strategies()
  - Display strategy names
  - Store selection in session state
- [ ] Create backtest run selector
  - Use BacktestManager.list_backtests(selected_strategy)
  - Display run date/time and key metrics
  - Store selection in session state
- [ ] Add date range filter (optional)
- [ ] Add refresh button to reload data
- [ ] Update Changelog: `feat: Add strategy and backtest selection controls`

**Time Estimate:** 45 minutes

#### 2.4 Create Overview Tab

**Action Items:**

- [ ] Create tab container (4 tabs: Overview, Results, Trades, Downloads)
- [ ] In Overview tab:
  - Display strategy name and class
  - Show strategy docstring/description
  - Display parameters table
  - Show file info (path, size, last modified)
- [ ] Update Changelog: `feat: Add strategy overview tab`

**Time Estimate:** 30 minutes

#### 2.5 Create Backtest Results Tab

**Action Items:**

- [ ] Add metrics summary cards at top
  - Total Return
  - Sharpe Ratio
  - Max Drawdown
  - Win Rate
- [ ] Display full metrics table from tearsheet.csv
  - Use st.dataframe with formatting
  - Highlight key metrics
- [ ] Add tearsheet HTML iframe
  - Use st.components.v1.html()
  - Set height and scrolling
  - Handle missing HTML gracefully
- [ ] Update Changelog: `feat: Add backtest results visualization tab`

**Time Estimate:** 1 hour

#### 2.6 Create Trades Tab

**Action Items:**

- [ ] Display trades dataframe
  - Use st.dataframe with filtering
  - Format currency columns
  - Color code buy/sell
- [ ] Add column filters
- [ ] Add sort controls
- [ ] Handle empty trades.csv case
  - Show "No trades executed" message
- [ ] Update Changelog: `feat: Add trades analysis tab`

**Time Estimate:** 30 minutes

#### 2.7 Create Downloads Tab

**Action Items:**

- [ ] List all files for selected backtest run
  - tearsheet.html, tearsheet.csv
  - trades.csv, trades.html
  - stats.csv, settings.json
- [ ] Add individual download button for each file
  - Use st.download_button
  - Display file size
- [ ] Add "Download All as ZIP" button
  - Create ZIP archive in memory
  - Download all backtest files
- [ ] Update Changelog: `feat: Add backtest file download functionality`

**Time Estimate:** 45 minutes

**Step 2 Deliverables:**
- `pages/1_Generate_Strategy.py` (renamed from main)
- `pages/2_Review_Strategies.py` (complete with 4 tabs)
- `Home.py` (optional)
- 7 Changelog entries
- 7 git commits

**Step 2 Total Time:** 4-5 hours

---

### Step 3: Styling and Error Handling (1-2 hours)

**Objective:** Polish UI and add comprehensive error handling

**Dependencies:** Step 2 (UI must be functional)

#### 3.1 Apply Consistent Styling

**Action Items:**

- [ ] Copy CSS from `pages/1_Generate_Strategy.py`
- [ ] Apply to Review page
- [ ] Add info boxes for metric highlights
- [ ] Ensure responsive layout
- [ ] Test on different screen sizes
- [ ] Update Changelog: `style: Apply consistent CSS to review page`

**Time Estimate:** 30 minutes

#### 3.2 Implement Error Handling

**Action Items:**

- [ ] Handle missing strategy files
  - Show "No strategies found" message
  - Provide link to generator page
- [ ] Handle missing backtest files
  - Show "No backtests found for this strategy"
  - Suggest running a backtest
- [ ] Handle corrupted JSON/CSV files
  - Log error to console
  - Show user-friendly error message
  - Allow continuing with partial data
- [ ] Handle missing tearsheet HTML
  - Show CSV metrics instead
  - Display "Tearsheet not available" message
- [ ] Update Changelog: `fix: Add comprehensive error handling`

**Time Estimate:** 30-45 minutes

#### 3.3 Performance Optimization

**Action Items:**

- [ ] Cache loaded backtest results in session state
  - Avoid re-loading same run
  - Clear cache on strategy change
- [ ] Lazy load tearsheet HTML
  - Only load when Results tab is opened
  - Show loading spinner
- [ ] Optimize dataframe rendering
  - Use st.dataframe instead of st.table for large data
  - Implement pagination if needed
- [ ] Update Changelog: `perf: Add caching and lazy loading`

**Time Estimate:** 20-30 minutes

**Step 3 Deliverables:**
- Polished UI with consistent styling
- Comprehensive error handling
- Performance optimizations
- 3 Changelog entries
- 3 git commits

**Step 3 Total Time:** 1-2 hours

---

### Step 4: Testing and Documentation (1-2 hours)

**Objective:** Test all functionality and complete documentation

**Dependencies:** Steps 1-3 (all code must be complete)

#### 4.1 Test with Existing Data

**Action Items:**

- [ ] Load ema_crossover_test strategy
- [ ] View backtest run from 2025-10-29
- [ ] Verify tearsheet HTML displays correctly
- [ ] Check all tabs render properly
- [ ] Test file downloads work
- [ ] Verify metrics match actual backtest results
- [ ] Update Changelog: `test: Verify review page with existing backtests`

**Time Estimate:** 20 minutes

#### 4.2 Test Error Cases

**Action Items:**

- [ ] Test with no strategies (delete/move .py files temporarily)
- [ ] Test with no backtests (empty logs/ directory)
- [ ] Test with missing tearsheet HTML
- [ ] Test with empty trades.csv
- [ ] Test with corrupted JSON file
- [ ] Verify all error messages display correctly
- [ ] Update Changelog: `test: Verify error handling edge cases`

**Time Estimate:** 20 minutes

#### 4.3 Complete Documentation

**Action Items:**

- [ ] Fill all TODO sections in Backend.md
  - Complete API specifications
  - Add data flow diagrams (ASCII/markdown)
  - Document error handling approach
- [ ] Fill all TODO sections in Schemas.md
  - Complete file format specifications
  - Add example JSON structures
  - Document data types
- [ ] Update Project_plan.md
  - Check off completed items
  - Add usage examples
  - Update time estimates with actuals
- [ ] Move future features to Enhancements.md
  - Phase 2 details
  - Phase 3 details
  - Database migration plan
- [ ] Update Changelog: `docs: Complete Phase 1 documentation`

**Time Estimate:** 30 minutes

#### 4.4 Add Code Documentation

**Action Items:**

- [ ] Ensure all classes have comprehensive docstrings
- [ ] Ensure all methods have docstrings with:
  - Description
  - Parameters (with types)
  - Returns (with types)
  - Raises (exceptions)
- [ ] Add inline comments for complex logic
- [ ] Update Changelog: `docs: Add comprehensive docstrings`

**Time Estimate:** 20 minutes

**Step 4 Deliverables:**
- Fully tested review page
- Complete documentation (all 5 files)
- All code documented with docstrings
- 4 Changelog entries
- 4 git commits

**Step 4 Total Time:** 1-2 hours

---

## Phase 2: Run Backtests from UI (Future)

**Status:** Planned - Not in Phase 1 MVP

**Estimated Time:** 10-15 hours

**Features:**
- Parameter modification UI
- Background backtest execution
- Progress tracking
- Real-time log streaming

See: `Docs/Enhancements.md` for detailed plan

---

## Phase 3: Comparison Features (Future)

**Status:** Planned - Not in Phase 1 MVP

**Estimated Time:** 8-12 hours

**Features:**
- Multi-run selection
- Side-by-side metric comparison
- Performance charts overlay
- Export comparison reports

See: `Docs/Enhancements.md` for detailed plan

---

## Status Tracking

### Overall Progress

- [ ] **Phase 1: Strategy Review (MVP)** - 8-12 hours
  - [ ] Step 0: Documentation Setup (1 hour)
  - [ ] Step 1: Backend Module (3-4 hours)
  - [ ] Step 2: Review Page UI (4-5 hours)
  - [ ] Step 3: Styling & Error Handling (1-2 hours)
  - [ ] Step 4: Testing & Documentation (1-2 hours)

### Detailed Task Checklist

**Step 0: Documentation (1 hour)**
- [x] Create Docs/ directory
- [ ] Create Project_plan.md
- [ ] Create Changelog.md
- [ ] Create Backend.md
- [ ] Create Schemas.md
- [ ] Create Enhancements.md

**Step 1: Backend Module (3-4 hours)**
- [ ] 1.1: Create module file
- [ ] 1.2: StrategyLoader class
- [ ] 1.3: BacktestManager class
- [ ] 1.4: Utility functions

**Step 2: UI Implementation (4-5 hours)**
- [ ] 2.1: Multi-page structure
- [ ] 2.2: Page header/setup
- [ ] 2.3: Sidebar controls
- [ ] 2.4: Overview tab
- [ ] 2.5: Results tab
- [ ] 2.6: Trades tab
- [ ] 2.7: Downloads tab

**Step 3: Polish (1-2 hours)**
- [ ] 3.1: Styling
- [ ] 3.2: Error handling
- [ ] 3.3: Performance

**Step 4: Testing & Docs (1-2 hours)**
- [ ] 4.1: Test with real data
- [ ] 4.2: Test error cases
- [ ] 4.3: Complete docs
- [ ] 4.4: Add docstrings

---

## Success Criteria

### Functional Requirements
- ✅ User can navigate to "Review Strategies" page
- ✅ User can select any strategy from Outputs/Strategies/
- ✅ User can see list of all backtest runs for selected strategy
- ✅ User can view tearsheet HTML inline
- ✅ User can see metrics table from tearsheet.csv
- ✅ User can see trades table from trades.csv
- ✅ User can download individual or all backtest files
- ✅ Error messages display for missing/corrupt files

### Documentation Requirements
- ✅ All 5 documentation files created and complete
- ✅ Changelog has detailed entry for each commit (~18 entries)
- ✅ Backend.md documents all classes/methods
- ✅ Schemas.md documents all file formats
- ✅ Enhancements.md contains Phase 2/3 plans

### Code Quality
- ✅ All classes have docstrings
- ✅ All methods have parameter/return type docs
- ✅ Complex logic has inline comments
- ✅ Error handling covers all edge cases
- ✅ Page loads in <2 seconds with caching

---

## Dependencies

### Required Packages (Already Installed)
- streamlit
- pandas
- json (stdlib)
- glob (stdlib)
- pathlib (stdlib)

### Optional Packages (Not Required for Phase 1)
- plotly (for future charts in Phase 3)
- zipfile (stdlib - for download all feature)

---

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Large HTML files don't render | Medium | Low | Use iframe with scrolling, fall back to CSV metrics |
| Missing/corrupt backtest files | Medium | Medium | Comprehensive error handling, graceful degradation |
| Performance issues with many backtests | Low | Low | Caching, lazy loading, pagination if needed |
| Multi-page navigation confusing | Low | Low | Clear navigation, breadcrumbs, consistent styling |

---

## Notes

- Keep Phase 1 scope tight - read-only review only
- Document everything for future developers
- Test with existing ema_crossover_test backtest
- Prepare for database migration in Phase 2

---

**Last Updated:** 2025-10-29
**Updated By:** Claude Code Agent
**Version:** 1.0 (Phase 1 MVP Planning)
