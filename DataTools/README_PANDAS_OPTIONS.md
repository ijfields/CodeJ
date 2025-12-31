# Pandas Options Data Source for Lumibot

## Overview

This custom data source enables options backtesting in Lumibot using pre-converted pandas DataFrames. It solves the limitation where `PandasDataBacktesting.get_chains()` always returns `None`, preventing options strategies from working with local data.

## Why This Was Needed

Lumibot's built-in `PandasDataBacktesting` class has a critical limitation:

```python
# From Lumibot's pandas_backtesting.py
def get_chains(self, asset):
    return None  # ← Always returns None for options!
```

This means that even though you have perfectly formatted options data in `data/lumibot/`, you cannot use it for backtesting because there's no data source class to feed it to the backtesting engine.

## Solution

The `PandasOptionsDataSource` class:

1. **Extends Lumibot's DataSource base class**
2. **Implements `get_chains()`** to retrieve options chains from pandas DataFrames
3. **Implements `get_historical_prices()`** for stock price history
4. **Maps DataFrame data** to Lumibot's expected chain structure

## Quick Start

### 1. Basic Usage

```python
from DataTools.pandas_options_data_source import PandasOptionsDataSource
from lumibot.entities import Asset

# Initialize data source
data_source = PandasOptionsDataSource()

# Get options chains
spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
chains = data_source.get_chains(spy_asset)

# Get historical prices
historical = data_source.get_historical_prices(spy_asset, length=30, timestep="1D")
```

### 2. With Zero Loss Butterfly Strategy

```python
from lumibot.backtesting import BacktestingBroker
from lumibot.strategies import Strategy

class CustomBacktestingBroker(BacktestingBroker):
    def __init__(self, data_source, **kwargs):
        super().__init__(**kwargs)
        self.data_source = data_source
    
    def get_chains(self, asset):
        return self.data_source.get_chains(asset)
    
    def get_historical_prices(self, asset, length, timestep="1D"):
        return self.data_source.get_historical_prices(asset, length, timestep)
    
    def get_last_price(self, asset):
        return self.data_source.get_last_price(asset)

# Use with your strategy
broker = CustomBacktestingBroker(data_source)
strategy = YourZeroLossButterflyStrategy(broker=broker)
```

## Data Format Requirements

### Input Data Structure

The data source expects pickled files in `data/lumibot/`:

- **`stock_data.pkl`**: MultiIndex DataFrame with `(symbol, datetime)` index
- **`options_data.pkl`**: Dictionary `{symbol: DataFrame}` with options contracts
- **`metadata.json`**: Metadata about the data (optional)

### Stock Data Format

```python
# MultiIndex: (symbol, datetime)
# Columns: open, high, low, close, volume
stock_data.index = [('SPY', '2024-03-28'), ('SPY', '2024-03-29'), ...]
stock_data.columns = ['open', 'high', 'low', 'close', 'volume']
```

### Options Data Format

```python
# Dictionary by symbol
options_data = {
    'SPY': DataFrame with columns:
        - strike: float
        - expiration: datetime
        - option_type: 'Call' or 'Put'
        - last_price: float
        - bid: float
        - ask: float
        - volume: int
        - open_interest: int
        - days_to_expiry: int
}
```

### Output Chain Format

The `get_chains()` method returns data in Lumibot's expected format:

```python
{
    expiration_date: {
        strike: {
            'CALL': contract_data,
            'PUT': contract_data
        }
    }
}
```

## API Reference

### Core Methods

#### `get_chains(asset, quote=None)`

Returns options chain for the specified asset.

**Parameters:**
- `asset`: Asset object with symbol
- `quote`: Optional quote object (not used)

**Returns:**
- Dictionary with options chain data, or `None` if not found

#### `get_historical_prices(asset, length, timestep="1D")`

Returns historical price data for the specified asset.

**Parameters:**
- `asset`: Asset object with symbol
- `length`: Number of periods to retrieve
- `timestep`: Time step ("1D", "1H", "5M", etc.)

**Returns:**
- DataFrame with OHLCV data, or `None` if not found

#### `get_last_price(asset)`

Returns the most recent price for the specified asset.

**Parameters:**
- `asset`: Asset object with symbol

**Returns:**
- Last price as float, or `None` if not found

### Utility Methods

#### `get_available_expirations(symbol)`

Get available expiration dates for a symbol.

#### `get_available_strikes(symbol, expiration)`

Get available strikes for a symbol and expiration.

#### `validate_data_integrity()`

Validate that the loaded data is properly formatted.

## Testing

Run the integration test to verify everything works:

```bash
cd DataTools
python test_pandas_options_backtest.py
```

This will:
1. Test data loading and validation
2. Test chains retrieval
3. Test historical prices
4. Test options contract creation
5. Test order creation (without submission)

## Limitations (Minimal Implementation)

This is a minimal working implementation with the following limitations:

- **Single-date snapshot only**: No historical options prices over time
- **Basic chain filtering**: Only by expiration dates
- **No Greeks calculation**: No delta, gamma, theta, vega
- **No bid-ask spread modeling**: Uses last_price for simplicity
- **No volatility data**: No implied volatility calculations

## Suitable For

✅ **Strategy logic testing**: Verify that your options strategies can retrieve chains and create orders

✅ **Proof of concept**: Demonstrate that options backtesting is possible with local data

✅ **Development**: Test and debug options strategies before moving to production

## Not Suitable For

❌ **Production backtesting**: Missing advanced features like Greeks and historical options prices

❌ **Risk analysis**: No volatility modeling or advanced risk metrics

❌ **Performance optimization**: Limited to basic functionality

## Next Steps

To make this production-ready, consider adding:

1. **Historical options prices**: Store options data over time, not just snapshots
2. **Greeks calculation**: Implement delta, gamma, theta, vega calculations
3. **Volatility modeling**: Add implied volatility data and calculations
4. **Bid-ask spread modeling**: Use bid/ask prices instead of last_price
5. **Performance optimization**: Cache frequently accessed data
6. **Error handling**: More robust error handling and validation

## Troubleshooting

### Common Issues

**"No options data loaded"**
- Check that `data/lumibot/options_data.pkl` exists
- Verify the file is not corrupted
- Check file permissions

**"No stock data for symbol"**
- Verify the symbol exists in `stock_data.pkl`
- Check the MultiIndex format is correct
- Ensure symbol case matches exactly

**"Empty options data"**
- Check that the options DataFrame is not empty
- Verify the data conversion process worked correctly
- Check the date range in metadata.json

### Debug Mode

Enable debug output by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about data loading and method calls.

## Files

- `pandas_options_data_source.py` - Core data source class
- `test_pandas_options_backtest.py` - Integration test suite
- `README_PANDAS_OPTIONS.md` - This documentation

## Dependencies

- `pandas` - Data manipulation
- `lumibot` - Trading framework
- `pickle` - Data serialization
- `pathlib` - File path handling
