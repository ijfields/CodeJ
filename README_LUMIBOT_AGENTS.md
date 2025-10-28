# Lumibot Strategy Generator - Enhanced with Claude Code AI Agents

Complete system for generating production-quality Lumibot trading strategies from YouTube videos, PDFs, or text descriptions using specialized AI agents.

## 🎯 Quick Start

### Option 1: Enhanced Streamlit Webapp (Recommended)

```bash
# Install dependencies
pip install streamlit youtube-transcript-api PyPDF2 lumibot pandas_ta

# Run the enhanced webapp
streamlit run lumibot_strategy_generator_enhanced.py
```

Then:
1. Open browser to `http://localhost:8501`
2. Choose input method (YouTube/PDF/Text)
3. Provide your strategy description
4. Click "Generate Lumibot Strategy with AI Agents"
5. Watch the 5 agents work together in real-time!
6. Download your production-ready code

### Option 2: Command-Line Agents

```bash
# Use the /lumibot-generate slash command
/lumibot-generate

# Or use Python integration directly
from claude_agent_integration import generate_lumibot_strategy

result = generate_lumibot_strategy(
    content="Buy SPY when RSI < 30, sell when RSI > 70",
    strategy_name="rsi_strategy"
)

print(result['strategy_code'])
```

## 🤖 How It Works

### Multi-Agent Architecture

Five specialized AI agents collaborate to create production-quality code:

```
[Input Content]
      ↓
[1. Researcher Agent] ──→ Extracts precise trading rules
      ↓
[2. Architect Agent] ──→ Designs clean architecture
      ↓
[3. Coder Agent] ──────→ Implements production code
      ↓
[4. Validator Agent] ──→ Validates quality & compliance
      ↓              ↗
      ❌ Issues found?
      ↓              ↘
[5. Optimizer Agent] ──→ Fixes and optimizes
      ↓
[Production-Ready Strategy]
```

**Time:** 2-4 minutes
**Output:** Production-quality Lumibot strategy with documentation

### What Each Agent Does

**1. 🔍 Lumibot Researcher**
- Extracts entry/exit conditions from your content
- Researches Lumibot documentation for correct methods
- Identifies technical indicators and parameters
- Creates detailed strategy specification

**2. 🏗️ Lumibot Architect**
- Designs class structure and parameters
- Plans lifecycle methods (initialize, on_trading_iteration)
- Designs state management and helper methods
- Creates architecture blueprint

**3. 💻 Lumibot Coder**
- Implements complete Python code
- Uses correct Lumibot API methods
- Adds comprehensive error handling
- Includes detailed logging throughout

**4. ✅ Lumibot Validator**
- Validates Python syntax (AST parsing)
- Checks Lumibot API compliance
- Verifies error handling and risk management
- Generates quality report

**5. ⚡ Lumibot Optimizer**
- Fixes critical validation issues
- Optimizes performance
- Refactors for clarity
- Adds missing features

## 📁 File Structure

```
Your Project/
├── .claude/
│   ├── agents/lumibot/              # Agent definitions
│   │   ├── lumibot-researcher.md
│   │   ├── lumibot-architect.md
│   │   ├── lumibot-coder.md
│   │   ├── lumibot-validator.md
│   │   ├── lumibot-optimizer.md
│   │   └── README.md
│   ├── commands/
│   │   └── lumibot-generate.md      # Slash command docs
│   └── docs/
│       └── lumibot-reference.md     # Complete Lumibot API reference
│
├── claude_agent_integration.py      # Integration layer
├── lumibot_strategy_generator_enhanced.py  # Enhanced Streamlit app
├── credentials_example.py            # Configuration template
│
└── Outputs/Strategies/              # Generated strategies
    ├── {strategy_name}.py
    ├── {strategy_name}_analysis.md
    ├── {strategy_name}_architecture.md
    └── {strategy_name}_validation.md
```

## 🎓 Examples

### Example 1: Simple RSI Strategy from Text

**Input:**
```
Buy SPY when RSI(14) crosses below 30 (oversold).
Sell SPY when RSI(14) crosses above 70 (overbought).
Daily timeframe, use 95% of cash.
Take profit at 10%, stop loss at 5%.
```

**Output:** Complete strategy with:
- ✅ RSI indicator calculation with pandas_ta
- ✅ Entry/exit logic with proper thresholds
- ✅ Position sizing (95% of cash)
- ✅ Risk management (TP/SL)
- ✅ Error handling and logging
- ✅ Backtest configuration

### Example 2: 0DTE Options from YouTube

**Input:** YouTube video URL about 0DTE options trading

**Output:** Production strategy with:
- ✅ 0DTE expiration filtering (`exp == date.today()`)
- ✅ Option chains handling (`get_chains`)
- ✅ Strike selection logic
- ✅ Asset.AssetType.OPTION creation
- ✅ Premium-based exits
- ✅ Multi-leg position management
- ✅ Polygon.io integration

### Example 3: Complex Strategy from PDF

**Input:** PDF document with detailed trading rules

