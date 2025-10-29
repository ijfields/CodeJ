"""
Claude Code Agent Integration for Lumibot Strategy Generator

This module provides a bridge between Streamlit webapp and instruction file generation.
It structures trading strategy content into comprehensive instruction files that can be
used with /lumibot-generate command.

Two-Stage Workflow:
Stage 1 (This Module): Content → Instruction File
Stage 2 (Manual): Instruction File → /lumibot-generate → Strategy Code

The instruction file follows the template format refined from Zero Loss Butterfly experience,
incorporating critical implementation details, testing requirements, and expected outcomes.

Usage:
    from claude_agent_integration import generate_instruction_file

    result = generate_instruction_file(
        content="Buy SPY when RSI < 30...",
        strategy_name="rsi_strategy",
        source_type="youtube"
    )
"""

import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class InstructionFileGenerator:
    """
    Generates structured instruction files from trading strategy content.

    This class takes raw strategy content (from YouTube, PDF, or text)
    and structures it into a template-compliant instruction file that
    can be used with /lumibot-generate command.
    """

    def __init__(self, output_dir: str = "Outputs/Inscructions"):
        """
        Initialize the instruction file generator.

        Args:
            output_dir: Directory where instruction files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load template reference
        self.template_path = self.output_dir / "TEMPLATE_zero_loss_butterfly.txt"

    def generate_instruction_file(
        self,
        content: str,
        strategy_name: str,
        source_type: str = "text",
        source_url: str = None,
        progress_callback=None
    ) -> Dict:
        """
        Generate instruction file from strategy content.

        Args:
            content: Trading strategy description (text, transcript, or PDF content)
            strategy_name: Name for the strategy
            source_type: Type of content ("text", "youtube", "pdf")
            source_url: Optional URL of source (for YouTube videos)
            progress_callback: Optional function to call with progress updates

        Returns:
            Dictionary containing:
                - success: bool
                - instruction_file: str (generated instruction content)
                - file_path: str (path to saved file)
                - preview: str (preview for UI)
                - error: str (if failed)
        """

        try:
            # Step 1: Extract key information
            if progress_callback:
                progress_callback(1, 3, "Analyzing strategy content...", 33)

            extracted_info = self._extract_strategy_info(content, source_type)

            # Step 2: Structure into template format
            if progress_callback:
                progress_callback(2, 3, "Structuring instruction file...", 66)

            instruction_content = self._create_instruction_file(
                extracted_info,
                strategy_name,
                source_type,
                source_url
            )

            # Step 3: Save to file
            if progress_callback:
                progress_callback(3, 3, "Saving instruction file...", 100)

            file_path = self.output_dir / f"{strategy_name}_instructions.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(instruction_content)

            # Create preview (first 1000 characters)
            preview = instruction_content[:1000]
            if len(instruction_content) > 1000:
                preview += "\n\n... (see full file for complete instructions)"

            return {
                "success": True,
                "instruction_file": instruction_content,
                "file_path": str(file_path),
                "preview": preview
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Instruction file generation failed: {str(e)}"
            }

    def _extract_strategy_info(self, content: str, source_type: str) -> Dict:
        """
        Extract key strategy information from content.

        This is a simplified extraction. In a full implementation,
        this would use NLP or Claude API to extract structured information.
        """

        # For now, return the raw content with metadata
        # The user will edit this in the Streamlit UI
        return {
            "content": content,
            "content_length": len(content),
            "source_type": source_type,
            "extracted_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _create_instruction_file(
        self,
        extracted_info: Dict,
        strategy_name: str,
        source_type: str,
        source_url: str = None
    ) -> str:
        """
        Create instruction file content following the template format.

        Template structure based on:
        - Outputs/Inscructions/README_TEMPLATE_GUIDE.md
        - Outputs/Inscructions/TEMPLATE_zero_loss_butterfly.txt
        """

        content = extracted_info["content"]

        # Generate instruction file with template structure
        instruction = f"""Strategy Instruction File
