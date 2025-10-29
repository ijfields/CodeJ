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
from claude_agent_integration import generate_instruction_file, validate_instruction_file

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
<b>🚀 Two-Stage Strategy Generation Workflow</b><br>
This enhanced version uses a two-stage approach for maximum control and quality:
<br><br>
<b>Stage 1 (This App):</b> Content → Structured Instruction File
<ul>
<li>Extract strategy from YouTube, PDF, or text</li>
<li>Structure into template-compliant instruction file</li>
<li>Review and edit instructions before code generation</li>
<li>Save to: Outputs/Inscructions/</li>
</ul>
<b>Stage 2 (Claude Code):</b> Instruction File → Production Strategy
<ul>
<li>Use /lumibot-generate command with instruction file</li>
<li>5 specialized AI agents generate production code</li>
<li>Complete strategy + tests + validation + documentation</li>
</ul>
<i>Result: Full control over requirements + production-quality code from proven workflow</i>
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
                        st.session_state['youtube_url'] = youtube_url  # Store URL for instruction file

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
        "📝 Generate Instruction File (Stage 1)",
        type="primary",
        use_container_width=True,
        disabled='content' not in st.session_state
    ):
        if 'content' not in st.session_state or not st.session_state['content']:
            st.error("Please provide input first!")
            st.stop()

        # Instruction file generation workflow
        st.markdown("### 📝 Stage 1: Instruction File Generation")

        # Create placeholders for progress
        progress_container = st.container()
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Workflow step tracking (simplified for instruction generation)
        workflow_steps = {
            1: {"name": "📖 Extract", "desc": "Analyzing strategy content", "status": "pending"},
            2: {"name": "📋 Structure", "desc": "Structuring instruction file", "status": "pending"},
            3: {"name": "💾 Save", "desc": "Saving instruction file", "status": "pending"},
        }

        # Display workflow steps
        with progress_container:
            step_placeholders = {}
            for step_num, step_info in workflow_steps.items():
                step_placeholders[step_num] = st.empty()
                step_placeholders[step_num].markdown(
                    f'<div class="agent-step">{step_info["name"]}: {step_info["desc"]}</div>',
                    unsafe_allow_html=True
                )

        # Progress callback for workflow tracking
        def update_progress(step, total, message, progress_pct):
            # Update progress bar
            progress_bar.progress(progress_pct / 100)
            status_text.text(f"[{step}/{total}] {message}")

            # Update workflow step status
            if step in step_placeholders:
                workflow_steps[step]["status"] = "active"
                step_placeholders[step].markdown(
                    f'<div class="agent-step active">✨ {workflow_steps[step]["name"]}: {message}</div>',
                    unsafe_allow_html=True
                )

            # Mark previous steps as complete
            for i in range(1, step):
                if i in step_placeholders and workflow_steps[i]["status"] != "complete":
                    workflow_steps[i]["status"] = "complete"
                    step_placeholders[i].markdown(
                        f'<div class="agent-step complete">✅ {workflow_steps[i]["name"]}: Complete</div>',
                        unsafe_allow_html=True
                    )

        # Generate instruction file
        youtube_url = st.session_state.get('youtube_url', None)  # Store URL if from YouTube
        with st.spinner("Generating instruction file..."):
            result = generate_instruction_file(
                content=st.session_state['content'],
                strategy_name=strategy_name,
                source_type=input_type.lower().replace(' ', '_'),
                source_url=youtube_url,
                progress_callback=update_progress
            )

        # Mark all steps as complete
        for step_num in step_placeholders:
            workflow_steps[step_num]["status"] = "complete"
            step_placeholders[step_num].markdown(
                f'<div class="agent-step complete">✅ {workflow_steps[step_num]["name"]}: Complete</div>',
                unsafe_allow_html=True
            )

        progress_bar.progress(100)
        status_text.text("✅ Instruction file generated!")

        # Store result in session
        if result['success']:
            st.session_state['generation_result'] = result
            st.success("✅ Instruction file generated successfully!")
            st.info(f"📁 Saved to: `{result.get('file_path')}`")
        else:
            st.error(f"❌ Generation failed: {result.get('error')}")
            st.stop()

