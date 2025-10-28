# Strategy Instruction Template Guide

## Your Workflow

```
[Video/PDF/Source]
    ↓
[Streamlit App - Parse & Structure]
    ↓
[Outputs/Instructions/*.txt - Structured Instructions]
    ↓
[/lumibot-generate or AI Coder]
    ↓
[Complete Lumibot Strategy + Tests + Validation]
```

---

## Template Structure

Based on `0dte_iwm.txt` format and Zero Loss Butterfly lessons learned.

### Required Sections

1. **Strategy Name**
2. **Asset Class**
3. **Entry Conditions** (specific, numbered)
4. **Exit Conditions** (specific, numbered)
5. **Position Sizing**
6. **Risk Management** (stop loss, take profit, max position)
7. **Timeframe**
8. **Technical Indicators** (or "None" if structure-based)
9. **Implementation Requirements** (CRITICAL SECTION)
10. **Testing Requirements** (validation criteria)
11. **Expected Deliverables** (files to create)
12. **Risk Assessment**
13. **Expected Outcome** (optional but helpful)

---

## Critical Elements to Include

### From Zero Loss Butterfly Experience

#### 1. Position-Based Checking
```
**CRITICAL: Stock Purchase Logic**
- Use position-based checking: `len(self.get_positions()) == 0`
- NOT flag-based tracking (unreliable with canceled orders)
- [Asset] should appear EXACTLY [N] times in trades CSV
```

#### 2. Strike Selection Logic
```
**Strike Selection Requirements**
- Round target strikes to nearest $[X]: `round(price / X) * X`
- Query option chain with `self.get_chains()`
- Find nearest available strikes from chain
```

#### 3. Multi-Leg Execution
```
**Order Execution**
- Submit all [N] legs as separate orders
- Use market orders for backtesting reliability
- Check fill status on next iteration
- If orders canceled, determine re-entry logic
```

#### 4. Quantity Specifications
```
**CRITICAL**: When selling/buying multiple contracts, specify:
- Buy [N]x CALL/PUT at strike $[X] **CRITICAL: [N] contracts**
```

#### 5. Testing Strategy
```
**Testing Requirements**
1. Confirmed Trade Test (Video/Source Match)
   - Date: [specific dates from source]
   - Symbol: [specific symbol]
   - Expected behavior: [specific outcomes]

2. Historical Data Test (Reliability)
   - Date: [1 year prior for complete data]
   - Symbols: [test multiple if applicable]
   - Purpose: Complete data availability

3. Validation Requirements
   - Create validator to check [specific items]
   - Count [specific events]
   - Verify [specific structure]
```

#### 6. Configuration
```
**Configuration**
- Use parameterized backtesting dates (NOT environment variables)
- Create credentials.py for API keys (no dates)
- Each test script defines its own date range
```

---

## Template Sections Explained

### Entry Conditions
- **Be specific with quantities**: "Sell 2 CALLs" not "Sell CALLs"
- **Include strike calculations**: "Strike = current_price - $10"
- **Specify timing**: "Early in trading day" or "At market open"
- **Include validation**: "Enter ONLY if [condition] is met"

### Position Structure Verification
NEW SECTION (add this for complex strategies):
```
Position Structure Verification:
- Check actual positions held (not just order flags)
- [Asset] should be [quantity] (not more, not less)
- If [condition], then [re-entry logic]
- Maintain [ratio] at all times
```

### Exit Conditions
- **Roll logic**: When, how, what to keep vs replace
- **Failure handling**: What if roll fails? How many retries?
- **End conditions**: When to exit entirely

### Implementation Requirements
**THIS IS THE KEY SECTION** - Add specific gotchas:
- Position tracking method
- Strike rounding logic
- Order execution sequence
- Fill status checking
- Re-entry scenarios

