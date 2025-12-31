# ================================================================
# LUMIBOT STRATEGY GENERATOR - COMPLETE IMPLEMENTATION
# Converts YouTube videos, PDFs, or text into Lumibot strategies
# ================================================================

"""
This webapp uses AI subagents to convert trading content into backtestable
Lumibot strategies. Based on Moon Dev's RBI agent pattern adapted for Lumibot.
"""

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2
from anthropic import Anthropic
from lumibot.strategies import Strategy
from lumibot.backtesting import YahooDataBacktesting
from lumibot.entities import TradingFee
from datetime import datetime
import ast
import os
import sys
import traceback
import pandas as pd

# ================================================================
# CONFIGURATION
# ================================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_API_KEY = os.getenv("ANTHROPIC_AUTH_TOKEN")  # DeepSeek uses same env var
DEEPSEEK_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
DEEPSEEK_MODEL = os.getenv("ANTHROPIC_MODEL", "deepseek-chat")

# ================================================================
# SUBAGENT 1: YouTube Transcript Extractor
# ================================================================

class YouTubeTranscriptExtractorSubagent:
    """Extracts transcripts from YouTube videos"""
    
    def extract(self, video_url: str) -> str:
        try:
            # Extract video ID from URL
            if 'v=' in video_url:
                video_id = video_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in video_url:
                video_id = video_url.split('youtu.be/')[1].split('?')[0]
            else:
                video_id = video_url
            
            # Add retry logic for rate limiting
            import time
            import random
            
            for attempt in range(3):  # Try up to 3 times
                try:
                    # Fetch transcript
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    
                    # Combine into single text
                    full_text = ' '.join([item['text'] for item in transcript_list])
                    return full_text
                    
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check if it's a rate limiting error
                    if "Too Many Requests" in error_msg or "429" in error_msg:
                        if attempt < 2:  # Don't wait on the last attempt
                            wait_time = random.uniform(2, 5) + (attempt * 2)  # Exponential backoff
                            print(f"Rate limited. Waiting {wait_time:.1f} seconds before retry {attempt + 1}/3...")
                            time.sleep(wait_time)
                            continue
                    
                    # If it's not a rate limit error, or we've exhausted retries
                    if attempt == 2:  # Last attempt
                        if "Too Many Requests" in error_msg or "429" in error_msg:
                            return "Error: YouTube rate limit exceeded. Please try again in a few minutes. You can also try using the 'Text Input' option instead."
                        else:
                            return f"Error extracting transcript: {error_msg}"
            
        except Exception as e:
            return f"Error extracting transcript: {str(e)}"

# ================================================================
# SUBAGENT 2: PDF Parser
# ================================================================

class PDFParserSubagent:
    """Extracts text from PDF documents"""
    
    def parse(self, pdf_file) -> str:
        try:
            # Reset file pointer to beginning
            pdf_file.seek(0)
            
            # Create PDF reader object
            reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            
            # Extract text from each page
            for page in reader.pages:
                text += page.extract_text() + '\n'
            
            return text
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

# ================================================================
# SUBAGENT 3: Strategy Analyzer (RBI Pattern)
# ================================================================

