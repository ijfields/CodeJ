# Changelog

All notable changes to the Strategy Review feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Documentation templates (Project_plan.md, Changelog.md, Backend.md, Schemas.md, Enhancements.md)

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

*This section will be filled with detailed commit entries as implementation progresses.*

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
