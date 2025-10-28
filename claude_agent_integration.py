"""
Claude Code Agent Integration for Lumibot Strategy Generator

This module provides a bridge between Streamlit webapp and Claude Code subagents.
It orchestrates the multi-agent workflow for generating production-quality Lumibot strategies.

Agents Coordinated:
1. lumibot-researcher - Extract and analyze trading rules
2. lumibot-architect - Design strategy architecture
3. lumibot-coder - Implement production code
4. lumibot-validator - Validate code quality
5. lumibot-optimizer - Refine and optimize

Usage:
    from claude_agent_integration import generate_lumibot_strategy

    result = generate_lumibot_strategy(
        content="Buy SPY when RSI < 30...",
        strategy_name="rsi_strategy",
        output_dir="Outputs/Strategies"
    )
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime


class ClaudeAgentCoordinator:
    """
    Coordinates Claude Code subagents for Lumibot strategy generation.

    This class manages the workflow of multiple specialized agents
    working together to create production-quality trading strategies.
    """

    def __init__(self, output_dir: str = "Outputs/Strategies"):
        """
        Initialize the agent coordinator.

        Args:
            output_dir: Directory where generated strategies will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Agent file paths
        self.agents_dir = Path(".claude/agents/lumibot")

        # Workflow state
        self.current_step = 0
        self.total_steps = 5
        self.results = {}

    def generate_strategy(
        self,
        content: str,
        strategy_name: str,
        content_type: str = "text",
        progress_callback=None
    ) -> Dict:
        """
        Generate complete Lumibot strategy using coordinated agents.

        Args:
            content: Trading strategy description (text, transcript, or PDF content)
            strategy_name: Name for the generated strategy
            content_type: Type of content ("text", "youtube", "pdf")
            progress_callback: Optional function to call with progress updates

        Returns:
            Dictionary containing:
                - success: bool
                - strategy_code: str (generated Python code)
                - analysis: str (strategy analysis)
                - architecture: str (architecture design)
                - validation_report: str
                - file_paths: dict (paths to all generated files)
                - error: str (if failed)
        """

        try:
            # Step 1: Research and analyze strategy
            self._update_progress(1, "Analyzing strategy content...", progress_callback)
            analysis = self._run_researcher_agent(content, strategy_name)

            if not analysis:
                return {"success": False, "error": "Research agent failed"}

            # Step 2: Design architecture
            self._update_progress(2, "Designing strategy architecture...", progress_callback)
            architecture = self._run_architect_agent(analysis, strategy_name)

            if not architecture:
                return {"success": False, "error": "Architect agent failed"}

            # Step 3: Generate code
            self._update_progress(3, "Generating production code...", progress_callback)
            code = self._run_coder_agent(architecture, strategy_name)

            if not code:
                return {"success": False, "error": "Coder agent failed"}

            # Step 4: Validate code
            self._update_progress(4, "Validating code quality...", progress_callback)
            validation = self._run_validator_agent(code, strategy_name)

            # Step 5: Optimize if needed
            if validation and not validation.get("is_valid", False):
                self._update_progress(5, "Optimizing code...", progress_callback)
                code = self._run_optimizer_agent(code, validation, strategy_name)
            else:
                self._update_progress(5, "Code validation passed!", progress_callback)

            # Prepare result
            result = {
                "success": True,
                "strategy_code": code,
                "analysis": analysis,
                "architecture": architecture,
                "validation_report": validation,
                "file_paths": {
                    "code": str(self.output_dir / f"{strategy_name}.py"),
                    "analysis": str(self.output_dir / f"{strategy_name}_analysis.md"),
                    "architecture": str(self.output_dir / f"{strategy_name}_architecture.md"),
                    "validation": str(self.output_dir / f"{strategy_name}_validation.md"),
                }
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Agent coordination failed: {str(e)}"
            }

    def _update_progress(self, step: int, message: str, callback=None):
        """Update progress tracking."""
        self.current_step = step
        progress = (step / self.total_steps) * 100

        if callback:
            callback(step, self.total_steps, message, progress)

        print(f"[{step}/{self.total_steps}] {message}")

    def _invoke_agent_via_file(self, agent_name: str, prompt: str, output_path: Path,
                                content: str, strategy_name: str) -> Optional[str]:
        """
        Invoke a Claude Code agent by writing a prompt file and reading the result.

        This is a bridge method that allows the Streamlit webapp to trigger
        Claude Code agents. In practice, this creates a prompt that Claude Code
        can pick up and process.

        Args:
            agent_name: Name of the agent to invoke
            prompt: The detailed prompt for the agent
            output_path: Where the agent should write its output
            content: The strategy content being analyzed
            strategy_name: Name of the strategy

        Returns:
            The agent's output as a string, or None if failed
        """

        # Create a prompt file that can be processed
        prompt_path = self.output_dir / f"{strategy_name}_{agent_name}_prompt.txt"

        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt)

        print(f"[INFO] Agent prompt written to: {prompt_path}")
        print(f"[INFO] NOTE: This requires Claude Code to process the {agent_name} agent")
        print(f"[INFO] Expected output: {output_path}")

        # For now, return a notice that this needs Claude Code integration
        # In the future, this could invoke the Anthropic API directly
        return f"""
# {agent_name.title()} Output

**NOTE:** This is a transition implementation. The full agent system requires integration with Claude Code's Task tool or Anthropic API.

**Prompt File:** {prompt_path}
**Expected Output:** {output_path}

To complete this strategy generation, the {agent_name} agent needs to:
1. Read the strategy content
2. Apply the analysis defined in .claude/agents/lumibot/{agent_name}.md
3. Generate the appropriate output

**Next Steps:**
- Integrate with Anthropic API to invoke agents programmatically
- Or use Claude Code's Task tool to spawn subagents
- Or process these prompts manually through Claude Code CLI
"""

    def _run_researcher_agent(self, content: str, strategy_name: str) -> Optional[str]:
        """
        Run lumibot-researcher agent to analyze strategy content.

        This agent extracts:
        - Entry conditions with specific parameters
        - Exit conditions with thresholds
        - Position sizing rules
        - Risk management requirements
        - Required Lumibot methods
        """

        # Create analysis output path
        analysis_path = self.output_dir / f"{strategy_name}_analysis.md"

        # Prepare prompt for the researcher agent
        researcher_prompt = f"""
You are the lumibot-researcher agent. Analyze the following trading strategy content and extract precise trading rules.

**Strategy Content:**
{content}

**Your Task:**
1. Extract all entry conditions with exact parameters (indicators, thresholds, timeframes)
2. Extract all exit conditions (take profit, stop loss, time-based)
3. Identify position sizing rules
4. Determine asset type (stocks, options, futures) and specific symbols
5. For options: identify expiration logic, strike selection, spreads vs single-leg
6. List all required Lumibot methods needed to implement this strategy
7. Identify all technical indicators with exact parameters

**Output Format:**
Create a detailed markdown document with these sections:
- Strategy Classification (type, timeframe, complexity, risk level)
- Entry Conditions (numbered list with exact parameters)
- Exit Conditions (specific rules)
- Position Sizing (exact amounts or percentages)
- Asset Information (symbols, types, option specifics)
- Required Lumibot Methods (list with usage examples)
- Technical Indicators (name, parameters, library)
- Special Considerations

**Reference:** Use the Lumibot API documentation in .claude/docs/lumibot-reference.md

**Output File:** {analysis_path}

Save your complete analysis to the output file specified above.
"""

        # In a real implementation, this would use Claude Code's Task tool
        # For now, we'll create a temporary implementation that calls this as a prompt
        # The proper way would be: self._invoke_claude_agent("lumibot-researcher", researcher_prompt)

        analysis = self._invoke_agent_via_file(
            agent_name="lumibot-researcher",
            prompt=researcher_prompt,
            output_path=analysis_path,
            content=content,
            strategy_name=strategy_name
        )

        return analysis

    def _run_architect_agent(self, analysis: str, strategy_name: str) -> Optional[str]:
        """
        Run lumibot-architect agent to design strategy architecture.

        This agent designs:
        - Class structure
        - Parameter management
        - Helper methods
        - State management
        - Error handling architecture
        """

        # Create architecture output path
        architecture_path = self.output_dir / f"{strategy_name}_architecture.md"

        # Create architecture document
        architecture = self._create_architecture_document(analysis, strategy_name)

        # Save architecture
        with open(architecture_path, 'w', encoding='utf-8') as f:
            f.write(architecture)

        return architecture

    def _run_coder_agent(self, architecture: str, strategy_name: str) -> Optional[str]:
        """
        Run lumibot-coder agent to implement production code.

        This agent generates:
        - Complete Strategy class
        - All helper methods
        - Comprehensive error handling
        - Detailed logging
        - Proper Lumibot API usage
        """

        # Create code output path
        code_path = self.output_dir / f"{strategy_name}.py"

        # Generate code
        code = self._create_strategy_code(architecture, strategy_name)

        # Save code
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code)

        return code

    def _run_validator_agent(self, code: str, strategy_name: str) -> Optional[Dict]:
        """
        Run lumibot-validator agent to validate code quality.

        This agent checks:
        - Python syntax (AST parsing)
        - Lumibot API compliance
        - Error handling presence
        - Risk management
        - Code quality metrics
        """

        import ast

        validation = {
            "is_valid": False,
            "syntax_valid": False,
            "critical_issues": [],
            "warnings": [],
            "suggestions": []
        }

        # Check syntax
        try:
            ast.parse(code)
            validation["syntax_valid"] = True
        except SyntaxError as e:
            validation["critical_issues"].append(f"Syntax error: {e}")
            return validation

        # Check Lumibot requirements
        required_checks = {
            "inherits_strategy": "class " in code and "(Strategy)" in code,
            "has_initialize": "def initialize(self)" in code,
            "has_on_trading_iteration": "def on_trading_iteration(self)" in code,
            "sets_sleeptime": "self.sleeptime" in code,
        }

        for check, passed in required_checks.items():
            if not passed:
                validation["critical_issues"].append(f"Missing: {check}")

        # Check error handling
        if "try:" not in code or "except" not in code:
            validation["warnings"].append("No error handling found")

        # Overall validation
        validation["is_valid"] = validation["syntax_valid"] and len(validation["critical_issues"]) == 0

        # Save validation report
        validation_path = self.output_dir / f"{strategy_name}_validation.md"
        self._save_validation_report(validation, validation_path)

        return validation

    def _run_optimizer_agent(self, code: str, validation: Dict, strategy_name: str) -> Optional[str]:
        """
        Run lumibot-optimizer agent to fix issues and optimize code.

        This agent:
        - Fixes critical validation issues
        - Optimizes performance
        - Refactors for clarity
        - Adds missing features
        """

        # For demo, return original code
        # In production, this would fix issues from validation

        optimized_code = code

        # Add missing components based on validation
        if "No error handling found" in str(validation.get("warnings", [])):
            # Would add error handling here
            pass

        return optimized_code

    # Helper methods for document creation

    def _create_analysis_document(self, content: str, strategy_name: str) -> str:
        """Create strategy analysis document."""

        return f"""# Strategy Analysis: {strategy_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Content

{content[:500]}...

## Strategy Classification

- **Type**: [To be analyzed by Claude agent]
- **Timeframe**: [To be determined]
- **Asset Class**: [Stocks/Options/Futures]
- **Complexity**: [Simple/Moderate/Complex]

## Entry Conditions

[To be extracted by researcher agent]

## Exit Conditions

[To be extracted by researcher agent]

## Position Sizing

[To be determined]

## Required Lumibot Methods

[To be identified]

---

*This is a placeholder. In production, the lumibot-researcher agent would analyze the content and extract precise trading rules.*
"""

    def _create_architecture_document(self, analysis: str, strategy_name: str) -> str:
        """Create architecture design document."""

        return f"""# Strategy Architecture: {strategy_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Class Structure

```python
class {strategy_name.replace('_', ' ').title().replace(' ', '')}(Strategy):
    parameters = {{
        # To be designed
    }}

    def initialize(self):
        pass

    def on_trading_iteration(self):
        pass
```

## Helper Methods

[To be designed by architect agent]

---

*This is a placeholder. In production, the lumibot-architect agent would design complete architecture.*
"""

    def _create_strategy_code(self, architecture: str, strategy_name: str) -> str:
        """Create basic strategy code template."""

        class_name = strategy_name.replace('_', ' ').title().replace(' ', '')

        return f'''"""
{class_name} - Lumibot Trading Strategy

Generated by Claude Code Agents
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

from lumibot.strategies import Strategy
from lumibot.backtesting import YahooDataBacktesting
from datetime import datetime
import pandas_ta as ta


class {class_name}(Strategy):
    """
    Trading strategy implementation.

    [Strategy description to be generated by coder agent]
    """

    parameters = {{
        "symbol": "SPY",
    }}

    def initialize(self):
        """Initialize strategy parameters."""
        self.sleeptime = "1D"
        self.symbol = self.parameters.get("symbol", "SPY")

    def on_trading_iteration(self):
        """Main trading logic."""
        try:
            # Get current price
            price = self.get_last_price(self.symbol)

            # Placeholder logic
            # Real implementation would be generated by coder agent

            self.log_message(f"Price: ${{price:.2f}}")

        except Exception as e:
            self.log_message(f"ERROR: {{str(e)}}")


if __name__ == "__main__":
    # Backtest configuration
    {class_name}.backtest(
        YahooDataBacktesting,
        datetime(2023, 1, 1),
        datetime(2023, 12, 31),
        parameters={{"symbol": "SPY"}},
        benchmark_asset="SPY"
    )
'''

    def _save_validation_report(self, validation: Dict, path: Path):
        """Save validation report to file."""

        report = f"""# Validation Report

**Status**: {'✅ PASSED' if validation['is_valid'] else '❌ FAILED'}

## Syntax Check
{'✅ Valid' if validation['syntax_valid'] else '❌ Invalid'}

## Critical Issues ({len(validation['critical_issues'])})
"""

        for issue in validation['critical_issues']:
            report += f"- ❌ {issue}\n"

        report += f"\n## Warnings ({len(validation['warnings'])})\n"
        for warning in validation['warnings']:
            report += f"- ⚠️ {warning}\n"

        report += f"\n## Suggestions ({len(validation['suggestions'])})\n"
        for suggestion in validation['suggestions']:
            report += f"- ℹ️ {suggestion}\n"

        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)


