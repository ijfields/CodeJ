<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# i want to create a webapp that allows the user to youtube video, pdf or text and endup with a lumibot codedstategy that can be backtested. How can i use the claude subagent defined here: [https://github.com/moondevonyt/moon-dev-ai-agents/tree/main/docs](https://github.com/moondevonyt/moon-dev-ai-agents/tree/main/docs)  what other subagents might i need?

Perfect! Now I have all the components. Let me generate the final comprehensive answer.

# Building a Lumibot Strategy Generation Webapp with Claude Subagents

Based on your requirements to create a webapp that converts YouTube videos, PDFs, or text into backtestable Lumibot strategies, here's a comprehensive guide on using the Moon Dev Claude subagent architecture and identifying the additional subagents you'll need.

![Architecture flowchart for the Lumibot strategy generation webapp showing the complete workflow from input to backtested strategy](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/b0e85d773ece02608e89764ccbf5716e/41775a4b-2df8-4ed3-bbdc-b14cc549da07/09bffe58.png)

Architecture flowchart for the Lumibot strategy generation webapp showing the complete workflow from input to backtested strategy

## Understanding the Moon Dev Subagent Architecture

The **moon-dev-ai-agents** repository provides an excellent foundation for your project. The key component you should leverage is the **RBI Agent (Research-Based Inference)**, located at `src/agents/rbi_agent.py`. This agent follows the exact pattern you need: it takes YouTube videos, PDFs, or text as input and converts them into backtestable trading strategies.[^1]

### Core Moon Dev Components to Integrate

**1. RBI Agent Pattern**
The RBI Agent demonstrates the complete workflow you need:[^1]

- Input extraction from multiple sources (YouTube/PDF/text)
- AI-powered strategy analysis using DeepSeek R1 or Claude
- Code generation for backtesting frameworks
- Automated backtest execution
- Performance metrics reporting
- Cost: ~\$0.027 per strategy generation[^1]

**2. Model Factory**
Located at `src/models/model_factory.py`, this provides unified LLM provider abstraction. You can easily switch between Claude, GPT-4, DeepSeek, Groq, Gemini, and local Ollama models:[^1]

```python
from src.models.model_factory import ModelFactory
model = ModelFactory.create_model('anthropic')  # or 'deepseek', 'openai'
```

**3. Configuration Management**
The repository uses `src/config.py` for centralized settings including AI model selection, API keys, risk parameters, and agent behavior.[^1]

## Required Subagents for Your Webapp

Based on the Moon Dev architecture and your specific requirements, you'll need these subagents:

### Input Processing Layer (3 Subagents)

**YouTube Transcript Extractor Subagent**

- **Library**: youtube-transcript-api[^2][^3]
- **Function**: Extract video transcripts from YouTube URLs
- **Implementation**: The youtube-transcript-api library provides a simple interface to fetch transcripts without downloading videos[^2]

```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript(video_id)
full_text = ' '.join([item['text'] for item in transcript])
```

**PDF Parser Subagent**

- **Libraries**: PyPDF, PyMuPDF (fitz), or pdfplumber[^4][^5]
- **Function**: Extract text content from PDF documents
- **Recommendation**: PyPDF for simple PDFs, PyMuPDF for complex layouts[^4]

**Text Preprocessor Subagent**

- **Technology**: Python string processing
- **Function**: Clean and format raw text input for optimal LLM processing


### Strategy Generation Layer (3 Subagents)

**Strategy Analyzer Subagent** (Adapting RBI Agent Pattern)

- **Model**: Claude Sonnet or DeepSeek R1[^1][^6]
- **Function**: Analyze trading content and extract structured strategy rules (entry conditions, exit conditions, position sizing, risk management, timeframe, assets)[^1]
- **Integration**: Directly adapt from `src/agents/rbi_agent.py`

**Code Generator Subagent**

- **Model**: Claude Sonnet or GPT-4[^6]
- **Function**: Generate Lumibot-compatible Python code that inherits from `lumibot.strategies.Strategy`[^7][^8]
- **Requirements**: Must implement `on_trading_iteration()` method and use proper Lumibot API methods

**Code Validator Subagent**

- **Technology**: Python AST module
- **Function**: Validate syntax, check Lumibot API compliance, verify required imports and methods
- **Benefit**: Ensures generated code is executable before backtesting


