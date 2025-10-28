# Polygon.io Backtesting Data Guide

**Last Updated**: 2025-01-26  
**Purpose**: Comprehensive guide for using Polygon.io data in backtesting strategies

---

## Table of Contents

1. [Overview](#overview)
2. [Subscription Tiers](#subscription-tiers)
3. [Stocks Data](#stocks-data)
4. [Options Data](#options-data)
5. [API Endpoints](#api-endpoints)
6. [Lumibot Integration](#lumibot-integration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

Polygon.io provides institutional-grade market data for backtesting strategies. Based on the [pricing page](https://polygon.io/pricing?product=options), they offer different tiers for stocks and options data with varying historical depth and real-time capabilities.

### Key Features
- **Stocks**: 20+ years historical data (Advanced tier)
- **Options**: 5+ years historical data (Advanced tier)
- **Coverage**: 100% US market coverage
- **Formats**: JSON and CSV
- **Real-time**: Available on Advanced tiers

---

## Subscription Tiers

### Stocks Pricing

| Tier | Price | Historical Data | API Calls | Real-time | Best For |
|------|-------|----------------|-----------|-----------|----------|
| **Basic** | $0/month | 2 years | 5/minute | No | Testing/Development |
| **Starter** | $29/month | 5 years | Unlimited | 15-min delayed | Basic backtesting |
| **Developer** | $79/month | 10 years | Unlimited | 15-min delayed | Historical analysis |
| **Advanced** | $199/month | 20+ years | Unlimited | Real-time | Professional backtesting |

### Options Pricing

| Tier | Price | Historical Data | API Calls | Real-time | Best For |
|------|-------|----------------|-----------|-----------|----------|
| **Basic** | $0/month | 2 years | 5/minute | No | Testing/Development |
| **Starter** | $29/month | 2 years | Unlimited | 15-min delayed | Basic options backtesting |
| **Developer** | $79/month | 4 years | Unlimited | 15-min delayed | Options strategies |
| **Advanced** | $199/month | 5+ years | Unlimited | Real-time | Professional options trading |

### Recommendation for Your Use Case

For the **Zero Loss Butterfly** strategy, you need:
- **Options data** (4+ years historical)
- **Stocks data** (for underlying)
- **Minute-level aggregates**

**Recommended**: **Options Developer** ($79/month) + **Stocks Starter** ($29/month) = **$108/month total**

---

## Stocks Data

### Available Data Types

1. **Aggregates (OHLCV)**
   - Minute, hour, day bars
   - 20+ years historical (Advanced)
   - 10 years historical (Developer)

2. **Trades**
   - Individual trade records
   - Nanosecond timestamps
   - All US exchanges + dark pools

3. **Quotes**
   - Bid/ask data
   - Level 2 market depth
   - Real-time on Advanced tier

4. **Reference Data**
   - Company information
   - Corporate actions
   - Financials & ratios

### Key Endpoints

```python
# Historical aggregates
GET /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}

# Current snapshot
GET /v2/snapshot/locale/us/markets/stocks/tickers

# Trades
GET /v3/trades/{ticker}

# Quotes
GET /v3/quotes/{ticker}

# Reference data
GET /v3/reference/tickers
GET /v3/reference/tickers/{ticker}
```

### Example: Fetch SPY Data

```python
import requests
from datetime import datetime, timedelta

def fetch_spy_data(api_key, start_date, end_date):
    """Fetch SPY minute data for backtesting"""
    
    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/range/1/minute/{start_date}/{end_date}"
    
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "OK":
            return data["results"]
    
    return None

# Usage
api_key = "YOUR_API_KEY"
start_date = "2024-01-01"
end_date = "2024-12-31"

spy_data = fetch_spy_data(api_key, start_date, end_date)
```

---

## Options Data

### Available Data Types

1. **Options Chains**
   - All strikes and expirations
   - Greeks, IV, Open Interest
   - 5+ years historical (Advanced)

2. **Options Aggregates**
   - OHLCV for individual contracts
   - Minute-level data
   - Historical backtesting support

3. **Options Trades**
   - Individual option trades
   - Real-time on Advanced tier

### Key Endpoints

```python
# Options snapshot (current)
GET /v3/snapshot/options/{underlyingAsset}

# Options aggregates (historical)
GET /v2/aggs/ticker/{optionsTicker}/range/{multiplier}/{timespan}/{from}/{to}

# Options trades
GET /v3/trades/{optionsTicker}

# Options quotes
GET /v3/quotes/{optionsTicker}
```

### Option Ticker Format

Polygon uses specific formats for option tickers:

```python
# Format: O:{underlying}{expiry}{type}{strike}{right}
# Example: O:SPY250117C00640000

def create_option_ticker(underlying, expiry, option_type, strike):
    """Create Polygon option ticker format"""
    
    # Convert expiry to YYMMDD format
    expiry_str = expiry.strftime("%y%m%d")
    
    # Convert strike to 8-digit format (multiply by 1000)
    strike_str = f"{int(strike * 1000):08d}"
    
    # Create ticker
    ticker = f"O:{underlying}{expiry_str}{option_type}{strike_str}"
    
    return ticker

# Example
ticker = create_option_ticker("SPY", "2025-01-17", "C", 644)
# Result: O:SPY250117C00640000
```

### Example: Fetch Options Data

```python
def fetch_options_data(api_key, underlying, start_date, end_date):
    """Fetch options chain data for backtesting"""
    
    # Get current options snapshot
    url = f"https://api.polygon.io/v3/snapshot/options/{underlying}"
    
    params = {"apiKey": api_key}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "OK":
            return data["results"]
    
    return None

# Usage
options_data = fetch_options_data(api_key, "SPY", start_date, end_date)
```

---

## API Endpoints

### Core Endpoints

#### 1. Aggregates (OHLCV Data)
```python
# Historical bars
GET /v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}

# Parameters:
# - multiplier: 1, 5, 15, 30, 60, 240, 1D, 1W, 1M
# - timespan: minute, hour, day, week, month, quarter, year
# - from/to: YYYY-MM-DD format
```

#### 2. Snapshots (Current Market State)
```python
# Single ticker
GET /v2/snapshot/locale/us/markets/stocks/tickers/{ticker}

# All tickers
GET /v2/snapshot/locale/us/markets/stocks/tickers

# Options snapshot
GET /v3/snapshot/options/{underlyingAsset}
```

#### 3. Trades (Individual Transactions)
```python
# Historical trades
GET /v3/trades/{ticker}

# Parameters:
# - timestamp: Specific time
# - timestamp.gte: Greater than or equal
# - timestamp.lte: Less than or equal
# - limit: Max results (default 1000, max 50000)
```

#### 4. Quotes (Bid/Ask Data)
```python
# Historical quotes
GET /v3/quotes/{ticker}

# Same parameters as trades
```

### Advanced Endpoints

#### 1. Technical Indicators
```python
# SMA, EMA, RSI, MACD, etc.
GET /v1/indicators/sma/{ticker}
GET /v1/indicators/ema/{ticker}
GET /v1/indicators/rsi/{ticker}
```

#### 2. Reference Data
```python
# Company information
GET /v3/reference/tickers/{ticker}

# Corporate actions
GET /v3/reference/dividends/{ticker}

# Financials
GET /v3/reference/financials/{ticker}
```

---

## Lumibot Integration

### PolygonDataBacktesting

Lumibot supports Polygon.io through `PolygonDataBacktesting`:

```python
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.strategies import Strategy

class MyStrategy(Strategy):
    def initialize(self):
        # Your strategy logic
        pass

# Backtest with Polygon data
MyStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2024, 1, 1),
    datetime(2024, 12, 31),
    parameters={
        "polygon_api_key": "YOUR_API_KEY",
        "polygon_has_paid_subscription": True,  # Required for options
    }
)
```

### Configuration

```python
# lumibot_config.py
POLYGON_CONFIG = {
    "API_KEY": "your_api_key_here",
    "HAS_PAID_SUBSCRIPTION": True,  # Required for options data
    "MAX_WORKERS": 4,  # Parallel data fetching
}
```

### Common Issues

1. **Options Data Not Available**
   - Ensure `HAS_PAID_SUBSCRIPTION: True`
   - Check subscription tier includes options
   - Verify option ticker format

2. **Rate Limiting**
   - Basic tier: 5 calls/minute
   - Paid tiers: Unlimited calls
   - Use `MAX_WORKERS` to control parallel requests

3. **Historical Data Limits**
   - Basic: 2 years
   - Developer: 4-10 years
   - Advanced: 5-20+ years

---

## Troubleshooting

### Issue 1: "No options data found"

**Symptoms**:
- Options orders get canceled
- `trades.csv` shows "CANCELED" for options
- Stock orders work fine

**Solutions**:
1. Check subscription tier includes options
2. Verify `HAS_PAID_SUBSCRIPTION: True`
3. Test with direct API calls
4. Consider Barchart Premier as alternative

### Issue 2: Rate limiting errors

**Symptoms**:
- HTTP 429 errors
- "Too many requests" messages

**Solutions**:
1. Upgrade to paid tier
2. Reduce `MAX_WORKERS`
3. Add delays between requests
4. Use batch endpoints when possible

### Issue 3: Missing historical data

**Symptoms**:
- Empty results for old dates
- "No data found" errors

**Solutions**:
1. Check subscription tier limits
2. Verify date format (YYYY-MM-DD)
3. Try different time ranges
4. Use alternative data sources

### Issue 4: Option ticker format errors

**Symptoms**:
- Invalid ticker errors
- Options not found

**Solutions**:
1. Use correct format: `O:SPY250117C00640000`
2. Verify strike price format (multiply by 1000)
3. Check expiry date format (YYMMDD)
4. Test with known working tickers

---

## Best Practices

### 1. Data Management

```python
# Cache frequently used data
import pickle
from datetime import datetime

def cache_data(data, filename):
    """Cache data to avoid repeated API calls"""
    with open(f"cache/{filename}.pkl", "wb") as f:
        pickle.dump(data, f)

def load_cached_data(filename):
    """Load cached data if available"""
    try:
        with open(f"cache/{filename}.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
```

### 2. Error Handling

```python
import time
import requests

def fetch_with_retry(url, params, max_retries=3):
    """Fetch data with retry logic"""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                raise e
```

### 3. Data Validation

```python
def validate_data(data, expected_fields):
    """Validate API response data"""
    
    if not data:
        return False
    
    if data.get("status") != "OK":
        return False
    
    results = data.get("results", [])
    if not results:
        return False
    
    # Check first result has expected fields
    first_result = results[0]
    for field in expected_fields:
        if field not in first_result:
            return False
    
    return True

# Usage
spy_data = fetch_spy_data(api_key, start_date, end_date)
if validate_data(spy_data, ["o", "h", "l", "c", "v", "t"]):
    print("Data is valid")
else:
    print("Data validation failed")
```

### 4. Performance Optimization

```python
# Use batch endpoints when possible
def fetch_multiple_tickers(tickers, start_date, end_date):
    """Fetch data for multiple tickers efficiently"""
    
    # Use snapshot endpoint for current data
    url = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers"
    params = {
        "tickers": ",".join(tickers),
        "apiKey": api_key
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

---

## Alternative Data Sources

### 1. Barchart Premier (Recommended for Options)

**Pros**:
- You already have access
- Complete options chains
- Historical data available
- CSV export format

**Cons**:
- Manual download required
- Need conversion scripts

### 2. ThetaData

**Pros**:
- Designed for options backtesting
- Lumibot integration available
- Automated data fetching

**Cons**:
- Additional $59/month cost
- Need to sign up

### 3. Yahoo Finance (Free)

**Pros**:
- Free
- Good for basic backtesting
- Easy to use

**Cons**:
- Limited historical depth
- No options data
- Rate limiting

---

## Conclusion

For your **Zero Loss Butterfly** strategy:

1. **Immediate Solution**: Use Barchart Premier data with custom conversion
2. **Long-term Solution**: Upgrade to Polygon Options Developer tier ($79/month)
3. **Alternative**: Consider ThetaData for options-specific backtesting

The key is ensuring you have access to historical options data with the right format for Lumibot integration.

---

## References

- [Polygon.io Options Pricing](https://polygon.io/pricing?product=options)
- [Polygon.io Stocks Pricing](https://polygon.io/stocks)
- [Polygon.io API Documentation](https://polygon.io/docs/rest/quickstart#next-steps)
- [Lumibot Documentation](https://lumibot.readthedocs.io/)

