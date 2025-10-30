# Changelog

All notable changes to the Strategy Review feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Documentation templates (Project_plan.md, Changelog.md, Backend.md, Schemas.md, Enhancements.md)
- Backend module: strategy_review_manager.py (750+ lines)
- StrategyLoader class for strategy file discovery and parsing
- BacktestManager class for backtest result loading
- Utility functions: parse_run_id(), format_metric()

### Changed
- (TODO: Will be filled as we implement)

### Fixed
- (TODO: Will be filled as we implement)

### Deprecated
- (TODO: Will be filled as applicable)

### Removed
- (TODO: Will be filled as applicable)

### Security
- (TODO: Will be filled as applicable)

---

## [0.1.0] - Phase 1 MVP - Target

### Planned Features

**Strategy Review Capabilities:**
- List all generated Lumibot strategies from Outputs/Strategies/
- Display strategy information (name, class, parameters)
- Browse backtest history for each strategy
- View backtest results (tearsheet HTML, metrics CSV, trades CSV)
- Download backtest output files (individual or ZIP all)

**UI Enhancements:**
- Multi-page Streamlit app structure
- Review Strategies page with 4 tabs (Overview, Results, Trades, Downloads)
- Consistent styling with existing generator page
- Comprehensive error handling for missing/corrupt files
- Performance optimization (caching, lazy loading)

**Backend Module:**
- StrategyLoader class for strategy file parsing
- BacktestManager class for backtest result loading
- Utility functions for file parsing and formatting

**Documentation:**
- Complete project plan with phased approach
- Backend architecture and API specifications
- Data schemas for all file formats
- Changelog with detailed semantic versioning
- Enhancements document for future phases

---

## Commit History

### [feat]: Initialize strategy review backend module
**Date:** 2025-10-29
**Commit:** [pending]
**Files Changed:** strategy_review_manager.py

Created backend module with StrategyLoader and BacktestManager classes.

**StrategyLoader Features:**
- list_strategies(): Discover all .py files in Outputs/Strategies/
- get_strategy_info(): Extract class name, docstring, parameters
- extract_parameters(): Parse parameters dict using AST

**BacktestManager Features:**
- list_backtests(): Find all runs for a strategy
- load_backtest_results(): Load all files for a run
- get_tearsheet_html(): Read HTML content
- get_metrics_df(): Parse tearsheet.csv
- get_trades_df(): Parse trades.csv
- get_stats_df(): Parse stats.csv
- get_settings(): Parse settings.json

**Utility Functions:**
- parse_run_id(): Extract ID from filename
- format_metric(): Format values for display

Related Action Items:
- Project_plan.md: Step 1.1, 1.2, 1.3, 1.4

---

### [docs]: Create documentation structure for Strategy Review feature
**Date:** 2025-10-29
**Commit:** 84e9898
**Files Changed:** Docs/Project_plan.md, Docs/Changelog.md, Docs/Backend.md, Docs/Schemas.md, Docs/Enhancements.md

Created comprehensive documentation templates for Phase 1 MVP.

Related Action Items:
- Project_plan.md: Step 0

### Format

Each commit entry follows this format:

```
### [Type]: Brief description
**Date:** YYYY-MM-DD
**Commit:** [hash]
**Files Changed:** file1.py, file2.md

Description of changes made.

Related Action Items:
- Project_plan.md: Step X.Y
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no feature change)
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `build`: Build system or dependency changes
- `ci`: CI/CD configuration changes
- `chore`: Other changes (gitignore, etc.)

---

## Version History

### Phase 1 Development Timeline

**Target Completion:** 9-13 hours from start

| Date | Version | Milestone |
|------|---------|-----------|
| 2025-10-29 | 0.0.1 | Documentation setup complete |
| TBD | 0.0.2 | Backend module complete |
| TBD | 0.0.3 | UI implementation complete |
| TBD | 0.0.4 | Testing and polish complete |
| TBD | 0.1.0 | Phase 1 MVP release |

---

## Breaking Changes

*None yet - this is initial implementation*

---

## Migration Guide

*Not applicable for Phase 1 - fresh implementation*

---

## Contributors

- Claude Code Agent (Primary Developer)
- User (Product Owner, Requirements, Testing)

---

**Last Updated:** 2025-10-29
**Current Version:** 0.0.1 (In Development)