Generated: {extracted_info['extracted_date']}
Source: {source_type.upper()}"""

        if source_url:
            instruction += f"\nSource URL: {source_url}"

        instruction += f"""

Strategy Name: {strategy_name}

---

INSTRUCTIONS FOR EDITING:

This instruction file follows the template format from:
- Outputs/Inscructions/README_TEMPLATE_GUIDE.md
- Outputs/Inscructions/TEMPLATE_zero_loss_butterfly.txt

Please complete each section below based on the strategy content.
Mark critical implementation details with **CRITICAL:** prefix.

---

## Source Content

{content[:3000]}"""

        if len(content) > 3000:
            instruction += f"\n\n... (content truncated, total length: {len(content)} characters)"

        instruction += """

---

## Strategy Structure

**TODO: Complete the sections below by analyzing the source content above**

### Asset Class
- [Specify: Stocks, ETFs, Options, Futures]
- Primary symbols: [List specific symbols]
- Price range or other constraints: [If applicable]

### Entry Conditions

1. [First entry condition with specific parameters]
2. [Second entry condition]
3. [Additional conditions...]

**CRITICAL:** [Mark any critical quantity specifications, e.g., "2 contracts NOT 1"]

### Position Structure Verification
- Check actual positions: [How to verify correct structure]
- [Asset] should be purchased: [EXACTLY N times]
- If [scenario], then [action]
- Maintain [ratio/structure] at all times

### Exit Conditions

1. [Primary exit condition]
2. [Roll logic if applicable]
   - When: [days before expiration]
   - What to keep: [stock, etc.]
   - What to replace: [options, etc.]
3. If exit fails: [Retry logic, max attempts]
4. Exit entire position if: [End conditions]

### Position Sizing
- [Specify exact quantities]
- [Contract sizes]
- [Capital requirements]

### Risk Management

Stop Loss:
- [Specific stop loss rules or "None"]

Take Profit:
- [Specific take profit targets]

Maximum Position Size:
- [Maximum contracts/shares]

Capital at Risk:
- [Estimated capital requirement]

### Timeframe
- Position holding period: [Duration]
- Check frequency: [How often strategy runs]
- Execution timing: [Intraday, daily, etc.]

### Technical Indicators
- [List indicators with exact parameters]
- OR: "None - structure-based strategy"

---

## Implementation Requirements

**CRITICAL: [Most important implementation gotcha]**
- [Specific detail about position tracking]
- [Strike rounding logic if options]
- [Order execution sequence]

**Strike Selection Requirements** (if options):
- Query option chain with: `self.get_chains()`
- Round target strikes to nearest $[X]: `round(price / X) * X`
- Find nearest available strikes from chain

**Order Execution**:
- Submit [N] legs as separate orders
- Use market orders for backtesting reliability
- Check fill status on next iteration
- Log all order submissions with identifiers

**Position Management**:
- Every iteration: Check actual positions held
- Verify: [specific position structure]
- If mismatch: [re-entry logic]

---

## Testing Requirements

### 1. Confirmed Trade Test (if source has specific example)
- Date: [Specific dates from source]
- Symbol: [Specific symbol]
- Expected entry price: ~$[X]
- Expected outcome: [What should happen]
- Purpose: Validate strategy matches source specifications

### 2. Historical Data Test (Reliability)
- Date: [Suggest 1 year prior for complete data]
- Symbols: [Test with multiple symbols if applicable]
- Purpose: Complete data availability, successful execution
- Compare: [Performance between symbols or vs benchmark]

### 3. Validation Requirements
- Create validator script to check trades CSV:
  * Count [specific events]
  * Verify [specific structure]
  * Calculate [specific metrics]
  * Validate [specific behavior]

