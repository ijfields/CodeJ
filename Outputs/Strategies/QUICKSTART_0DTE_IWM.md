# Quick Start Guide - 0DTE IWM Strategy

## Get Running in 5 Minutes

### Prerequisites

1. **Python Environment**
   - Lumibot installed: `pip install lumibot`
   - Required packages: pandas, pandas_ta

2. **API Credentials**
   - Polygon.io API key (PAID subscription for options data)
   - `.env` file configured

3. **Credentials Setup**
   - `credentials.py` exists in project root
   - `IS_BACKTESTING = True` set
   - `POLYGON_API_KEY` configured

### Step 1: Verify Credentials

```bash
cd "C:\Data\Cousin Ingrid\Git Hub\CodeJ"
python credentials.py
```

Expected output:
```
✅ All required credentials present
```

### Step 2: Run Backtest

```bash
python "Outputs/Strategies/0dte_iwm_premium_collection.py"
```

### Step 3: Review Results

Open the generated file:
```
0dte_iwm_tearsheet.html
```

## Expected Output

### Console Output

```
================================================================================
0DTE IWM PREMIUM COLLECTION STRATEGY - BACKTEST
================================================================================

Strategy Parameters:
  - Underlying: IWM
  - Position: 10 puts, 5 high calls, 5 mid calls
  - Put exit: $0.02 premium
  - High call exit: $0.15 premium
  - Mid call exit: $0.07 premium

Backtest period: 2024-01-02 to 2024-12-31
================================================================================

[Backtest runs...]

================================================================================
BACKTEST COMPLETE
Check the generated tearsheet: 0dte_iwm_tearsheet.html
================================================================================
```

### Tearsheet Metrics

Look for:
- **Total Return**: Strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable days
- **Average Trade**: Average profit per trade

## Customization

### Adjust Position Size

Edit in file before running:
```python
parameters={
    "num_puts": 20,              # Double position size
    "num_calls_high": 10,
    "num_calls_mid": 10,
}
```

### Change Exit Targets

```python
parameters={
    "exit_put_premium": 0.01,    # More aggressive (close earlier)
    "exit_call_high_premium": 0.10,
    "exit_call_mid_premium": 0.05,
}
```

### Use Different Strikes

```python
parameters={
    "put_strike_offset": 10,      # Farther OTM (less risk, less premium)
    "call_strike_high": 195,      # Higher strike
    "call_strike_mid": 192,
}
```

### Change Backtest Period

```python
backtesting_start = datetime(2024, 6, 1)   # Start in June
backtesting_end = datetime(2024, 12, 31)   # End in December
```

## Troubleshooting

### Error: "No Polygon API key"
**Fix**: Add `POLYGON_API_KEY=your_key_here` to `.env` file

### Error: "Options data requires paid subscription"
**Fix**: Upgrade Polygon.io plan to include options data

### Error: "No 0DTE options available"
**Cause**: Backtest date may not have 0DTE options trading
**Fix**: Try different date range or check IWM options calendar

### Error: "Import error: credentials"
**Fix**: Ensure `credentials.py` exists in project root

## Understanding the Logs

### Successful Entry
```
================================================================================
INITIALIZING 0DTE IWM PREMIUM COLLECTION STRATEGY
================================================================================
...
--------------------------------------------------------------------------------
ENTERING POSITIONS
--------------------------------------------------------------------------------
Selected PUT strike: $183.00 (current: $188.00)
SELLING 10 PUT contracts at $183.00 @ $0.45 premium
✓ Put order submitted successfully
...
✓ ALL POSITIONS ENTERED SUCCESSFULLY
Total premium collected: $1,350.00
--------------------------------------------------------------------------------
```

### Position Monitoring
```
PUT position - Entry: $0.45, Current: $0.12, Target: $0.02
HIGH CALL position - Entry: $0.68, Current: $0.22, Target: $0.15
MID CALL position - Entry: $0.52, Current: $0.15, Target: $0.07
```

### Successful Exit
```
--------------------------------------------------------------------------------
CLOSING MID CALLS POSITION
Premium decayed to target: $0.07
✓ MID CALLS position closed
Estimated profit: $225.00
--------------------------------------------------------------------------------
```

## Key Strategy Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `num_puts` | 10 | Number of put contracts to sell |
| `num_calls_high` | 5 | Number of high strike calls |
| `num_calls_mid` | 5 | Number of mid strike calls |
| `put_strike_offset` | 5 | Dollars below current for put strike |
| `call_strike_high` | 191 | Fixed high call strike |
| `call_strike_mid` | 190 | Fixed mid call strike |
| `exit_put_premium` | 0.02 | Target premium to close puts |
| `exit_call_high_premium` | 0.15 | Target premium to close high calls |
| `exit_call_mid_premium` | 0.07 | Target premium to close mid calls |
| `entry_time_minutes` | 30 | Entry window after market open |
| `check_frequency_minutes` | 5 | How often to check positions |

## Performance Tips

1. **Start with smaller positions** (5 puts, 2-3 calls each)
2. **Test different date ranges** to see consistency
3. **Compare against IWM benchmark** (buy-and-hold)
4. **Monitor max drawdown** - should be acceptable risk
5. **Check win rate** - should be high (>60%) for premium collection

## Next Actions

- [ ] Run initial backtest with default parameters
- [ ] Review tearsheet performance metrics
- [ ] Experiment with different exit targets
- [ ] Test different position sizes
- [ ] Compare multiple time periods
- [ ] Optimize strike selection
- [ ] Add stop-loss if needed
- [ ] Paper trade before live

## Safety Reminders

1. **This is a high-risk strategy**
   - Selling options = unlimited risk potential
   - 0DTE = extreme time decay and volatility

2. **Never risk more than you can afford to lose**

3. **Backtest results ≠ future performance**

4. **Start with paper trading**

5. **Use proper position sizing** (1-2% of account per trade)

## Resources

- **Strategy File**: `Outputs/Strategies/0dte_iwm_premium_collection.py`
- **Full Documentation**: `README_0DTE_IWM.md`
- **Lumibot Docs**: https://lumibot.lumiwealth.com/
- **Polygon.io**: https://polygon.io/

---

Ready to trade? Run the backtest and review the results!

```bash
python "Outputs/Strategies/0dte_iwm_premium_collection.py"
```
