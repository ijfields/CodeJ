# Moon Dev AI Trading System

A comprehensive AI-powered trading system featuring multiple specialized agents for backtesting, live trading, risk management, and market analysis. This project provides a complete ecosystem for algorithmic trading with AI agents that can analyze market data, execute strategies, and manage risk automatically.

## Features

- **RBI Backtesting Agent**: Automated strategy backtesting with AI-generated code
- **Live Trading Agents**: Real-time trading with multiple AI models and consensus
- **Risk Management**: Automated portfolio risk monitoring and management
- **Market Analysis**: Sentiment analysis, whale tracking, and chart analysis
- **Multi-Exchange Support**: HyperLiquid, Aster, and other exchanges
- **Strategy Development**: AI-powered strategy generation and optimization

## How to Run

### Prerequisites

1. **Python 3.10.9** (recommended version)
2. **API Keys** for AI models and market data sources
3. **Environment Setup** with required dependencies

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/moon-dev-ai-agents-for-trading.git
   cd moon-dev-ai-agents-for-trading
   ```

2. **Set up environment:**
   ```bash
   # Using conda (recommended)
   conda create -n tflow python=3.10.9
   conda activate tflow
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   Add your API keys to the `.env` file:
   ```bash
   # AI Model APIs (at least one required)
   ANTHROPIC_KEY=your_anthropic_api_key_here
   OPENAI_KEY=your_openai_api_key_here
   DEEPSEEK_KEY=your_deepseek_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   
   # Market Data APIs
   BIRDEYE_API_KEY=your_birdeye_api_key_here
   COINGECKO_API_KEY=your_coingecko_api_key_here
   ```

### Running the Main System

**To run the main trading system:**
```bash
python moon-dev-ai-agents/src/main.py
```

This will start the main AI trading system with all configured agents. The system will:
- Initialize all active agents (trading, risk, strategy, copybot, sentiment)
- Run continuous analysis cycles
- Monitor market conditions and execute trades
- Manage portfolio risk automatically

**To run specific agents individually:**
```bash
# RBI Backtesting Agent
python moon-dev-ai-agents/src/agents/rbi_agent_pp_multi.py

# Trading Agent
python moon-dev-ai-agents/src/agents/trading_agent.py

# Risk Management Agent
python moon-dev-ai-agents/src/agents/risk_agent.py

# Strategy Agent
python moon-dev-ai-agents/src/agents/strategy_agent.py
```

## How to Test

### Running Tests

**To run the main test suite:**
```bash
# Run all tests
pytest

# Run specific test files
pytest moon-dev-ai-agents/src/scripts/test_exchange_manager.py
pytest moon-dev-ai-agents/src/scripts/test_hyperliquid_mm.py
pytest moon-dev-ai-agents/src/scripts/test_groq_qwen.py
```

**To run individual agent tests:**
```bash
# Test RBI Agent
python moon-dev-ai-agents/src/agents/rbi_batch_backtester.py

# Test Exchange Manager
python moon-dev-ai-agents/src/scripts/test_exchange_manager.py

# Test HyperLiquid Integration
python moon-dev-ai-agents/src/scripts/test_hyperliquid_mm.py
```

**To run strategy backtests:**
```bash
# Run strategy tests from the strategies folder
python Outputs/Strategies/rsi_test_strategy.py
python Outputs/Strategies/my_strategy.py
```

### Test Configuration

The system includes comprehensive testing for:
- **Agent Functionality**: Individual agent behavior and responses
- **Exchange Integration**: API connectivity and data retrieval
- **Strategy Performance**: Backtesting and validation
- **Risk Management**: Portfolio risk calculations
- **Market Data**: Data source connectivity and accuracy

### Creating Custom Tests

To create your own tests, follow the existing test patterns:

1. **Create test files** in the appropriate directory
2. **Use pytest** for test discovery and execution
3. **Mock external APIs** to avoid rate limits during testing
4. **Test both success and failure scenarios**

Example test structure:
```python
import pytest
from src.agents.trading_agent import TradingAgent

def test_trading_agent_initialization():
    agent = TradingAgent()
    assert agent is not None
    assert agent.is_initialized == True

def test_trading_agent_signal_generation():
    agent = TradingAgent()
    signals = agent.generate_signals("BTC-USD")
    assert len(signals) > 0
```

## Project Structure

```
moon-dev-ai-agents/
├── src/
│   ├── agents/           # AI trading agents
│   ├── scripts/          # Utility scripts and tests
│   ├── data/            # Market data and configurations
│   └── models/          # AI model configurations
├── Outputs/
│   ├── Strategies/      # Generated trading strategies
│   └── ForReview/       # Analysis results
└── Docs/               # Documentation and guides
```

## Important Disclaimers

⚠️ **This is an experimental research project, NOT a trading system**
- There are NO plug-and-play solutions for guaranteed profits
- Success depends entirely on YOUR trading strategy and risk management
- Trading involves substantial risk of loss
- Past performance does not indicate future results

## Support and Community

- **Discord**: [discord.gg/8UPuVZ53bh](https://discord.gg/8UPuVZ53bh)
- **Documentation**: [moondev.com](https://moondev.com)
- **Education**: [algotradecamp.com](https://algotradecamp.com)

## License

This project is open source and available under the MIT License.