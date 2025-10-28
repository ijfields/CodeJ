# SPY vs VISA Comparison - Zero Loss Butterfly Strategy

**Test Period**: August 21 - October 17, 2024 (57 days)
**Complete Historical Data**: Using 2024 data for reliable options pricing
**Date**: October 28, 2025

---

## Executive Summary

**CRITICAL FINDING**: The Zero Loss Butterfly strategy **SIGNIFICANTLY UNDERPERFORMS** both SPY and VISA buy-and-hold during this test period. While it successfully reduces volatility and drawdown, the returns are far too low to justify the strategy.

**Recommendation**: **DO NOT USE THIS STRATEGY** - Both SPY and VISA buy-and-hold delivered better risk-adjusted returns.

---

## Performance Comparison Table

| Metric | SPY Buy & Hold | SPY Strategy | VISA Buy & Hold | VISA Strategy |
|--------|----------------|--------------|-----------------|---------------|
| **Total Return** | **+4%** | +1% | **+7%** | +1% |
| **CAGR (Annual)** | **30.68%** | 5.98% | **57.41%** | 7.49% |
| **Sharpe Ratio** | **1.86** | 0.44 | **2.05** | 0.45 |
| **Max Drawdown** | -4.14% | **-0.89%** | -7.52% | **-1.43%** |
| **Volatility (Annual)** | 12.16% | **3.04%** | 20.67% | **6.38%** |
| **Correlation to Underlying** | 100% | **2.4%** | 100% | **21.84%** |
| **Beta** | 1.0 | **0.01** | 1.0 | **0.07** |
| **Win Days %** | **58.97%** | 47.92% | **58.97%** | 56.25% |

---

## Key Findings

### 1. Returns: STRATEGY LOSES BADLY

**SPY Comparison:**
- Buy & Hold: +4% total, 30.68% annualized
- Strategy: +1% total, 5.98% annualized
- **Underperformance: 75% lower returns**

**VISA Comparison:**
- Buy & Hold: +7% total, 57.41% annualized
- Strategy: +1% total, 7.49% annualized
- **Underperformance: 87% lower returns**

**Verdict**: The strategy captures only 13-25% of the underlying's gains.

### 2. Risk Reduction: WORKS BUT NOT WORTH IT

**Volatility Reduction:**
- SPY: 12.16% → 3.04% (75% reduction) ✓
- VISA: 20.67% → 6.38% (69% reduction) ✓

**Drawdown Reduction:**
- SPY: -4.14% → -0.89% (78% reduction) ✓
- VISA: -7.52% → -1.43% (81% reduction) ✓

**Correlation:**
- SPY: 2.4% (almost no correlation) ✓
- VISA: 21.84% (low correlation) ✓

**Verdict**: Risk reduction works, but at too high a cost (75-87% lower returns).

### 3. Risk-Adjusted Returns: POOR

**Sharpe Ratios:**
- SPY Buy & Hold: 1.86 (excellent)
- SPY Strategy: 0.44 (poor)
- VISA Buy & Hold: 2.05 (excellent)
- VISA Strategy: 0.45 (poor)

**Verdict**: Even after adjusting for risk, buy-and-hold wins decisively.

### 4. Consistency: STRATEGY LOSES MORE OFTEN

**Win Rate:**
- SPY Buy & Hold: 58.97% winning days
- SPY Strategy: 47.92% winning days (worse than coin flip)
- VISA Buy & Hold: 58.97% winning days
- VISA Strategy: 56.25% winning days

**Verdict**: Strategy has lower probability of profit on any given day.

---

## Why SPY vs VISA Makes Little Difference

Both tests show the same pattern:
1. **Strategy returns ~1%** regardless of underlying
2. **Buy-and-hold beats strategy** by wide margins
3. **Risk reduction works** but doesn't compensate for lost returns

**Key Insight**: The strategy structure itself is the problem, not the choice of underlying asset.

---

## Detailed Metrics

### SPY Test Results

**Performance:**
- Total Return: SPY +4% vs Strategy +1%
- CAGR: SPY 30.68% vs Strategy 5.98%
- Monthly Expected: SPY +1.38% vs Strategy +0.3%

**Risk:**
- Max Drawdown: SPY -4.14% vs Strategy -0.89%
- Volatility: SPY 12.16% vs Strategy 3.04%
- Beta: 0.01 (minimal market exposure)

