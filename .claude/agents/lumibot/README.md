# Lumibot Strategy Generation Agents

This directory contains 5 specialized Claude Code subagents that work together to generate production-quality Lumibot trading strategies from various content sources (YouTube videos, PDFs, text descriptions).

## Quick Start

### Using the Command

```bash
/lumibot-generate
```

The command will:
1. Ask for input source (YouTube URL, PDF path, or text description)
2. Orchestrate all 5 agents to work in parallel
3. Generate complete, production-ready Lumibot strategy
4. Output strategy file to `Outputs/Strategies/`

### Example Usage

**From YouTube Video:**
```bash
/lumibot-generate
# Input: youtube
# URL: https://www.youtube.com/watch?v=qoTbzJAQshs
# Strategy name: 0dte_iwm_options
```

**From Text Description:**
```bash
/lumibot-generate
# Input: text
# Description: "Buy SPY when RSI(14) < 30, sell when RSI > 70. Daily timeframe, use 95% of cash, take profit at 10%, stop loss at 5%"
# Strategy name: rsi_mean_reversion
```

## Agent Architecture

### 1. 🔍 lumibot-researcher

**Purpose**: Research and extract trading rules

**Responsibilities**:
- Extract entry/exit conditions from content
- Research Lumibot documentation for correct methods
- Identify technical indicators and parameters
- Create detailed strategy specification

**Output**: `{strategy_name}_analysis.md`

**Example Output**:
```markdown
## Strategy: 0DTE IWM Options

### Entry Conditions
1. Time: Within 30 minutes of market open
2. Sell 10 PUT options on IWM
   - Expiration: Same day (0DTE)
   - Strike: $183 (OTM by ~5 points)
3. Sell 5 CALL options on IWM @$191
4. Sell 5 CALL options on IWM @$190

### Exit Conditions
1. Buy back PUTs when premium ≤ $0.02
2. Buy back $191 CALLs when premium ≤ $0.15
3. Buy back $190 CALLs when premium ≤ $0.07

### Lumibot Methods Required
- `get_chains(Asset("IWM"))`
- `chains.expirations("PUT")`
- `chains.strikes(expiry, "CALL")`
- `create_order(option_asset, quantity, side="sell")`
```

### 2. 🏗️ lumibot-architect

**Purpose**: Design strategy architecture

**Responsibilities**:
- Plan class structure and lifecycle methods
- Design state management
- Plan error handling architecture
- Create method signatures

**Output**: `{strategy_name}_architecture.md`

**Example Output**:
```markdown
## Class Structure

### Parameters
```python
parameters = {
    "symbol": "IWM",
    "num_puts": 10,
    "num_calls_191": 5,
    "num_calls_190": 5,
    "put_strike_offset": 5,
    "exit_put_premium": 0.02,
    "exit_call_191_premium": 0.15,
    "exit_call_190_premium": 0.07
}
```

### Helper Methods
- `_get_0dte_option(option_type, strike_offset)`
- `_check_market_timing()` - Ensure early trading day
- `_execute_entry()` - Sell all options
- `_check_exit_conditions()` - Check premium targets
```

### 3. 💻 lumibot-coder

**Purpose**: Implement production code

**Responsibilities**:
- Write complete, working Python code
- Implement all Lumibot methods correctly
- Add comprehensive error handling
- Include logging and documentation

**Output**: `{strategy_name}.py`

**Example Features**:
```python
class ZeroDTE_IWM_Strategy(Strategy):
    """
    0DTE Options Premium Collection on IWM

    Sells out-of-the-money puts and calls at market open,
    buys back when premium decays to target levels.
    """

    def initialize(self):
        self.sleeptime = "5M"  # Check every 5 minutes
        # ... setup

    def on_trading_iteration(self):
        try:
            # Wrapped for error handling
            self._execute_trading_logic()
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

    def _get_0dte_option(self, option_type, target_strike):
        """Get 0DTE option with same-day expiration"""
        chains = self.get_chains(Asset(self.symbol))

        # Validate chains
        if chains is None:
            return None

        # Filter for today's expiration
        expiries = chains.expirations(option_type)
        today = date.today()
        dte_0 = [e for e in expiries if e == today]

        # ... implementation
```

### 4. 🔍 lumibot-validator

**Purpose**: Validate code quality and compliance

