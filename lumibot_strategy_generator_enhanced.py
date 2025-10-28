"""
Enhanced Lumibot Strategy Generator - Powered by Claude Code Agents

This webapp uses specialized Claude Code subagents to convert YouTube videos,
PDFs, or text descriptions into production-quality Lumibot trading strategies.

Features:
- Multi-agent collaboration (Researcher → Architect → Coder → Validator → Optimizer)
- Production-grade code with comprehensive error handling
- Expert options trading support (0DTE, chains, Asset objects)
- Polygon.io integration
- Iterative refinement and validation
- Complete documentation (analysis + architecture + code + validation)

Agents:
1. lumibot-researcher - Extracts precise trading rules
2. lumibot-architect - Designs clean architecture
3. lumibot-coder - Implements production code
4. lumibot-validator - Validates quality & compliance
5. lumibot-optimizer - Refines and optimizes

Original concept based on Moon Dev's RBI agent pattern.
Enhanced with Claude Code multi-agent architecture.
"""

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2
from datetime import datetime
import os
import sys

# Import the Claude agent integration layer
from claude_agent_integration import generate_lumibot_strategy, validate_strategy_code

# ================================================================
# PAGE CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="Lumibot Strategy Generator - Enhanced with AI Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 2px solid #c3e6cb;
        margin: 10px 0;
    }
    .info-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d1ecf1;
        border: 2px solid #bee5eb;
        margin: 10px 0;
    }
    .warning-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #fff3cd;
        border: 2px solid #ffeaa7;
        margin: 10px 0;
    }
    .agent-step {
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid #4CAF50;
        background-color: #f1f8f4;
    }
    .agent-step.active {
        border-left-color: #2196F3;
        background-color: #e3f2fd;
    }
    .agent-step.complete {
        border-left-color: #4CAF50;
        background-color: #e8f5e9;
    }
    </style>