class StrategyAnalyzerSubagent:
    """Analyzes trading content and extracts strategy rules using Claude or DeepSeek"""
    
    def __init__(self, api_key: str, use_deepseek: bool = True):
        if use_deepseek and DEEPSEEK_API_KEY:
            # Use DeepSeek (more cost-effective)
            self.client = Anthropic(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
            self.model = DEEPSEEK_MODEL
        else:
            # Use Claude
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-haiku-20240307"
    
    def analyze(self, content: str) -> str:
        prompt = f"""
        You are an expert trading strategy analyst. Analyze the following trading content
        and extract a clear, structured trading strategy suitable for algorithmic implementation.
        
        Extract these key components:
        1. Entry Conditions: Specific signals or conditions to enter a trade
        2. Exit Conditions: Specific signals or conditions to exit a trade
        3. Position Sizing: How much capital to allocate per trade
        4. Risk Management: Stop loss rules, take profit targets, maximum position size
        5. Timeframe: What timeframe to trade on (1 minute, 5 minutes, 1 hour, daily, etc.)
        6. Asset Class: What to trade (stocks, ETFs, specific symbols)
        7. Technical Indicators: Any indicators used (RSI, SMA, MACD, etc.) with specific parameters
        
        Content to analyze:
        {content[:6000]}
        
        Return your analysis in clear, structured format with specific values and conditions.
        Be precise about thresholds, periods, and logic operators (>, <, ==, crossover, etc.).
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,  # Reduced token limit to save costs
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            error_msg = str(e)
            if "credit balance" in error_msg.lower() or "billing" in error_msg.lower():
                return f"Error: Insufficient Anthropic API credits. Please check your billing at https://console.anthropic.com/ or try using 'Text Input' with a simpler strategy description."
            return f"Error analyzing strategy: {error_msg}"

# ================================================================
# SUBAGENT 4: Lumibot Code Generator
# ================================================================

class LumibotCodeGeneratorSubagent:
    """Generates Lumibot-compatible strategy code"""
    
    def __init__(self, api_key: str, use_deepseek: bool = True):
        if use_deepseek and DEEPSEEK_API_KEY:
            # Use DeepSeek (more cost-effective)
            self.client = Anthropic(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL
            )
            self.model = DEEPSEEK_MODEL
        else:
            # Use Claude
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-haiku-20240307"
    
    def generate_strategy(self, strategy_logic: str) -> str:
        prompt = f"""
        You are an expert Python developer specializing in algorithmic trading with Lumibot.
        
        Generate a COMPLETE, WORKING Lumibot strategy class based on this strategy logic:
        
        {strategy_logic}
        
        STRICT REQUIREMENTS FOR LUMIBOT:
        
        1. Import Structure:
           from lumibot.strategies import Strategy
           from datetime import datetime
           import pandas_ta as ta
        
        2. Class Structure:
           - Inherit from Strategy
           - Name the class "GeneratedStrategy"
        
        3. Implement initialize() method:
           - Set self.sleeptime (e.g., "1D" for daily, "1H" for hourly, "5M" for 5-minute)
           - Initialize any strategy parameters
           - Set self.symbol or get from parameters
        
        4. Implement on_trading_iteration() method:
           - This is the main trading logic called at each interval
           - Use self.get_last_price(symbol) to get current price
           - Use self.get_historical_prices(symbol, length, timestep) to get historical data
           - Calculate indicators using pandas_ta or built-in methods
           - Use self.get_position(symbol) to check current positions
           
        5. Order Execution:
           - Create orders: order = self.create_order(symbol, quantity, side)
           - Submit orders: self.submit_order(order)
           - Close positions: self.sell_all()
           - Side values: "buy" or "sell"
        
        6. Position Sizing:
           - Get available cash: cash = self.get_cash()
           - Calculate quantity based on cash and price
           - Use integer quantities for stocks
        
        7. Error Handling:
           - Check if historical data is None before using
           - Check if position exists before accessing attributes
           - Validate quantity > 0 before creating orders
        
        8. Parameters:
           - Access via self.parameters dictionary
           - Provide default values with .get()
        
        9. Best Practices:
           - Add comprehensive docstrings
           - Include comments explaining logic
           - Use clear variable names
           - Avoid complex nested conditions
        
        Return ONLY the Python code with NO markdown formatting, explanations, or text before/after.
        The code should be ready to execute as-is.
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,  # Reduced token limit to save costs
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            code = response.content[0].text
            
            # Clean up markdown code blocks if present
            if code.startswith('```'):
                lines = code.split('\n')
                # Remove first line (```python) and last line (```)
                if lines[0].startswith('```'):
                    lines = lines[1:]
                if lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines)
            
            return code
        except Exception as e:
            error_msg = str(e)
            if "credit balance" in error_msg.lower() or "billing" in error_msg.lower():
                return f"# Error: Insufficient Anthropic API credits. Please check your billing at https://console.anthropic.com/ or try using 'Text Input' with a simpler strategy description."
            return f"# Error generating code: {error_msg}"

# ================================================================
# SUBAGENT 5: Code Validator
# ================================================================