### Testing Requirements
**ALSO CRITICAL** - Define success criteria:
- Specific test cases (confirmed trade, historical)
- What to validate (counts, ratios, structure)
- Performance comparison baseline
- Expected vs actual verification

### Expected Outcome
**NEW - Very helpful**:
- Include expected results from testing if known
- "NOT profitable" or "Target X% return"
- Comparison to alternatives
- Clear recommendation

---

## Example: Minimal Template

```
Strategy Name: [Name]

Entry Conditions:
1. Buy/Sell [quantity] [asset] at [strike/price]
2. [Additional leg] **CRITICAL: [important detail]**
3. Enter when [condition]

Position Structure Verification:
- Check positions: [specific checks]
- [Asset] purchased [how many times]: [N]
- If [scenario], then [action]

Exit Conditions:
1. [Primary exit condition]
2. [Roll logic if applicable]
3. [Failure handling]

Implementation Requirements:
**CRITICAL: [Most important gotcha]**
- [Specific implementation detail]
- [Position tracking method]
- [Strike rounding if options]

Testing Requirements:
1. Confirmed Trade: [dates], [symbol], expect [outcome]
2. Historical Test: [dates], [symbols]
3. Validator checks: [specific items]

Expected Outcome:
[Expected results or recommendation]
```

---

## Example: Complete Template

See: `TEMPLATE_zero_loss_butterfly.txt` for full example with all sections.

---

## Checklist for Your Instruction Files

Before feeding to AI coder, verify:

- [ ] Quantities specified (not vague)
- [ ] Strike calculations shown
- [ ] Critical details marked with `**CRITICAL:**`
- [ ] Position checking method specified
- [ ] Roll logic clear (if applicable)
- [ ] Testing requirements with specific dates
- [ ] Validation criteria defined
- [ ] Configuration approach specified (parameterized dates)
- [ ] Expected outcome or recommendation included
- [ ] All "gotchas" from similar strategies documented

---

## Common Gotchas to Include

### For Options Strategies
1. Strike rounding (to $5 or $1)
2. Multi-contract specifications (2x CALL not just CALL)
3. Position-based vs flag-based tracking
4. Options-only re-entry if stock owned
5. Data availability for backtesting

### For Intraday Strategies
1. Exact entry timing
2. Exit timing or price targets
3. Zero DTE handling
4. Check frequency requirements

### For Rolling Strategies
1. When to roll (days before expiration)
2. What to keep (stock) vs replace (options)
3. Roll failure handling
4. Recalculation of strikes

---

## Integration with /lumibot-generate

When you have an instruction file, use it with:

```
/lumibot-generate

[Paste or reference instruction file from Outputs/Instructions/]

Additional context:
- Source: [YouTube video / PDF / article]
- Confirmed trade: [dates if known]
- Priority: [what to implement first]
```

The instruction file provides the structure, the command handles the implementation.

---

## Benefits of This Approach

1. **Reproducible**: Same instruction → same implementation
2. **Documented**: Captures all requirements upfront
3. **Validated**: Forces you to think through edge cases
4. **Efficient**: AI has everything it needs in one file
5. **Reusable**: Template for similar strategies

---

## Evolution of This Template

This template incorporates lessons from:
- 0DTE IWM strategy (your existing format)
- Zero Loss Butterfly (our debugging experience)
- Common Lumibot patterns (StrategyTemplate.py)

Key additions from Zero Loss Butterfly:
1. "Position Structure Verification" section
2. "Implementation Requirements" with gotchas
3. "Testing Requirements" with specific validation
4. "Expected Outcome" with recommendation
5. Emphasis on position-based checking
6. Strike rounding requirements
7. Configuration approach (parameterized dates)

---

## Next Steps

1. Use this template for future strategies
2. Update your Streamlit app to include new sections
3. Build library of instruction files
4. Reference previous similar strategies' gotchas
5. Continuously refine based on lessons learned

---

Generated: October 28, 2025
Based on: Zero Loss Butterfly implementation experience