### Execution Layer (2 Subagents)

**Backtest Executor Subagent**

- **Framework**: Lumibot backtesting engine[^7][^9]
- **Data Sources**: Polygon.io (recommended), Yahoo Finance (free), or custom CSV[^7]
- **Function**: Execute generated strategy on historical data with configurable date ranges

**Results Analyzer Subagent**

- **Metrics**: Sharpe ratio, maximum drawdown, win rate, total return, profit factor[^7]
- **Visualization**: Generate charts and performance reports


## Frontend Implementation Options

### Option A: Streamlit (Recommended for Speed)

**Advantages**:[^10][^11]

- Fastest development time (hours vs. days)
- Built-in file upload widget with `st.file_uploader()`
- No separate frontend/backend needed
- Native support for data visualization
- Perfect for MVP and internal tools

```python
import streamlit as st

uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
youtube_url = st.text_input("Enter YouTube URL")
text_input = st.text_area("Paste strategy text")
```


### Option B: Flask/FastAPI + React (For Production Apps)

**Flask/FastAPI Backend**:[^12][^13]

- FastAPI: 5-7x faster than Flask, built-in async support, automatic API documentation[^12]
- Flask: More mature ecosystem, simpler learning curve, extensive plugin support[^12]
- Best for: Production apps requiring scalability and custom frontends

**React Frontend**:[^14][^15]

- Full control over UI/UX
- Better for complex user interactions
- Industry-standard for professional web applications

**Integration Pattern**:[^15][^14]

```python
# Flask backend
@app.route('/api/generate-strategy', methods=['POST'])
def generate_strategy():
    file = request.files['file']
    # Process through subagents...
    return jsonify({'code': generated_code})

# React frontend
const response = await fetch('/api/generate-strategy', {
    method: 'POST',
    body: formData
});
```


## Additional Subagents You Might Need

Beyond the core architecture, consider these enhancement subagents:

**1. Parameter Optimizer Subagent**

- Function: Fine-tune strategy parameters using grid search or Bayesian optimization
- Use Case: Maximize Sharpe ratio or other performance metrics

**2. Risk Validator Subagent** (Optional)

- Location: `src/agents/risk_agent.py` in Moon Dev repo[^1]
- Function: Validate strategies against risk limits before deployment
- Integration: Add as final validation step

**3. Multi-Timeframe Analyzer Subagent**

- Function: Test strategies across different timeframes (1min, 5min, 1hour, daily)
- Use Case: Ensure strategy robustness across market conditions

**4. Documentation Generator Subagent**

- Function: Auto-generate README and strategy documentation
- Use Case: Create shareable strategy reports

**5. Deployment Assistant Subagent**

- Function: Deploy strategies to live trading platforms (Alpaca, Tradier, Interactive Brokers)[^16]
- Use Case: Bridge gap from backtest to live trading


## Recommended Architecture Pattern

```
User Input → Input Router Subagent
           ↓
      Content Extractor Subagents (YouTube/PDF/Text)
           ↓
      Strategy Analyzer Subagent (Claude - RBI Pattern)
           ↓
      Code Generator Subagent (Claude/DeepSeek)
           ↓
      Code Validator Subagent
           ↓
      Backtest Executor Subagent (Lumibot)
           ↓
      Results Visualizer Subagent
           ↓
      User Output (Code + Performance Metrics)
```

Each subagent operates independently, allowing for:

- Separate testing and debugging
- Easy swapping of implementations
- Enhanced functionality without affecting other components
- Caching to reduce API costs


## Implementation Timeline

**Required Subagents (Core Functionality)**: 30-50 hours

- Input processing: 5-10 hours
- Strategy generation: 16-24 hours
- Execution and results: 8-12 hours
- Frontend integration: 6-8 hours

**Optional Enhancement Subagents**: Additional 20-40 hours

## Key Integration Points with Moon Dev Architecture

1. **Adopt the Model Factory Pattern**: Use `ModelFactory.create_model()` for all LLM calls, enabling easy switching between providers[^1]
2. **Follow RBI Agent Structure**: The RBI agent in the Moon Dev repo demonstrates the exact input → analysis → code generation → execution → results pattern you need[^1]
3. **Use Shared Utilities**: Leverage `src/nice_funcs.py` for trading-specific functions if you expand beyond strategy generation[^1]
4. **Configuration Management**: Follow the centralized config approach in `src/config.py` for API keys and settings[^1]