### 4. Performance Comparison
- Compare strategy vs [benchmark, e.g., buy-and-hold]
- Metrics: Total return, CAGR, Sharpe ratio, max drawdown
- Generate tearsheet for both strategy and benchmark
- Determine: Is this strategy profitable?

---

## Configuration

- Use parameterized backtesting dates (NOT environment variables)
- Create credentials.py for API keys (no dates in credentials)
- Each test script defines its own date range
- Follow pattern from StrategyTemplate.py

---

## Expected Deliverables

1. Complete Lumibot strategy class: {strategy_name}.py
2. Test script for confirmed trade: test_{strategy_name}_confirmed.py
3. Test script for historical data: test_{strategy_name}_historical.py
4. Validator script: {strategy_name}_validator.py
5. Configuration: credentials.py (template provided)
6. Documentation:
   - {strategy_name}_ANALYSIS.md (strategy analysis)
   - {strategy_name}_RESULTS.md (backtest results)
   - {strategy_name}_RECOMMENDATION.md (final assessment)

---

## Risk Assessment

Overall Risk Level: [LOW / MODERATE / HIGH / VERY HIGH]

Risks:
1. [Specific risk 1]
2. [Specific risk 2]
3. [Additional risks...]

Mitigation:
1. [How risk 1 is mitigated]
2. [How risk 2 is mitigated]
3. [Additional mitigations...]

---

## Expected Outcome

**TODO: After testing, document expected results here**

Based on testing:
- Strategy return: [X%]
- Benchmark return: [Y%]
- Volatility: [Reduction or increase]
- Sharpe ratio: [Value]

**RECOMMENDATION**: [PROFITABLE / NOT PROFITABLE / NEEDS MORE TESTING]

[Explanation of recommendation]

Better alternatives: [If not profitable, suggest alternatives]

---

## Implementation Notes

1. [Important note about strategy behavior]
2. [Market conditions where strategy works best]
3. [Limitations or considerations]
4. [Educational value vs production readiness]

---

## Next Steps

1. Review and complete all TODO sections above
2. Verify all quantities and parameters are specific (not vague)
3. Mark all critical details with **CRITICAL:** prefix
4. Save edited instruction file
5. Use with /lumibot-generate command:
   ```
   /lumibot-generate

   Read the instruction file at: {self.output_dir}/{strategy_name}_instructions.txt

   Generate a complete Lumibot strategy following the specifications.
   Output to: Outputs/Strategies/
   ```

---

