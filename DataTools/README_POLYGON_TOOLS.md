# Polygon.io Data Tools for Zero Loss Butterfly Strategy

This directory contains flexible tools for downloading and managing Polygon.io data for backtesting the Zero Loss Butterfly strategy.

## Files Overview

### Core Tools
- **`download_polygon_data_flexible.py`** - Flexible data downloader with command-line interface
- **`polygon_data_manager.py`** - High-level manager with Lumibot integration
- **`example_usage.py`** - Usage examples and demonstrations

### Original Tools
- **`download_polygon_data_for_backtest.py`** - Original hardcoded version (for reference)
- **`get_spy_underlying_data.py`** - SPY underlying price analysis
- **`get_spy_options_multi_days.py`** - SPY options analysis (has limitations)

## Quick Start

### 1. Download V Data for Zero Loss Butterfly

```bash
# Download V data for April-October 2024
python polygon_data_manager.py download V 2024-04-15 2024-10-17

# Or use the flexible downloader
python download_polygon_data_flexible.py V --start-date 2024-04-15 --end-date 2024-10-17
```

### 2. Download Multiple Time Periods

```bash
# Download V for multiple periods
python polygon_data_manager.py multi V

# Download SPY data
python download_polygon_data_flexible.py SPY --start-date 2024-05-01 --end-date 2024-10-31
```

### 3. Use with Lumibot

```python
import pickle
from lumibot.backtesting import PandasDataBacktesting

# Load downloaded data
with open('data/polygon/v_lumibot_data.pkl', 'rb') as f:
    data_dict = pickle.load(f)

# Run backtest
strategy.backtest(
    PandasDataBacktesting,
    datetime(2024, 4, 15),
    datetime(2024, 10, 17),
    pandas_data=data_dict
)
```

## Detailed Usage

### Flexible Downloader (`download_polygon_data_flexible.py`)

**Command Line Interface:**

```bash
# Basic usage
python download_polygon_data_flexible.py SYMBOL --start-date YYYY-MM-DD --end-date YYYY-MM-DD

# Multiple symbols
python download_polygon_data_flexible.py SPY V QQQ --start-date 2024-01-01 --end-date 2024-12-31

# Different timeframes
python download_polygon_data_flexible.py SPY --start-date 2024-11-01 --end-date 2024-11-30 --timeframe minute
python download_polygon_data_flexible.py SPY --start-date 2024-01-01 --end-date 2024-12-31 --timeframe hour --multiplier 4

# Custom output directory
python download_polygon_data_flexible.py V --start-date 2024-04-15 --end-date 2024-10-17 --output-dir data/my_strategy
```

**Programmatic Usage:**

```python
from download_polygon_data_flexible import PolygonDataDownloader

downloader = PolygonDataDownloader()

# Download data
success = downloader.download_data(
    symbols=['V', 'SPY'],
    start_date='2024-04-15',
    end_date='2024-10-17',
    timeframe='day',
    multiplier=1,
    description='butterfly_strategy'
)
```

### Data Manager (`polygon_data_manager.py`)

**Command Line Interface:**

```bash
# Download single period
python polygon_data_manager.py download V 2024-04-15 2024-10-17

# Download multiple periods
python polygon_data_manager.py multi V

# Convert existing data
python polygon_data_manager.py convert data/polygon/v_butterfly_20240415_20241017
```

**Programmatic Usage:**

```python
from polygon_data_manager import PolygonDataManager

manager = PolygonDataManager()

# Download data
output_dir = manager.download_butterfly_data('V', '2024-04-15', '2024-10-17')

# Convert to Lumibot format
data_dict = manager.create_lumibot_data_dict(output_dir)

# Save for later use
manager.save_lumibot_data(data_dict, 'data/polygon/v_lumibot_data.pkl')
```

## Configuration

### Required: `credentials.py`

Make sure you have a `credentials.py` file with your Polygon API key:

```python
POLYGON_CONFIG = {
    "API_KEY": "your_polygon_api_key_here"
}
```

### Environment Variables (Alternative)

Create a `.env` file:

```bash
POLYGON_API_KEY=your_polygon_api_key_here
```

## Data Structure

### Downloaded Files

The tools create CSV files with this structure:

```csv
timestamp,open,high,low,close,volume
2024-04-15 09:30:00,336.50,338.20,335.80,337.10,5000000
2024-04-16 09:30:00,337.10,339.50,336.80,338.90,4800000
...
```

### Lumibot Data Dictionary

The data manager creates a dictionary suitable for `PandasDataBacktesting`:

```python
{
    'V': DataFrame,  # V stock data
    'SPY': DataFrame,  # SPY stock data
    # ... other symbols
}
```

## Troubleshooting

### Common Issues

1. **"POLYGON_API_KEY not found"**
   - Check `credentials.py` has `POLYGON_CONFIG` with `API_KEY`
   - Or create `.env` file with `POLYGON_API_KEY`

2. **"No data found"**
   - Check date range (avoid future dates)
   - Verify symbol is correct
   - Check API subscription tier

3. **Rate limiting errors**
   - Free tier: 5 calls/minute
   - Paid tiers: Unlimited calls
   - Add delays between requests

4. **Options data issues**
   - Polygon may not have historical options data
   - Use Barchart Premier as alternative
   - See `SUMMARY_AND_SOLUTION.md` for details

### Debug Mode

Add debug prints to see what's happening:

```python
# In download_polygon_data_flexible.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Zero Loss Butterfly

### Step 1: Download Data

```bash
# Download V data for your strategy period
python polygon_data_manager.py download V 2024-04-15 2024-10-17
```

### Step 2: Use in Strategy

```python
# In your Zero Loss Butterfly strategy
import pickle
from lumibot.backtesting import PandasDataBacktesting

# Load data
with open('data/polygon/v_lumibot_data.pkl', 'rb') as f:
    data_dict = pickle.load(f)

# Run backtest
ZeroLossButterfly.backtest(
    PandasDataBacktesting,
    datetime(2024, 4, 15),
    datetime(2024, 10, 17),
    pandas_data=data_dict,
    parameters={
        "symbol": "V",
        "target_dte": 57,
        "strike_spacing": 10,
        # ... other parameters
    }
)
```

### Step 3: Handle Options Data

Since Polygon may not have options data:

1. **Use Barchart Premier** (recommended)
2. **Upgrade Polygon subscription** to Options Developer tier
3. **Use ThetaData** as alternative

See `SUMMARY_AND_SOLUTION.md` for detailed options data solutions.

## File Organization

```
DataTools/
├── download_polygon_data_flexible.py    # Flexible downloader
├── polygon_data_manager.py              # High-level manager
├── example_usage.py                     # Usage examples
├── README_POLYGON_TOOLS.md              # This file
└── ...

data/polygon/
├── v_butterfly_20240415_20241017/       # Downloaded V data
│   └── V_1d_20240415_20241017.csv
├── spy_butterfly_20240501_20241031/     # Downloaded SPY data
│   └── SPY_1d_20240501_20241031.csv
├── v_lumibot_data.pkl                   # Lumibot-ready data
└── combined_lumibot_data.pkl            # Multiple symbols
```

## Next Steps

1. **Download your data** using these tools
2. **Test with stock data** first (this will work)
3. **Handle options data** using Barchart Premier or upgraded Polygon
4. **Run your Zero Loss Butterfly backtest**
5. **Compare results** with your previous tests

The tools are designed to work seamlessly with your existing Lumibot strategy code!