## Getting Started

1. **Clone and study the Moon Dev repository**: Focus on `src/agents/rbi_agent.py` and `src/models/model_factory.py`
2. **Start with Streamlit MVP**: Build a minimal working version in 1-2 days
3. **Implement core subagents**: YouTube extractor → Strategy analyzer → Code generator → Backtest executor
4. **Test with sample inputs**: Use trading strategy videos from YouTube to validate the pipeline
5. **Add enhancement subagents**: Parameter optimization, risk validation, multi-timeframe analysis
6. **Consider production migration**: If needed, migrate to Flask/FastAPI + React for scalability

The Moon Dev repository provides an excellent blueprint for this exact use case. The RBI agent is essentially a production-ready implementation of what you're trying to build, and you can adapt it directly for Lumibot strategy generation.[^1]
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^110][^111][^112][^113][^114][^115][^116][^117][^118][^119][^120][^121][^122][^123][^124][^125][^126][^127][^128][^129][^130][^131][^132][^133][^134][^135][^136][^137][^138][^139][^140][^141][^142][^143][^144][^145][^146][^147][^148][^149][^150][^151][^152][^153][^154][^155][^156][^157][^158][^159][^160][^161][^162][^163][^164][^165][^166][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#claudemd

[^2]: https://pypi.org/project/youtube-transcript-api/

[^3]: https://stackoverflow.com/questions/76856230/how-to-extract-youtube-video-transcripts-using-youtube-api-on-python

[^4]: https://www.geeksforgeeks.org/python/extract-text-from-pdf-file-using-python/

[^5]: https://nanonets.com/blog/extract-text-from-pdf-file-using-python/

[^6]: https://www.leanware.co/insights/prompt-engineering-for-code-generation

[^7]: https://lumibot.lumiwealth.com/backtesting.html

[^8]: https://github.com/Lumiwealth/lumibot

[^9]: https://lumibot.lumiwealth.com/backtesting.how_to_backtest.html

[^10]: https://www.projectpro.io/recipes/add-file-uploader-widget-streamlit

[^11]: https://docs.kanaries.net/topics/Streamlit/streamlit-upload-file

[^12]: https://betterstack.com/community/guides/scaling-python/flask-vs-fastapi/

[^13]: https://strapi.io/blog/fastapi-vs-flask-python-framework-comparison

[^14]: https://www.linkedin.com/pulse/quick-upload-display-photos-using-flask-api-react-frontend-soto-yotre

[^15]: https://stackoverflow.com/questions/53132236/file-upload-with-reactjs-and-flask

[^16]: https://lumibot.lumiwealth.com

[^17]: https://github.com/moondevonyt/moon-dev-ai-agents

[^18]: https://docs.claude.com/en/docs/claude-code/sub-agents

[^19]: https://www.youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz

[^20]: https://github.com/moondevonyt

[^21]: https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

[^22]: https://www.moontechnolabs.com/blog/how-to-build-an-ai-agent/

[^23]: https://www.youtube.com/watch?v=RlqzkSgDKDc

[^24]: https://www.reddit.com/r/ClaudeAI/comments/1m8ik5l/claude_code_now_supports_custom_agents/

[^25]: https://www.youtube.com/watch?v=HJ9VvIG3Rps

[^26]: https://x.com/moondevonyt?lang=en

[^27]: https://github.com/VoltAgent/awesome-claude-code-subagents

[^28]: https://www.reddit.com/r/ClaudeAI/comments/1me8t0e/how_i_use_sub_agents_in_a_loop_like_a_dev_team/

[^29]: https://www.linkedin.com/posts/parker-perry-7a018315a_github-moondevonytmoon-dev-ai-agents-activity-7292950505457139712-lRzI

[^30]: https://www.youtube.com/watch?v=DNGxMX7ym44

[^31]: https://github.com/xircusweb3/ai-agents-trading

[^32]: https://www.reddit.com/r/ClaudeAI/comments/1mc6mzu/claude_code_subagents_collection_35_specialized/

[^33]: https://x.com/MoonDevOnYT/status/1980252349944758743

[^34]: https://docs.claude.com/en/api/agent-sdk/subagents

[^35]: https://x.com/MoonDevOnYT/status/1980344535319539981

[^36]: https://www.reddit.com/r/ClaudeAI/comments/1mb95kp/claude_custom_sub_agents_are_amazing_feature_and/

[^37]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#project-overview

[^38]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#key-development-commands

[^39]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#running-the-system

[^40]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#architecture-overview

[^41]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#agent-ecosystem

[^42]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#llm-integration-model-factory

[^43]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#configuration-management

[^44]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#shared-utilities

[^45]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#data-flow-pattern

[^46]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#development-rules

[^47]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#agent-development-pattern

[^48]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#testing-strategies

[^49]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#important-context

[^50]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#autonomous-execution

[^51]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#ai-driven-strategy-generation-rbi-agent

[^52]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#common-patterns

[^53]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#switching-ai-models

[^54]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#reading-market-data

[^55]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/CLAUDE.md\#project-philosophy

[^56]: https://www.youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz

[^57]: https://www.anthropic.com/research/building-effective-agents

[^58]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#trading-agent

[^59]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#what-it-does

[^60]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#usage

[^61]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#configuration

[^62]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#key-functions

[^63]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/trading_agent.md\#output

[^64]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#risk-agent

[^65]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#what-it-does

[^66]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#usage

[^67]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#configuration

[^68]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#risk-checks

[^69]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/risk_agent.md\#output

[^70]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#rbi-agent-research-based-inference

[^71]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#what-it-does

[^72]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#usage

[^73]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#input-sources

[^74]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#process

[^75]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#configuration

[^76]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#cost

[^77]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/rbi_agent.md\#output

[^78]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#sentiment-agent

[^79]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#what-it-does

[^80]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#usage

[^81]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#data-sources

[^82]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#key-metrics

[^83]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#configuration

[^84]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/sentiment_agent.md\#output

[^85]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#chat-agent

[^86]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#what-it-does

[^87]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#usage

[^88]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#commands

[^89]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#features

[^90]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#configuration

[^91]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/chat_agent.md\#output

[^92]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#whale-agent

[^93]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#what-it-does

[^94]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#usage

[^95]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#tracking-features

[^96]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#configuration

[^97]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#data-sources

[^98]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/whale_agent.md\#output

[^99]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#strategy-agent

[^100]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#what-it-does

[^101]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#usage

[^102]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#add-new-strategy

[^103]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#configuration

[^104]: https://github.com/moondevonyt/moon-dev-ai-agents/blob/main/docs/strategy_agent.md\#output

[^105]: https://www.reddit.com/r/LangChain/comments/1e7cntq/whats_the_best_python_library_for_extracting_text/

[^106]: https://www.youtube.com/watch?v=2Y_vwAkEx64\&vl=en

[^107]: https://python.langchain.com/docs/integrations/document_loaders/youtube_transcript/

[^108]: https://stackoverflow.com/questions/34837707/how-to-extract-text-from-a-pdf-file-via-python

[^109]: https://www.reddit.com/r/SideProject/comments/1ecg9f0/ive_created_a_free_tool_for_extracting_youtube/

[^110]: https://pymupdf.readthedocs.io

[^111]: https://www.youtube.com/watch?v=PMkBgsmXdTU

[^112]: https://assemblyai.com/blog/how-to-get-the-transcript-of-a-youtube-video

[^113]: https://www.reddit.com/r/algotrading/comments/1ies2sx/backtesting_platformstools/

[^114]: https://supadata.ai/youtube-transcript-api

[^115]: https://unstract.com/blog/extract-tables-from-pdf-python/

[^116]: https://www.youtube.com/watch?v=TwJX9AHdnQg

[^117]: https://orkes.io/blog/building-agentic-interview-app-with-conductor/

[^118]: https://arxiv.org/html/2502.02539v1

[^119]: https://www.youtube.com/watch?v=aK3dky0zpj0\&vl=en-US

[^120]: https://www.reddit.com/r/AI_Agents/comments/1lw7fdw/i_want_to_build_agentic_workflows/

[^121]: https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/

[^122]: https://www.reddit.com/r/ClaudeAI/comments/1mi59yk/we_prepared_a_collection_of_claude_code_subagents/

[^123]: https://www.patronus.ai/ai-agent-development/agentic-workflow

[^124]: https://www.reddit.com/r/ArtificialSentience/comments/1lrho3h/very_quickly_after_sustained_use_of_llm/

[^125]: https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/

[^126]: https://www.llamaindex.ai/blog/announcing-workflows-1-0-a-lightweight-framework-for-agentic-systems

[^127]: https://www.catio.tech/blog/emerging-architecture-patterns-for-the-ai-native-enterprise

[^128]: https://www.eesel.ai/blog/claude-code-sub-agent

[^129]: https://github.com/PrefectHQ/ControlFlow

[^130]: https://martinfowler.com/articles/convo-llm-abstractions.html

[^131]: https://www.reddit.com/r/ClaudeCode/comments/1m8r9ra/sub_agents_are_a_game_changer_here_is_how_i_made/

[^132]: https://wandb.ai/byyoung3/Generative-AI/reports/Agentic-workflows-Getting-started-with-AI-Agents--VmlldzoxMTAwNTI4OA

[^133]: https://eugeneyan.com/writing/llm-patterns/

[^134]: https://strandsagents.com/latest/documentation/docs/examples/python/agents_workflows/

[^135]: https://www.webiny.com/docs/architecture/api/file-upload

[^136]: https://cloudinary.com/guides/front-end-development/file-upload-as-a-service-how-it-works-and-5-leading-solutions

[^137]: https://www.prompthub.us/blog/using-llms-for-code-generation-a-guide-to-improving-accuracy-and-addressing-common-issues

[^138]: https://www.geeksforgeeks.org/python/comparison-of-fastapi-with-django-and-flask/

[^139]: https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads?view=aspnetcore-9.0

[^140]: https://cloud.google.com/discover/what-is-prompt-engineering

[^141]: https://aws.amazon.com/blogs/compute/uploading-to-amazon-s3-directly-from-a-web-or-mobile-application/

[^142]: https://www.reddit.com/r/PromptEngineering/comments/1hv1ni9/prompt_engineering_of_llm_prompt_engineering/

[^143]: https://webandcrafts.com/blog/django-vs-flask-vs-fastapi

[^144]: https://www.speakeasy.com/api-design/file-uploads

[^145]: https://scale.stanford.edu/ai/repository/enhancing-computer-programming-education-llms-study-effective-prompt-engineering

[^146]: https://leapcell.io/blog/python-framework-war-flask-fastapi

[^147]: https://www.bluetickconsultants.com/building-our-own-file-upload-system-why-we-replaced-filestack-with-uppy-ucs-and-gcs/

[^148]: https://www.promptingguide.ai/prompts/coding

[^149]: https://blog.jetbrains.com/pycharm/2025/02/django-flask-fastapi/

[^150]: https://www.reddit.com/r/LangChain/comments/1fpw9qd/an_advice_on_architecture_for_sessionbased_file/

[^151]: https://www.lakera.ai/blog/prompt-engineering-guide

[^152]: https://www.youtube.com/watch?v=IfTWiZyIbRU

[^153]: https://dev.to/tsubasa_tech/file-upload-and-download-with-streamlit-in-snowflake-1joi

[^154]: https://www.reddit.com/r/flask/comments/yk50nn/sending_files_from_flask_to_react_frontend/

[^155]: https://www.youtube.com/watch?v=PyZN02fKZAU

[^156]: https://www.youtube.com/watch?v=kuMDHHYTK5s

[^157]: https://dundermethodpaperco.hashnode.dev/file-uploads-made-easy-with-react-and-flask

[^158]: https://boramorka.github.io/LLM-Book/CHAPTER-2/2.2 LangChain Document Loaders/

[^159]: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader

[^160]: https://github.com/davidyen-888/react-flask-upload

[^161]: https://www.youtube.com/watch?v=ccXH6FhrWHk

[^162]: https://www.youtube.com/watch?v=k1DsA6cikJ4

[^163]: https://www.youtube.com/watch?v=WmLNjQAS3Mc

[^164]: https://www.youtube.com/watch?v=75uBcITe0gU

[^165]: https://discuss.streamlit.io/t/how-do-i-replicate-chatgpt-file-upload-option-ui/51781

[^166]: https://www.youtube.com/watch?v=tvcWCQqLegM