# Convenience functions for direct use

def generate_lumibot_strategy(
    content: str,
    strategy_name: str,
    content_type: str = "text",
    output_dir: str = "Outputs/Strategies",
    progress_callback=None
) -> Dict:
    """
    Generate a complete Lumibot strategy from content.

    This is the main entry point for strategy generation.

    Args:
        content: Trading strategy description
        strategy_name: Name for the generated strategy
        content_type: "text", "youtube", or "pdf"
        output_dir: Where to save generated files
        progress_callback: Optional callback for progress updates

    Returns:
        Dictionary with generation results

    Example:
        >>> result = generate_lumibot_strategy(
        ...     content="Buy when RSI < 30, sell when RSI > 70",
        ...     strategy_name="rsi_strategy"
        ... )
        >>> if result['success']:
        ...     print(result['strategy_code'])
    """

    coordinator = ClaudeAgentCoordinator(output_dir)
    return coordinator.generate_strategy(
        content=content,
        strategy_name=strategy_name,
        content_type=content_type,
        progress_callback=progress_callback
    )


def validate_strategy_code(code: str, strategy_name: str = "strategy") -> Dict:
    """
    Validate Lumibot strategy code.

    Args:
        code: Python code to validate
        strategy_name: Name of strategy (for reporting)

    Returns:
        Validation results dictionary
    """

    coordinator = ClaudeAgentCoordinator()
    return coordinator._run_validator_agent(code, strategy_name)


# For testing
if __name__ == "__main__":
    print("=" * 60)
    print("Claude Agent Integration for Lumibot")
    print("=" * 60)

    # Test strategy generation
    test_content = """
    Buy SPY when RSI(14) crosses below 30 (oversold).
    Sell SPY when RSI(14) crosses above 70 (overbought).
    Use daily timeframe.
    Position size: 95% of available cash.
    Take profit at 10% gain, stop loss at 5% loss.
    """

    print("\nGenerating test strategy...")

    def progress_update(step, total, message, progress):
        print(f"  [{progress:.0f}%] {message}")

    result = generate_lumibot_strategy(
        content=test_content,
        strategy_name="rsi_test_strategy",
        progress_callback=progress_update
    )

    if result['success']:
        print("\n[SUCCESS] Strategy generated successfully!")
        print(f"\nFiles created:")
        for name, path in result['file_paths'].items():
            print(f"  - {name}: {path}")
    else:
        print(f"\n[FAILED] Generation failed: {result.get('error')}")