""", unsafe_allow_html=True)

# ================================================================
# TITLE AND INTRODUCTION
# ================================================================

st.title("🤖 Lumibot Strategy Generator")
st.markdown("### **Enhanced with Claude Code AI Agents**")

st.markdown("""
<div class="info-box">
<b>🚀 Multi-Agent Strategy Generation</b><br>
This enhanced version uses 5 specialized AI agents working together to create production-quality Lumibot strategies:
<ul>
<li><b>Researcher</b> - Extracts precise trading rules from your content</li>
<li><b>Architect</b> - Designs clean, maintainable code structure</li>
<li><b>Coder</b> - Implements production-ready Python code</li>
<li><b>Validator</b> - Validates code quality and API compliance</li>
<li><b>Optimizer</b> - Refines and optimizes the final strategy</li>
</ul>
<i>Result: Production-quality code with comprehensive error handling, logging, and documentation</i>
</div>
""", unsafe_allow_html=True)

# ================================================================
# SIDEBAR CONFIGURATION
# ================================================================

with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("Input Method")
    input_type = st.radio(
        "Select input type:",
        ["YouTube URL", "PDF Upload", "Text Input"],
        help="Choose how you want to provide the trading strategy"
    )

    st.divider()

    st.subheader("Strategy Settings")

    strategy_name = st.text_input(
        "Strategy Name",
        value="my_strategy",
        help="Name for the generated strategy file (no spaces)"
    )

    # Replace spaces with underscores
    strategy_name = strategy_name.replace(' ', '_').lower()

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
        value=0.001,
        step=0.001,
        format="%.3f",
        help="Trading commission as percentage (0.001 = 0.1%)"
    )

    st.divider()

    st.subheader("Agent Options")

    show_intermediate = st.checkbox(
        "Show Intermediate Outputs",
        value=True,
        help="Display analysis and architecture documents"
    )

    auto_backtest = st.checkbox(
        "Auto-run Backtest",
        value=False,
        help="Automatically run backtest after code generation"
    )

    st.divider()
    st.caption("Built with Claude Code Agents + Lumibot + Streamlit")

# ================================================================
# MAIN CONTENT AREA
# ================================================================

# Two-column layout
col1, col2 = st.columns([1, 1])

# LEFT COLUMN: INPUT
with col1:
    st.header("📥 Input Strategy")

    content = None

    if input_type == "YouTube URL":
        st.markdown("Enter a YouTube URL of a trading strategy video:")
        st.info("💡 **Tip**: Videos with clear entry/exit rules work best")

        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed"
        )

        if st.button("📺 Extract Transcript", type="primary", use_container_width=True):
            if youtube_url:
                with st.spinner("Extracting transcript from YouTube..."):
                    try:
                        # Extract video ID
                        if 'v=' in youtube_url:
                            video_id = youtube_url.split('v=')[1].split('&')[0]
                        elif 'youtu.be/' in youtube_url:
                            video_id = youtube_url.split('youtu.be/')[1].split('?')[0]
                        else:
                            video_id = youtube_url

                        # Fetch transcript
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        content = ' '.join([item['text'] for item in transcript_list])
                        st.session_state['content'] = content

                        st.success(f"✅ Transcript extracted! ({len(content)} characters)")

                    except Exception as e:
                        error_msg = str(e)
                        if "Too Many Requests" in error_msg or "429" in error_msg:
                            st.error("🚫 YouTube rate limit exceeded. Try 'Text Input' mode instead.")
                        else:
                            st.error(f"❌ Error: {error_msg}")
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
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)

                    # Parse PDF
                    reader = PyPDF2.PdfReader(uploaded_file)
                    text = ''

                    for page in reader.pages:
                        text += page.extract_text() + '\n'

                    content = text
                    st.session_state['content'] = content

                    st.success(f"✅ PDF parsed! ({len(content)} characters)")

                except Exception as e:
                    st.error(f"❌ Error parsing PDF: {str(e)}")

    elif input_type == "Text Input":
        st.markdown("Paste or type your trading strategy description:")

        content = st.text_area(
            "Strategy Description",
            height=300,
            placeholder="Example:\n\nBuy SPY when RSI(14) crosses below 30 (oversold).\nSell SPY when RSI(14) crosses above 70 (overbought).\n\nTimeframe: Daily\nPosition size: 95% of cash\nTake profit: 10%\nStop loss: 5%",
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

    if st.button(
        "🚀 Generate Lumibot Strategy with AI Agents",
        type="primary",
        use_container_width=True,
        disabled='content' not in st.session_state
    ):
        if 'content' not in st.session_state or not st.session_state['content']:
            st.error("Please provide input first!")
            st.stop()

        # Agent workflow visualization
        st.markdown("### 🤖 Agent Workflow")

        # Create placeholders for agent progress
        agent_progress_container = st.container()
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Agent step tracking
        agent_steps = {
            1: {"name": "🔍 Researcher", "desc": "Analyzing strategy content", "status": "pending"},
            2: {"name": "🏗️ Architect", "desc": "Designing architecture", "status": "pending"},
            3: {"name": "💻 Coder", "desc": "Implementing code", "status": "pending"},
            4: {"name": "✅ Validator", "desc": "Validating quality", "status": "pending"},
            5: {"name": "⚡ Optimizer", "desc": "Optimizing code", "status": "pending"},
        }

        # Display agent steps
        with agent_progress_container:
            step_placeholders = {}
            for step_num, step_info in agent_steps.items():
                step_placeholders[step_num] = st.empty()
                step_placeholders[step_num].markdown(
                    f'<div class="agent-step">{step_info["name"]}: {step_info["desc"]}</div>',
                    unsafe_allow_html=True
                )

        # Progress callback for agent coordination
        def update_progress(step, total, message, progress_pct):
            # Update progress bar
            progress_bar.progress(progress_pct / 100)
            status_text.text(f"[{step}/{total}] {message}")

            # Update agent step status
            if step in step_placeholders:
                agent_steps[step]["status"] = "active"
                step_placeholders[step].markdown(
                    f'<div class="agent-step active">✨ {agent_steps[step]["name"]}: {message}</div>',
                    unsafe_allow_html=True
                )

            # Mark previous steps as complete
            for i in range(1, step):
                if i in step_placeholders and agent_steps[i]["status"] != "complete":
                    agent_steps[i]["status"] = "complete"
                    step_placeholders[i].markdown(
                        f'<div class="agent-step complete">✅ {agent_steps[i]["name"]}: Complete</div>',
                        unsafe_allow_html=True
                    )

        # Generate strategy using Claude Code agents
        with st.spinner("AI Agents are working..."):
            result = generate_lumibot_strategy(
                content=st.session_state['content'],
                strategy_name=strategy_name,
                content_type=input_type.lower().replace(' ', '_'),
                progress_callback=update_progress
            )

        # Mark all steps as complete
        for step_num in step_placeholders:
            agent_steps[step_num]["status"] = "complete"
            step_placeholders[step_num].markdown(
                f'<div class="agent-step complete">✅ {agent_steps[step_num]["name"]}: Complete</div>',
                unsafe_allow_html=True
            )

        progress_bar.progress(100)
        status_text.text("✅ All agents completed!")

        # Store result in session
        if result['success']:
            st.session_state['generation_result'] = result
            st.success("✅ Strategy generated successfully!")

            # Show validation status
            validation = result.get('validation_report', {})
            if validation.get('is_valid'):
                st.success("✅ Code validation passed!")
            else:
                st.warning("⚠️ Code was optimized to fix validation issues")
        else:
            st.error(f"❌ Generation failed: {result.get('error')}")
            st.stop()

# ================================================================
# GENERATED CONTENT DISPLAY
# ================================================================

if 'generation_result' in st.session_state:
    result = st.session_state['generation_result']

    st.divider()

    # Intermediate outputs (if enabled)
    if show_intermediate:
        st.header("📊 AI Agent Outputs")

        tab1, tab2, tab3 = st.tabs(["📋 Analysis", "🏗️ Architecture", "✅ Validation"])

        with tab1:
            st.markdown("### Strategy Analysis (Researcher Agent)")
            st.markdown(result.get('analysis', 'No analysis available'))

        with tab2:
            st.markdown("### Architecture Design (Architect Agent)")
            st.markdown(result.get('architecture', 'No architecture available'))

        with tab3:
            st.markdown("### Validation Report (Validator Agent)")
            validation = result.get('validation_report', {})

            col1, col2, col3 = st.columns(3)
            with col1:
                status = "✅ PASSED" if validation.get('is_valid') else "❌ FAILED"
                st.metric("Status", status)
            with col2:
                st.metric("Critical Issues", len(validation.get('critical_issues', [])))
            with col3:
                st.metric("Warnings", len(validation.get('warnings', [])))

            if validation.get('critical_issues'):
                st.markdown("**Critical Issues:**")
                for issue in validation['critical_issues']:
                    st.markdown(f"- ❌ {issue}")

            if validation.get('warnings'):
                st.markdown("**Warnings:**")
                for warning in validation['warnings']:
                    st.markdown(f"- ⚠️ {warning}")

    st.divider()

    # Generated code
    st.header("💻 Generated Lumibot Strategy Code")

    code = result.get('strategy_code', '')
    st.code(code, language='python', line_numbers=True)

    # Download buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="📥 Download Strategy Code",
            data=code,
            file_name=f"{strategy_name}.py",
            mime="text/x-python",
            use_container_width=True
        )

    with col2:
        if 'analysis' in result:
            st.download_button(
                label="📥 Download Analysis",
                data=result['analysis'],
                file_name=f"{strategy_name}_analysis.md",
                mime="text/markdown",
                use_container_width=True
            )

    with col3:
        if 'architecture' in result:
            st.download_button(
                label="📥 Download Architecture",
                data=result['architecture'],
                file_name=f"{strategy_name}_architecture.md",
                mime="text/markdown",
                use_container_width=True
            )

    # Backtest section (simplified - actual backtesting would require more setup)
    if auto_backtest or st.button("▶️ Run Backtest", type="primary", use_container_width=True):
        st.divider()
        st.header("📊 Backtest Results")

        st.info(f"""
        🎯 **Backtest Configuration:**
        - Symbol: {backtest_symbol}
        - Period: {start_date} to {end_date}
        - Initial Cash: ${initial_cash:,.2f}
        - Commission: {commission * 100:.2f}%

        ⚠️ **Note**: To run actual backtest, save the generated code and execute it with proper credentials.py setup.
        """)

        st.markdown("""
        ### How to Run Backtest:

        1. **Save the generated code** to a .py file
        2. **Set up credentials.py** with your Polygon.io API key
        3. **Run the strategy file**: `python {strategy_name}.py`
        4. **View results** in the generated tearsheet HTML file

        For detailed instructions, see the Quick Start guide in the generated README.
        """.format(strategy_name=strategy_name))

# ================================================================
# FOOTER
# ================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>Powered by Claude Code AI Agents</b></p>
    <p>Multi-agent architecture: Researcher → Architect → Coder → Validator → Optimizer</p>
    <p><i>Original concept based on Moon Dev's RBI agent pattern</i></p>
    <p style="font-size: 12px; margin-top: 10px;">
        ⚠️ Generated strategies are for educational purposes. Always backtest thoroughly
        and paper trade before using with real money. Trading involves risk of loss.
    </p>
</div>
""", unsafe_allow_html=True)