**Responsibilities**:
- Check syntax (AST parsing)
- Verify Lumibot API compliance
- Validate options trading logic
- Check error handling and risk management

**Output**: `{strategy_name}_validation.md`

**Validation Levels**:
1. ✅ **Syntax & Structure** (Critical)
   - Valid Python syntax
   - Inherits from Strategy
   - Has required methods

2. ✅ **Lumibot API** (Critical)
   - Correct imports
   - Proper method usage
   - Asset objects complete

3. ✅ **Options Trading** (High)
   - Proper chain handling
   - Expiration date logic
   - Strike selection

4. ✅ **Error Handling** (High)
   - Try/except present
   - Data validation
   - NaN handling

5. ⚠️ **Performance** (Medium)
   - No excessive data fetching
   - Efficient calculations

6. ✅ **Security** (High)
   - No hardcoded credentials
   - Position size limits
   - Risk management present

**Example Validation Report**:
```markdown
## ✅ PASSED CHECKS (18/20)
- Python syntax valid
- Inherits from Strategy
- Has initialize() and on_trading_iteration()
- Proper get_chains usage
- Asset objects complete
- Error handling present

## ⚠️ WARNINGS (2)
1. Consider adding stop loss for unlimited risk exposure
2. Add logging for option premium at entry

## Production Readiness: 90/100
Recommendation: APPROVED with minor improvements
```

### 5. ⚡ lumibot-optimizer

**Purpose**: Refine and optimize code

**Responsibilities**:
- Fix critical validation issues
- Optimize performance
- Refactor for clarity
- Add missing features

**Actions**:
- Fix all ❌ critical issues
- Address ⚠️ warnings
- Optimize data fetching
- Extract complex logic to helper methods
- Add comprehensive logging
- Remove magic numbers

**Example Optimization**:
```python
# Before (validation warning):
if rsi < 30:  # Magic number
    # entry logic

# After (optimized):
self.rsi_oversold = self.parameters.get("rsi_oversold", 30)

if rsi < self.rsi_oversold:
    self.log_message(f"Entry signal: RSI {rsi:.1f} < {self.rsi_oversold}")
    # entry logic
```

## Agent Workflow

```
[Input Content]
      ↓
[Researcher] ──→ Analysis
      ↓
[Architect] ──→ Architecture Design
      ↓
[Coder] ──────→ Python Code
      ↓
[Validator] ──→ Validation Report
      ↓         ↗
      ❌ Issues?
      ↓         ↘
[Optimizer] ──→ Refined Code
      ↓
[Final Strategy]
```

**Execution Time**: 2-4 minutes for production-ready code

## Generated Strategy Features

### ✅ Production Quality

**Code Quality**:
- ✅ PEP 8 compliant
- ✅ Comprehensive docstrings
- ✅ Inline comments for complex logic
- ✅ Type hints where beneficial
- ✅ Modular design (helper methods)

**Lumibot Best Practices**:
- ✅ Correct Asset object creation
- ✅ Proper data validation (None checks)
- ✅ DataFrame empty checks
- ✅ NaN handling for indicators
- ✅ Error handling with try/except
- ✅ Comprehensive logging

**Risk Management**:
- ✅ Position sizing logic
- ✅ Take profit targets
- ✅ Stop loss rules
- ✅ Maximum position limits
- ✅ Cash reserves

### ✅ Options Trading Support

**0DTE Strategies**:
- ✅ Same-day expiration filtering
- ✅ Intraday timing logic
- ✅ Premium collection strategies
- ✅ Strike selection (delta, moneyness, fixed offset)
- ✅ Multi-contract handling

**Options Features**:
- ✅ Proper get_chains usage
- ✅ Expiration date filtering
- ✅ Strike price selection
- ✅ OTM/ATM/ITM logic
- ✅ Spread construction (coming soon)
- ✅ Greeks calculations (coming soon)

## Testing Your Generated Strategy

### 1. Backtest with Yahoo Finance (Free)

```python
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting

# Import your generated strategy
from Outputs.Strategies.my_strategy import GeneratedStrategy

# Run backtest
GeneratedStrategy.backtest(
    YahooDataBacktesting,
    datetime(2023, 1, 1),
    datetime(2023, 12, 31),
    parameters={"symbol": "SPY"},
    benchmark_asset="SPY"
)
```

### 2. Backtest with Polygon (Paid, Better Data)