class CodeValidatorSubagent:
    """Validates generated Python code for Lumibot compatibility"""
    
    def validate(self, code: str) -> tuple:
        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check required Lumibot components
        checks = {
            'Strategy import': 'from lumibot.strategies import Strategy' in code,
            'Class definition': 'class ' in code and '(Strategy)' in code,
            'initialize method': 'def initialize(self)' in code,
            'on_trading_iteration method': 'def on_trading_iteration(self)' in code,
        }
        
        failed_checks = [name for name, passed in checks.items() if not passed]
        
        if failed_checks:
            return False, f"Missing required components: {', '.join(failed_checks)}"
        
        # Check for common issues
        warnings = []
        
        if 'self.sleeptime' not in code:
            warnings.append("Warning: sleeptime not set in initialize()")
        
        if 'self.get_last_price' not in code and 'self.get_historical_prices' not in code:
            warnings.append("Warning: No price data retrieval found")
        
        if 'self.create_order' not in code and 'self.submit_order' not in code:
            warnings.append("Warning: No order execution found")
        
        message = "✅ Code validation passed"
        if warnings:
            message += "\n" + "\n".join(warnings)
        
        return True, message

# ================================================================
# SUBAGENT 6: Lumibot Backtest Executor
# ================================================================

class LumibotBacktestExecutor:
    """Executes backtest using Lumibot framework"""
    
    def execute(self, strategy_code: str, symbol: str = "SPY", 
                start_date: datetime = None, end_date: datetime = None,
                initial_cash: float = 10000.0,
                commission_pct: float = 0.0):
        
        if start_date is None:
            start_date = datetime(2023, 1, 1)
        if end_date is None:
            end_date = datetime(2023, 12, 31)
        
        try:
            # Create a temporary module
            import types
            temp_module = types.ModuleType('temp_strategy')
            
            # Add necessary imports to module namespace
            exec_globals = {
                'Strategy': Strategy,
                'datetime': datetime,
                '__name__': 'temp_strategy',
                '__builtins__': __builtins__
            }
            
            # Try to import pandas_ta if needed
            try:
                import pandas_ta as ta
                exec_globals['ta'] = ta
            except ImportError:
                pass
            
            # Execute the code in the module namespace
            exec(strategy_code, exec_globals)
            
            # Find the strategy class
            strategy_class = None
            for name, obj in exec_globals.items():
                if isinstance(obj, type) and issubclass(obj, Strategy) and obj != Strategy:
                    strategy_class = obj
                    break
            
            if strategy_class is None:
                return None, "Could not find strategy class in generated code"
            
            # Create trading fees if commission specified
            trading_fees = []
            if commission_pct > 0:
                trading_fees = [TradingFee(percent_fee=commission_pct)]
            
            # Run backtest
            results = strategy_class.backtest(
                YahooDataBacktesting,
                start_date,
                end_date,
                parameters={"symbol": symbol},
                buy_trading_fees=trading_fees,
                sell_trading_fees=trading_fees,
                benchmark_asset=symbol
            )
            
            return results, "Backtest completed successfully"
            
        except Exception as e:
            error_msg = f"Error running backtest: {str(e)}\n\n"
            error_msg += "Traceback:\n" + traceback.format_exc()
            return None, error_msg

# ================================================================
# MAIN STREAMLIT WEBAPP
# ================================================================