Generated by: Lumibot Strategy Generator (Enhanced)
Template based on: Zero Loss Butterfly lessons learned
"""

        return instruction

    def validate_instruction_file(self, file_path: str) -> Dict:
        """
        Validate that an instruction file meets template requirements.

        Args:
            file_path: Path to instruction file to validate

        Returns:
            Dictionary with validation results
        """

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Required sections
            required_sections = [
                "Strategy Name:",
                "Entry Conditions",
                "Exit Conditions",
                "Position Sizing",
                "Risk Management",
                "Implementation Requirements",
                "Testing Requirements",
                "Expected Deliverables"
            ]

            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)

            # Check for CRITICAL markers
            has_critical_markers = "**CRITICAL:" in content

            # Check for TODO markers (should be completed)
            has_todos = "**TODO:" in content or "[TODO]" in content

            is_valid = len(missing_sections) == 0 and has_critical_markers

            return {
                "is_valid": is_valid,
                "missing_sections": missing_sections,
                "has_critical_markers": has_critical_markers,
                "has_incomplete_todos": has_todos,
                "validation_message": self._get_validation_message(
                    is_valid, missing_sections, has_critical_markers, has_todos
                )
            }

        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Validation failed: {str(e)}"
            }

    def _get_validation_message(
        self,
        is_valid: bool,
        missing_sections: list,
        has_critical: bool,
        has_todos: bool
    ) -> str:
        """Generate validation message."""

        if is_valid and not has_todos:
            return "✅ Instruction file is complete and ready for /lumibot-generate"

        messages = []

        if missing_sections:
            messages.append(f"❌ Missing sections: {', '.join(missing_sections)}")

        if not has_critical:
            messages.append("⚠️ No **CRITICAL:** markers found - add for important details")

        if has_todos:
            messages.append("⚠️ TODO markers found - complete these sections before generation")

        return "\n".join(messages)


# Convenience functions for direct use

def generate_instruction_file(
    content: str,
    strategy_name: str,
    source_type: str = "text",
    source_url: str = None,
    output_dir: str = "Outputs/Inscructions",
    progress_callback=None
) -> Dict:
    """
    Generate an instruction file from strategy content.

    This is the main entry point for instruction file generation.

    Args:
        content: Trading strategy description
        strategy_name: Name for the strategy
        source_type: "text", "youtube", or "pdf"
        source_url: Optional URL of source
        output_dir: Where to save instruction file
        progress_callback: Optional callback for progress updates

    Returns:
        Dictionary with generation results

    Example:
        >>> result = generate_instruction_file(
        ...     content="Buy when RSI < 30, sell when RSI > 70",
        ...     strategy_name="rsi_strategy",
        ...     source_type="text"
        ... )
        >>> if result['success']:
        ...     print(f"Saved to: {result['file_path']}")
    """

    generator = InstructionFileGenerator(output_dir)
    return generator.generate_instruction_file(
        content=content,
        strategy_name=strategy_name,
        source_type=source_type,
        source_url=source_url,
        progress_callback=progress_callback
    )


def validate_instruction_file(file_path: str) -> Dict:
    """
    Validate an instruction file for template compliance.

    Args:
        file_path: Path to instruction file

    Returns:
        Validation results dictionary
    """

    generator = InstructionFileGenerator()
    return generator.validate_instruction_file(file_path)


# Backward compatibility - deprecated functions

def generate_lumibot_strategy(*args, **kwargs):
    """
    DEPRECATED: Use generate_instruction_file instead.

    The two-stage workflow is:
    1. generate_instruction_file (this module)
    2. /lumibot-generate command (with instruction file)
    """
    import warnings
    warnings.warn(
        "generate_lumibot_strategy is deprecated. "
        "Use generate_instruction_file + /lumibot-generate command instead.",
        DeprecationWarning
    )

    # Convert to new API
    return generate_instruction_file(*args, **kwargs)


def validate_strategy_code(*args, **kwargs):
    """DEPRECATED: Validation now happens in /lumibot-generate workflow."""
    import warnings
    warnings.warn(
        "validate_strategy_code is deprecated. "
        "Validation now happens automatically in /lumibot-generate workflow.",
        DeprecationWarning
    )
    return {"is_valid": True, "message": "Use /lumibot-generate for validation"}


# For testing
if __name__ == "__main__":
    print("=" * 60)
    print("Instruction File Generator for Lumibot")
    print("=" * 60)

    # Test instruction file generation
    test_content = """
    Buy SPY when RSI(14) crosses below 30 (oversold).
    Sell SPY when RSI(14) crosses above 70 (overbought).
    Use daily timeframe.
    Position size: 95% of available cash.
    Take profit at 10% gain, stop loss at 5% loss.
    """

    print("\nGenerating test instruction file...")

    def progress_update(step, total, message, progress):
        print(f"  [{progress:.0f}%] {message}")

    result = generate_instruction_file(
        content=test_content,
        strategy_name="rsi_test_strategy",
        source_type="text",
        progress_callback=progress_update
    )

    if result['success']:
        print("\n[SUCCESS] Instruction file generated successfully!")
        print(f"\nFile saved to: {result['file_path']}")
        print(f"\nPreview:\n{result['preview']}")
        print("\n[NEXT STEP] Use with /lumibot-generate command")
    else:
        print(f"\n[FAILED] Generation failed: {result.get('error')}")