```python
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.entities import TradingFee

GeneratedStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2023, 1, 1),
    datetime(2023, 12, 31),
    parameters={"symbol": "SPY"},
    polygon_api_key="YOUR_KEY",
    polygon_has_paid_subscription=True,
    buy_trading_fees=[TradingFee(percent_fee=0.001)],
    sell_trading_fees=[TradingFee(percent_fee=0.001)]
)
```

### 3. Paper Trading

```python
from lumibot.brokers import Alpaca
from lumibot.traders import Trader

# Configure paper trading broker
ALPACA_CONFIG = {
    "API_KEY": "your_key",
    "API_SECRET": "your_secret",
    "PAPER": True  # Paper trading mode
}

broker = Alpaca(ALPACA_CONFIG)
strategy = GeneratedStrategy(broker=broker)

trader = Trader()
trader.add_strategy(strategy)
trader.run_all()
```

## Customization

### Modify Generated Strategy

All generated strategies include a `parameters` dict for easy customization:

```python
# Default parameters in generated code
parameters = {
    "symbol": "SPY",
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70
}

# Customize when instantiating
custom_params = {
    "symbol": "QQQ",
    "rsi_period": 10,
    "rsi_oversold": 25
}

strategy = GeneratedStrategy(
    broker=broker,
    parameters=custom_params
)
```

### Extend Generated Code

```python
from Outputs.Strategies.my_strategy import GeneratedStrategy

class MyEnhancedStrategy(GeneratedStrategy):
    """Extended version with additional features"""

    def initialize(self):
        super().initialize()
        # Add custom initialization
        self.my_custom_var = True

    def on_trading_iteration(self):
        # Add pre-processing
        self._my_custom_logic()

        # Call original logic
        super().on_trading_iteration()

        # Add post-processing
        self._update_metrics()
```

## Troubleshooting

### Issue: "Agent not found"

**Solution**: Ensure you're in the correct directory:
```bash
cd "C:\Data\Cousin Ingrid\Git Hub\CodeJ"
```

### Issue: "YouTube transcript not available"

**Solution**: Use text input mode and manually paste transcript from YouTube.

### Issue: "Validation failed"

**Solution**: Check `{strategy_name}_validation.md` for specific issues. The Optimizer agent should fix most problems automatically. If not, manually review the validation report.

### Issue: "Strategy too complex"

**Solution**: Break down into multiple simpler strategies or simplify input description.

## Best Practices

### Writing Good Strategy Descriptions

**✅ Good Example**:
```
Buy IWM when:
- Time is within first 30 minutes of market open
- Sell 10 PUT options with 0DTE
- Strike price $5 below current price
- Sell 5 CALL options @$191 strike
- Sell 5 CALL options @$190 strike

Exit when:
- PUT premium falls to $0.02
- CALL @$191 premium falls to $0.15
- CALL @$190 premium falls to $0.07
```

**❌ Poor Example**:
```
Trade IWM options for premium, exit when profitable
```

### Review Generated Code

Even with AI generation, always:
1. Read the generated code
2. Review validation report
3. Understand entry/exit logic
4. Verify risk management
5. Backtest thoroughly
6. Paper trade before live

## File Structure

```
.claude/
├── agents/
│   └── lumibot/
│       ├── README.md (this file)
│       ├── lumibot-researcher.md
│       ├── lumibot-architect.md
│       ├── lumibot-coder.md
│       ├── lumibot-validator.md
│       └── lumibot-optimizer.md
├── commands/
│   └── lumibot-generate.md
└── docs/
    └── lumibot-reference.md

Outputs/
└── Strategies/
    ├── {strategy_name}.py
    ├── {strategy_name}_analysis.md
    ├── {strategy_name}_architecture.md
    └── {strategy_name}_validation.md
```

## Resources

- **Lumibot Docs**: https://lumibot.lumiwealth.com/
- **Lumibot GitHub**: https://github.com/Lumiwealth/lumibot
- **Lumibot Reference**: `.claude/docs/lumibot-reference.md`
- **Command Docs**: `.claude/commands/lumibot-generate.md`

## Support

If you encounter issues:
1. Check validation report for specific problems
2. Review Lumibot reference docs
3. Re-run `/lumibot-generate` - agents improve iteratively
4. Check generated code comments for implementation notes

---

**Remember**: Generated strategies are for educational purposes. Always backtest thoroughly and paper trade before using with real money. Trading involves risk of loss.