def main():
    st.set_page_config(
        page_title="Lumibot Strategy Generator", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
            font-weight: bold;
        }
        .success-box {
            padding: 10px;
            border-radius: 5px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🤖 Lumibot Strategy Generator")
    st.markdown("### Convert YouTube videos, PDFs, or text into backtestable Lumibot trading strategies")
    
    # Check API keys
    if not ANTHROPIC_API_KEY and not DEEPSEEK_API_KEY:
        st.error("⚠️ No API keys found. Please set either ANTHROPIC_API_KEY or run DeepSeek.ps1")
        st.info("**Option 1**: Set `ANTHROPIC_API_KEY` for Claude\n**Option 2**: Run `DeepSeek.ps1` for DeepSeek (recommended - more cost-effective)")
        st.stop()
    
    # Determine which model to use
    use_deepseek = bool(DEEPSEEK_API_KEY)
    model_name = "DeepSeek" if use_deepseek else "Claude Haiku"
    
    # Add billing info
    st.info(f"💰 **Cost Optimization**: Using {model_name} model for cost efficiency. DeepSeek is typically 5-10x cheaper than Claude!")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("Input Method")
        input_type = st.radio(
            "Select input type:",
            ["YouTube URL", "PDF Upload", "Text Input"],
            help="Choose how you want to provide the trading strategy"
        )
        
        st.divider()
        
        st.subheader("Backtest Settings")
        
        backtest_symbol = st.text_input(
            "Symbol", 
            value="SPY",
            help="Stock symbol to backtest (e.g., SPY, QQQ, AAPL)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date", 
                value=datetime(2023, 1, 1),
                help="Backtest start date"
            )
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime(2023, 12, 31),
                help="Backtest end date"
            )
        
        initial_cash = st.number_input(
            "Initial Cash ($)", 
            min_value=1000.0,
            max_value=1000000.0,
            value=10000.0,
            step=1000.0,
            help="Starting portfolio value"
        )
        
        commission = st.number_input(
            "Commission (%)", 
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            format="%.3f",
            help="Trading commission as percentage (0.001 = 0.1%)"
        )
        
        st.divider()
        st.caption("Built with Lumibot & Claude AI")
    
    # Main content area - Two columns
    col1, col2 = st.columns(2)
    
    # LEFT COLUMN: INPUT
    with col1:
        st.header("📥 Input Strategy")
        
        content = None
        
        if input_type == "YouTube URL":
            st.markdown("Enter a YouTube URL of a trading strategy video:")
            st.info("💡 **Tip**: If you get rate limit errors, try using 'Text Input' instead and manually copy the video transcript.")
            youtube_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                label_visibility="collapsed"
            )
            
            if st.button("📺 Extract Transcript", type="primary", use_container_width=True):
                if youtube_url:
                    with st.spinner("Extracting transcript from YouTube..."):
                        extractor = YouTubeTranscriptExtractorSubagent()
                        content = extractor.extract(youtube_url)
                        st.session_state['content'] = content
                        
                        if "Error" in content:
                            if "rate limit" in content.lower():
                                st.error("🚫 " + content)
                                st.warning("**Alternative**: Switch to 'Text Input' and manually copy the video transcript from YouTube.")
                            else:
                                st.error(content)
                        else:
                            st.success(f"✅ Transcript extracted! ({len(content)} characters)")
                else:
                    st.warning("Please enter a YouTube URL")
        
        elif input_type == "PDF Upload":
            st.markdown("Upload a PDF file containing a trading strategy:")
            uploaded_file = st.file_uploader(
                "Choose PDF file",
                type=['pdf'],
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                with st.spinner("Parsing PDF..."):
                    parser = PDFParserSubagent()
                    content = parser.parse(uploaded_file)
                    st.session_state['content'] = content
                    
                    if "Error" in content:
                        st.error(content)
                    else:
                        st.success(f"✅ PDF parsed! ({len(content)} characters)")
        
        elif input_type == "Text Input":
            st.markdown("Paste or type your trading strategy description:")
            content = st.text_area(
                "Strategy Description",
                height=300,
                placeholder="Example: Buy SPY when RSI(14) crosses above 30, sell when it crosses below 70. Use daily timeframe...",
                label_visibility="collapsed"
            )
            
            if content:
                st.session_state['content'] = content
                st.info(f"📝 {len(content)} characters entered")
        
        # Display extracted content
        if 'content' in st.session_state and st.session_state['content']:
            with st.expander("👁️ View Extracted Content"):
                display_content = st.session_state['content']
                if len(display_content) > 3000:
                    st.text(display_content[:3000] + "\n\n... (truncated for display)")
                else:
                    st.text(display_content)
    
    # RIGHT COLUMN: GENERATION
    with col2:
        st.header("🎯 Generate Strategy")
        
        if st.button("🚀 Generate Lumibot Strategy", type="primary", use_container_width=True, disabled='content' not in st.session_state):
            if 'content' not in st.session_state or not st.session_state['content']:
                st.error("Please provide input first!")
                st.stop()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Analyze strategy
            status_text.text("Step 1/3: Analyzing strategy logic...")
            progress_bar.progress(33)
            
            analyzer = StrategyAnalyzerSubagent(ANTHROPIC_API_KEY, use_deepseek)
            with st.spinner("AI analyzing strategy..."):
                strategy_logic = analyzer.analyze(st.session_state['content'])
                st.session_state['strategy_logic'] = strategy_logic
            
            if "Error" in strategy_logic:
                st.error(strategy_logic)
                st.stop()
            
            with st.expander("📊 View Strategy Analysis"):
                st.markdown(strategy_logic)
            
            # Step 2: Generate code
            status_text.text("Step 2/3: Generating Lumibot code...")
            progress_bar.progress(66)
            
            generator = LumibotCodeGeneratorSubagent(ANTHROPIC_API_KEY, use_deepseek)
            with st.spinner("AI generating Python code..."):
                code = generator.generate_strategy(strategy_logic)
                st.session_state['generated_code'] = code
            
            if code.startswith("# Error"):
                st.error(code)
                st.stop()
            
            # Step 3: Validate code
            status_text.text("Step 3/3: Validating code...")
            progress_bar.progress(100)
            
            validator = CodeValidatorSubagent()
            is_valid, message = validator.validate(code)
            st.session_state['code_valid'] = is_valid
            
            if is_valid:
                st.success("✅ Strategy generated successfully!")
                if "Warning" in message:
                    st.warning(message)
            else:
                st.error(f"⚠️ Validation issues: {message}")
            
            status_text.empty()
            progress_bar.empty()
    
    # FULL WIDTH: GENERATED CODE
    if 'generated_code' in st.session_state:
        st.divider()
        st.header("💻 Generated Lumibot Strategy Code")
        
        # Code display with syntax highlighting
        st.code(st.session_state['generated_code'], language='python', line_numbers=True)
        
        # Download button
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📥 Download Strategy Code",
                data=st.session_state['generated_code'],
                file_name="lumibot_strategy.py",
                mime="text/x-python",
                use_container_width=True
            )
        
        # BACKTEST SECTION
        if st.session_state.get('code_valid', False):
            st.divider()
            st.header("📊 Backtest Strategy")
            
            st.info(f"🎯 Symbol: {backtest_symbol} | 📅 Period: {start_date} to {end_date} | 💰 Initial Cash: ${initial_cash:,.2f}")
            
            if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
                executor = LumibotBacktestExecutor()
                
                with st.spinner("Running backtest... This may take 30-60 seconds..."):
                    results, message = executor.execute(
                        st.session_state['generated_code'],
                        backtest_symbol,
                        datetime.combine(start_date, datetime.min.time()),
                        datetime.combine(end_date, datetime.min.time()),
                        initial_cash,
                        commission
                    )
                
                if results:
                    st.success(message)
                    
                    # Display results
                    st.subheader("📈 Backtest Results")
                    
                    # Try to extract key metrics
                    try:
                        if hasattr(results, 'to_dict'):
                            results_dict = results.to_dict()
                        else:
                            results_dict = results
                        
                        # Display key metrics in columns
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            total_return = results_dict.get('total_return', 'N/A')
                            if total_return != 'N/A':
                                st.metric("Total Return", f"{total_return:.2%}")
                            else:
                                st.metric("Total Return", "N/A")
                        
                        with metric_col2:
                            sharpe = results_dict.get('sharpe_ratio', 'N/A')
                            if sharpe != 'N/A':
                                st.metric("Sharpe Ratio", f"{sharpe:.2f}")
                            else:
                                st.metric("Sharpe Ratio", "N/A")
                        
                        with metric_col3:
                            max_dd = results_dict.get('max_drawdown', 'N/A')
                            if max_dd != 'N/A':
                                st.metric("Max Drawdown", f"{max_dd:.2%}")
                            else:
                                st.metric("Max Drawdown", "N/A")
                        
                        with metric_col4:
                            trades = results_dict.get('number_of_trades', 'N/A')
                            st.metric("Total Trades", trades)
                        
                        # Display full results
                        with st.expander("📋 View All Metrics"):
                            st.write(results)
                        
                    except Exception as e:
                        st.write("**Results:**")
                        st.write(results)
                        st.caption(f"Note: Could not parse detailed metrics: {str(e)}")
                else:
                    st.error("❌ Backtest failed:")
                    st.code(message)

if __name__ == "__main__":
    main()