**Quality:**
- Sharpe: SPY 1.86 vs Strategy 0.44
- Sortino: SPY 2.71 vs Strategy 0.67
- Calmar: SPY 7.42 vs Strategy 6.74

### VISA Test Results

**Performance:**
- Total Return: V +7% vs Strategy +1%
- CAGR: V 57.41% vs Strategy 7.49%
- Monthly Expected: V +2.35% vs Strategy +0.37%

**Risk:**
- Max Drawdown: V -7.52% vs Strategy -1.43%
- Volatility: V 20.67% vs Strategy 6.38%
- Beta: 0.07 (very low market exposure)

**Quality:**
- Sharpe: V 2.05 vs Strategy 0.45
- Sortino: V 2.72 vs Strategy 0.67
- Calmar: V 7.63 vs Strategy 5.25

---

## Data Quality Comparison

### SPY (2024 Data)
- **Stock purchases**: 1 (Aug 21) ✓
- **Options fill rate**: HIGH (used 2024 complete data)
- **Roll success**: YES (Oct 11 roll to Dec 6 expiration succeeded)
- **Data issues**: None - SPY has excellent options data

### VISA (2024 Data)
- **Stock purchases**: 1 (Aug 21) ✓
- **Options fill rate**: HIGH (used 2024 complete data)
- **Roll success**: YES (Oct 11 roll to Dec 6 expiration succeeded)
- **Data issues**: None - 2024 historical data is complete

**Conclusion**: Using 2024 data solved all data availability issues. Both tests ran cleanly with successful rolls.

---

## Why This Strategy Fails

### 1. Premium Erosion
The strategy sells 2 calls to generate income, but:
- Premium collected insufficient to compensate for lost upside
- Protective put costs eat into profits
- Long call provides minimal benefit during the test period

### 2. Capped Upside
The short calls at center strike mean:
- Strategy can't participate fully in stock gains
- SPY went from ~$560 to ~$580 (3.6% gain)
- VISA went from ~$268 to ~$287 (7% gain)
- Strategy captured only fraction of these moves

### 3. Time Decay Works Against Us
- Long puts and long calls both decay
- Short calls provide premium but create ceiling
- Net theta not as positive as expected

### 4. Capital Inefficiency
- Ties up ~$56,000 (SPY) or ~$27,000 (VISA)
- Returns only 1% over 57 days
- Annualized returns (6-7%) far below risk-free rate (4.51%)

### 5. Transaction Costs Not Included
Real-world costs would make it worse:
- 6 legs x $0.65/contract = $3.90 per entry
- 6 legs for roll = $3.90
- Bid-ask spreads on 4 option contracts
- Slippage on all orders
- **Estimated real cost**: -$200 to -$400 per cycle

---

## Break-Even Analysis

### What Would Be Needed for Strategy to Match Buy-and-Hold?

**For SPY:**
- Need 4% return vs current 1%
- Would need 4x more premium from short calls
- OR need stock to stay perfectly flat (maximize theta)
- **Conclusion**: Unrealistic in trending market

**For VISA:**
- Need 7% return vs current 1%
- Would need 7x more premium from short calls
- OR need stock to range-trade perfectly
- **Conclusion**: Impossible in strongly trending market

---

## Alternative Strategies (Better Choices)

### 1. Buy and Hold
- SPY: +4% (30.68% annualized)
- VISA: +7% (57.41% annualized)
- **Pros**: Simple, captures full upside, proven long-term winner
- **Cons**: Full volatility and drawdown exposure

### 2. Covered Call (Simple Version)
- Buy stock + sell 1 call (not 2)
- Collects premium while keeping some upside
- **Estimated**: 2-3% return with better risk profile
- **Pros**: Simpler, lower risk than Zero Loss Butterfly

### 3. Cash-Secured Put Selling
- Sell puts to collect premium
- If assigned, own stock at discount
- **Estimated**: 1-2% monthly premium in stable markets
- **Pros**: Simpler, no need for complex multi-leg structure

### 4. Collar (Stock + Put + Call)
- Buy stock, buy protective put, sell call (1:1:1 ratio)
- Similar protection with less complexity
- **Estimated**: Similar returns with fewer legs
- **Pros**: Simpler to manage, lower transaction costs

### 5. Simply Hold SPY/QQQQQ
- Long-term average: 10%+ annually
- This test period: +4% in 57 days is strong
- **Pros**: Proven 100-year track record, no effort