**Output:**
- ✅ Parsed all conditions from PDF
- ✅ Multi-timeframe analysis
- ✅ Multiple indicator combinations
- ✅ Advanced position sizing
- ✅ Portfolio-level risk management
- ✅ Complete documentation

## ⚙️ Configuration

### Setup credentials.py

```bash
# Copy example
cp credentials_example.py credentials.py

# Edit and add your API keys
# Required for backtesting:
POLYGON_API_KEY=your_key_here
```

### Customize Agent Behavior

Edit `.claude/agents/lumibot/{agent}.md` to customize:
- Code style preferences
- Risk management rules
- Validation strictness
- Optimization priorities

## 📊 Generated Code Quality

All generated strategies include:

**✅ Production Quality:**
- PEP 8 compliant code
- Comprehensive docstrings
- Inline comments for complex logic
- Modular design (helper methods)
- Type hints where beneficial

**✅ Lumibot Best Practices:**
- Correct Asset object creation
- Proper data validation (None checks)
- DataFrame empty checks
- NaN handling for indicators
- Error handling with try/except

**✅ Risk Management:**
- Position sizing logic
- Take profit targets
- Stop loss rules
- Maximum position limits
- Cash reserves

**✅ Options Trading:**
- Proper get_chains usage
- Expiration filtering (0DTE support)
- Strike selection logic
- Option Asset creation
- Multi-leg handling

## 🔄 Comparison: Original vs Enhanced

| Feature | Original Streamlit App | Enhanced with Agents |
|---------|----------------------|---------------------|
| **Analysis** | Single LLM call | Multi-agent collaboration |
| **Code Quality** | Basic | Production-grade |
| **Validation** | Simple AST check | 6-level comprehensive |
| **Options Support** | Limited | Expert (0DTE, chains, etc.) |
| **Error Handling** | Minimal | Comprehensive |
| **Refinement** | None | Iterative (Validator→Optimizer) |
| **Documentation** | Code only | Code + Analysis + Architecture |
| **Time** | ~30 seconds | 2-4 minutes |
| **Quality** | Good | Excellent |

## 🚀 Advanced Usage

### Integrate into Existing Workflow

```python
from claude_agent_integration import generate_lumibot_strategy

# Generate strategy
result = generate_lumibot_strategy(
    content=your_strategy_description,
    strategy_name="my_custom_strategy",
    progress_callback=lambda step, total, msg, pct: print(msg)
)

if result['success']:
    # Save code
    with open('my_strategy.py', 'w') as f:
        f.write(result['strategy_code'])

    # Save documentation
    with open('analysis.md', 'w') as f:
        f.write(result['analysis'])
```

### Customize Parameters

```python
# In your Streamlit app or Python script
from lumibot.strategies import Strategy

class CustomStrategy(GeneratedStrategy):
    """Extend generated strategy with custom features"""

    parameters = {
        **GeneratedStrategy.parameters,
        "my_custom_param": 100
    }

    def initialize(self):
        super().initialize()
        # Add custom initialization
```

## 🐛 Troubleshooting

### Issue: "Agent not found"
**Solution:** Ensure you're in the project directory with `.claude/agents/` folder

### Issue: "YouTube transcript failed"
**Solution:** Use "Text Input" mode and paste transcript manually

### Issue: "Validation failed"
**Solution:** Check `{strategy_name}_validation.md` - Optimizer agent should auto-fix most issues

### Issue: "Backtest fails"
**Solution:**
1. Verify `credentials.py` is configured
2. Check Polygon.io API key (paid plan required for options)
3. Review generated code for any manual adjustments needed

## 📚 Resources

- **Lumibot Docs**: https://lumibot.lumiwealth.com/
- **Lumibot GitHub**: https://github.com/Lumiwealth/lumibot
- **Claude Code**: https://claude.ai/code
- **Agent Reference**: `.claude/agents/lumibot/README.md`
- **API Reference**: `.claude/docs/lumibot-reference.md`

## 🎯 Best Practices

**For Best Results:**
1. Provide clear, specific entry/exit conditions
2. Include exact numeric parameters (not "around" or "approximately")
3. Specify timeframes explicitly
4. Mention risk management rules
5. Review generated code before backtesting
6. Always paper trade before live trading

**Input Examples:**

✅ **Good:**
```
Buy SPY when:
- RSI(14) < 30
- Price > 200-day SMA
- Volume > 1.5x average

Sell when:
- RSI(14) > 70
- OR take profit at 10%
- OR stop loss at 5%

Timeframe: Daily
Position size: 90% of cash
```

❌ **Poor:**
```
Trade SPY using RSI, exit when profitable
```

## ⚠️ Disclaimer

Generated strategies are for educational purposes. Always:
- ✅ Backtest thoroughly (6+ months of data)
- ✅ Paper trade before live trading
- ✅ Understand the strategy logic completely
- ✅ Start with small position sizes
- ✅ Monitor for unexpected behavior

Trading involves substantial risk of loss. Past performance does not indicate future results.

---

**Built with:**
- Claude Code AI Agents
- Lumibot Trading Framework
- Streamlit Web Framework
- Inspired by Moon Dev's RBI agent pattern

**Version:** 1.0.0
**Last Updated:** 2025-01-26