# ================================================================
# INSTRUCTION FILE DISPLAY
# ================================================================

if 'generation_result' in st.session_state:
    result = st.session_state['generation_result']

    st.divider()

    # Instruction file content
    st.header("📝 Generated Instruction File")

    instruction_content = result.get('instruction_file', '')
    file_path = result.get('file_path', '')

    st.markdown(f"""
    <div class="success-box">
    <b>✅ Stage 1 Complete: Instruction File Generated</b><br>
    File saved to: <code>{file_path}</code>
    </div>
    """, unsafe_allow_html=True)

    # Preview of instruction file
    st.markdown("### 📖 Preview")
    st.markdown(result.get('preview', 'No preview available'))

    # Editable instruction file
    st.markdown("### ✏️ Review and Edit Instructions")
    st.markdown("""
    **Instructions:** Review the generated instruction file below. Edit any sections to add specifics from your strategy.
    Make sure to:
    - Complete all `[TODO]` sections
    - Add `**CRITICAL:**` markers for important details
    - Specify exact quantities (not vague like "sell calls" → "sell 2 calls")
    - Add specific dates for testing if known
    """)

    edited_instruction = st.text_area(
        "Instruction File Content",
        value=instruction_content,
        height=400,
        label_visibility="collapsed"
    )

    # Save edited version button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Edited Instructions", type="primary", use_container_width=True):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(edited_instruction)
                st.success(f"✅ Saved to: {file_path}")
            except Exception as e:
                st.error(f"❌ Save failed: {str(e)}")

    with col2:
        st.download_button(
            label="📥 Download Instructions",
            data=edited_instruction,
            file_name=f"{strategy_name}_instructions.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.divider()

    # Next steps for Stage 2
    st.header("🚀 Stage 2: Generate Strategy Code")

    st.markdown("""
    <div class="warning-box">
    <b>⚠️ Next Steps - Run /lumibot-generate Command</b><br>
    After reviewing and editing the instruction file above, use the <code>/lumibot-generate</code> command
    in Claude Code to generate the actual strategy code.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    ### How to Generate Strategy Code:

    1. **Review and edit** the instruction file above (complete all TODO sections)
    2. **Save** your edits using the button above
    3. **Open Claude Code CLI** in your terminal
    4. **Run the command:**

    ```
    /lumibot-generate

    Read the instruction file at: {file_path}

    Generate a complete Lumibot strategy following the specifications.
    Output to: Outputs/Strategies/
    ```

    5. **Wait for agents** to generate:
       - Strategy code (`{strategy_name}.py`)
       - Test scripts
       - Validation reports
       - Documentation

    ### What Happens in Stage 2:

    The `/lumibot-generate` command will invoke 5 specialized AI agents:
    - **🔍 Researcher** - Analyzes instruction file
    - **🏗️ Architect** - Designs strategy architecture
    - **💻 Coder** - Implements production code
    - **✅ Validator** - Validates code quality
    - **⚡ Optimizer** - Refines and optimizes

    ### Expected Outputs:

    - `Outputs/Strategies/{strategy_name}.py` - Main strategy file
    - `Outputs/Strategies/{strategy_name}_analysis.md` - Strategy analysis
    - `Outputs/Strategies/{strategy_name}_architecture.md` - Architecture design
    - `Outputs/Strategies/{strategy_name}_validation.md` - Validation report
    - Test scripts and validator scripts

    ### Testing the Generated Strategy:

    Once the strategy is generated, you can:
    1. Review the generated code
    2. Run backtests with your specified date ranges
    3. Validate results with the generated validator
    4. Compare performance against benchmarks
    """)

# ================================================================
# FOOTER
# ================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><b>Powered by Claude Code AI Agents</b></p>
    <p>Two-Stage Workflow: Content → Instruction File → /lumibot-generate → Production Strategy</p>
    <p><i>Template based on Zero Loss Butterfly lessons learned</i></p>
    <p style="font-size: 12px; margin-top: 10px;">
        ⚠️ Generated strategies are for educational purposes. Always backtest thoroughly
        and paper trade before using with real money. Trading involves risk of loss.
    </p>
</div>
""", unsafe_allow_html=True)