---

## Final Recommendations

### For Conservative Investors
**DO**: Buy SPY and hold it
- Captures market returns
- Low cost (0.03% expense ratio)
- Proven strategy

**DON'T**: Use Zero Loss Butterfly
- Returns too low (1% vs 4-7%)
- Complexity not worth the effort
- Transaction costs make it worse

### For Income-Seeking Investors
**DO**: Consider covered calls or cash-secured puts
- Simpler strategies with better returns
- Lower transaction costs
- Easier to manage

**DON'T**: Use complex multi-leg strategies like Zero Loss Butterfly
- 4-6 legs per position = high costs
- Requires constant monitoring
- Returns don't justify complexity

### For Volatility Reducers
**DO**: Consider 60/40 portfolio (stocks/bonds) or similar
- Achieves volatility reduction
- Maintains reasonable returns
- Simpler rebalancing

**DON'T**: Use Zero Loss Butterfly for volatility reduction
- Yes, it reduces volatility (75%)
- But returns drop even more (75-87%)
- Not worth the trade-off

---

## Test Validity and Data Quality

### Why 2024 Data is Better Than 2025

**2025 Data Issues (Previous Test):**
- Only 11 days old (as of Oct 28, 2025)
- Incomplete options data for new expirations
- Roll attempts failed (no data for Dec 2025)
- Can't validate strategy performance

**2024 Data Advantages:**
- Complete historical record
- All options data available
- Rolls work correctly
- Can fully evaluate strategy

### Test Reliability

**High Confidence:**
- Both SPY and VISA tests show same pattern
- Complete data for entire period
- Successful rolls demonstrate full functionality
- Results consistent across two different underlyings

**Limitations:**
- Only 57-day test period (one cycle)
- Bull market period (Aug-Oct 2024 was positive)
- Need longer test to evaluate multiple market conditions
- Transaction costs not included (would make results worse)

---

## Conclusion

### The Verdict: DO NOT USE THIS STRATEGY

**Why It Fails:**
1. **Returns too low**: 1% vs 4-7% buy-and-hold
2. **Sharpe ratio poor**: 0.44-0.45 vs 1.86-2.05
3. **Complexity not justified**: 4-6 legs, constant monitoring
4. **Capital inefficiency**: Large capital requirement for minimal return
5. **Transaction costs**: Not included but would make it worse

**What It Does Well:**
1. Reduces volatility (69-75%)
2. Reduces drawdown (78-81%)
3. Low correlation to underlying (2-22%)

**But None of That Matters When:**
- Returns are 75-87% lower than buy-and-hold
- Risk-adjusted returns are worse
- Complexity is high
- Transaction costs eat into already meager profits

### Alternative Actions

**Instead of Zero Loss Butterfly:**
1. Buy and hold SPY (simple, proven, better returns)
2. Use covered calls if you want income (simpler, better)
3. Use 60/40 portfolio if you want lower volatility (simpler, proven)
4. Consider dividend stocks if you want income (simpler, proven)

**If You Must Trade Options:**
1. Covered calls (sell 1 call per 100 shares)
2. Cash-secured puts (sell puts to get paid while waiting to buy)
3. Protective collars (simpler 3-leg version)
4. Wheel strategy (put selling + covered calls)

**All of the above are simpler, more proven, and likely more profitable than the Zero Loss Butterfly.**

---

## Files Generated

### Tearsheets (HTML/CSV)
- `ZeroLossButterfly_2025-10-28_14-20_ELQg9n_tearsheet.html` - SPY results
- `ZeroLossButterfly_2025-10-28_14-27_RCAqK6_tearsheet.html` - VISA results

### Trade Logs
- `ZeroLossButterfly_2025-10-28_14-20_ELQg9n_trades.csv` - SPY transactions
- `ZeroLossButterfly_2025-10-28_14-27_RCAqK6_trades.csv` - VISA transactions

### Documentation
- `COMPREHENSIVE_ANALYSIS_SUMMARY.md` - Full analysis of video trade (2025 data)
- `SPY_VS_VISA_COMPARISON.md` - This file
- `VIDEO_TRADE_DETAILS.md` - Original video trade details

---

**Generated**: October 28, 2025
**Test Period**: August 21 - October 17, 2024 (2024 historical data)
**Conclusion**: Strategy works as designed but is not profitable
**Recommendation**: Use buy-and-hold or simpler alternatives instead
