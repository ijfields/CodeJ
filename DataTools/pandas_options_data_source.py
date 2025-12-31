#!/usr/bin/env python3
"""
Pandas Options Data Source for Lumibot

Custom data source class that enables options backtesting using converted pandas data.
Extends Lumibot's DataSource base class to support options chains from pickled DataFrames.

This solves the limitation where PandasDataBacktesting.get_chains() always returns None.
"""

import pickle
import pandas as pd
from datetime import datetime, date
from typing import Dict, Optional, Any, Union
from pathlib import Path

from lumibot.data_sources.data_source_backtesting import DataSourceBacktesting
from lumibot.entities import Asset


class PandasOptionsDataSource(DataSourceBacktesting):
    """
    Custom data source for options backtesting using pandas DataFrames.

    Loads stock and options data from pickled files and provides:
    - get_chains() for options chain retrieval
    - get_historical_prices() for stock price history
    - get_last_price() for current prices
    """

    # Required flag for Lumibot to recognize this as a backtesting data source
    IS_BACKTESTING_DATA_SOURCE = True

    def __init__(self, datetime_start=None, datetime_end=None, data_dir: str = "data/lumibot", **kwargs):
        """
        Initialize the data source with pickled data.

        Args:
            datetime_start: Start datetime for backtesting
            datetime_end: End datetime for backtesting
            data_dir: Directory containing stock_data.pkl and options_data.pkl
            **kwargs: Additional arguments for DataSourceBacktesting
        """
        self.data_dir = Path(data_dir)
        self.stock_data = None
        self.options_data = None
        self.metadata = None

        # Load data first (before calling super().__init__)
        self._load_data()

        # If no dates provided, use data range from metadata
        if datetime_start is None or datetime_end is None:
            if self.metadata:
                from datetime import datetime as dt
                datetime_start = dt.fromisoformat(self.metadata['date_range']['start'])
                datetime_end = dt.fromisoformat(self.metadata['date_range']['end'])

        # Call parent constructor with datetime range
        super().__init__(datetime_start=datetime_start, datetime_end=datetime_end, **kwargs)
    
    def _load_data(self):
        """Load pickled data files."""
        try:
            # Load stock data
            stock_file = self.data_dir / "stock_data.pkl"
            if stock_file.exists():
                with open(stock_file, 'rb') as f:
                    self.stock_data = pickle.load(f)
                print(f"[OK] Loaded stock data: {len(self.stock_data)} records")
            else:
                print(f"[WARN] Stock data file not found: {stock_file}")
            
            # Load options data
            options_file = self.data_dir / "options_data.pkl"
            if options_file.exists():
                with open(options_file, 'rb') as f:
                    self.options_data = pickle.load(f)
                print(f"[OK] Loaded options data: {sum(len(df) for df in self.options_data.values())} contracts")
            else:
                print(f"[WARN] Options data file not found: {options_file}")
            
            # Load metadata
            metadata_file = self.data_dir / "metadata.json"
            if metadata_file.exists():
                import json
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                print(f"[OK] Loaded metadata: {self.metadata.get('date_range', 'Unknown date range')}")
            
        except Exception as e:
            print(f"[FAIL] Error loading data: {e}")
            raise
    
    def get_chains(self, asset: Asset, quote: Optional[Any] = None) -> Optional[Dict]:
        """
        Get options chain for the specified asset.
        
        Args:
            asset: Asset object with symbol
            quote: Optional quote object (not used in this implementation)
            
        Returns:
            Dictionary with options chain data in Lumibot format:
            {expiration_date: {strike: {option_type: contract_data}}}
        """
        if not self.options_data:
            print("[FAIL] No options data loaded")
            return None
        
        symbol = asset.symbol
        if symbol not in self.options_data:
            print(f"[FAIL] No options data for symbol: {symbol}")
            return None
        
        # Get options DataFrame for this symbol
        options_df = self.options_data[symbol]
        
        if options_df.empty:
            print(f"[FAIL] Empty options data for symbol: {symbol}")
            return None
        
        # Convert to Lumibot chains format
        chains = {}
        
        # Group by expiration date
        for expiration, exp_group in options_df.groupby('expiration'):
            exp_date = pd.to_datetime(expiration).date()
            chains[exp_date] = {}
            
            # Group by strike
            for strike, strike_group in exp_group.groupby('strike'):
                chains[exp_date][strike] = {}
                
                # Separate calls and puts
                for _, contract in strike_group.iterrows():
                    option_type = contract['option_type'].upper()
                    
                    # Create contract data in Lumibot format
                    # Handle NaN values properly
                    def safe_int(value, default=0):
                        try:
                            if pd.isna(value):
                                return default
                            return int(value)
                        except (ValueError, TypeError):
                            return default
                    
                    def safe_float(value, default=0.0):
                        try:
                            if pd.isna(value):
                                return default
                            return float(value)
                        except (ValueError, TypeError):
                            return default
                    
                    contract_data = {
                        'strike': safe_float(contract['strike']),
                        'expiration': exp_date,
                        'option_type': option_type,
                        'last_price': safe_float(contract.get('last_price', 0.0)),
                        'bid': safe_float(contract.get('bid', 0.0)),
                        'ask': safe_float(contract.get('ask', 0.0)),
                        'volume': safe_int(contract.get('volume', 0)),
                        'open_interest': safe_int(contract.get('open_interest', 0)),
                        'days_to_expiry': safe_int(contract.get('days_to_expiry', 0))
                    }
                    
                    chains[exp_date][strike][option_type] = contract_data
        
        print(f"[OK] Retrieved options chain for {symbol}: {len(chains)} expirations")
        return chains
    
    def get_historical_prices(self, asset: Asset, length: int, timestep: str = "1D") -> Optional[pd.DataFrame]:
        """
        Get historical price data for the specified asset.
        
        Args:
            asset: Asset object with symbol
            length: Number of periods to retrieve
            timestep: Time step (e.g., "1D", "1H", "5M")
            
        Returns:
            DataFrame with OHLCV data
        """
        if not self.stock_data is not None:
            print("[FAIL] No stock data loaded")
            return None
        
        symbol = asset.symbol
        
        # For stock data, filter by symbol
        if symbol in self.stock_data.index.get_level_values('Symbol'):
            symbol_data = self.stock_data.loc[symbol]
            
            # Sort by datetime and get last 'length' records
            symbol_data = symbol_data.sort_index()
            if len(symbol_data) > length:
                symbol_data = symbol_data.tail(length)
            
            print(f"[OK] Retrieved {len(symbol_data)} historical prices for {symbol}")
            return symbol_data
        
        print(f"[FAIL] No stock data for symbol: {symbol}")
        return None
    
    def get_last_price(self, asset: Asset) -> Optional[float]:
        """
        Get the most recent price for the specified asset.
        
        Args:
            asset: Asset object with symbol
            
        Returns:
            Last price as float, or None if not found
        """
        if not self.stock_data is not None:
            return None
        
        symbol = asset.symbol
        
        # For stock data, get the most recent price
        if symbol in self.stock_data.index.get_level_values('Symbol'):
            symbol_data = self.stock_data.loc[symbol]
            if not symbol_data.empty:
                last_price = symbol_data['close'].iloc[-1]
                print(f"[OK] Last price for {symbol}: ${last_price:.2f}")
                return float(last_price)
        
        print(f"[FAIL] No price data for symbol: {symbol}")
        return None
    
    def get_available_expirations(self, symbol: str) -> list:
        """
        Get available expiration dates for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of available expiration dates
        """
        if not self.options_data or symbol not in self.options_data:
            return []
        
        options_df = self.options_data[symbol]
        expirations = sorted(options_df['expiration'].unique())
        
        print(f"[OK] Available expirations for {symbol}: {len(expirations)} dates")
        return [pd.to_datetime(exp).date() for exp in expirations]
    
    def get_available_strikes(self, symbol: str, expiration: date) -> list:
        """
        Get available strikes for a symbol and expiration.
        
        Args:
            symbol: Stock symbol
            expiration: Expiration date
            
        Returns:
            List of available strikes
        """
        if not self.options_data or symbol not in self.options_data:
            return []
        
        options_df = self.options_data[symbol]
        exp_data = options_df[options_df['expiration'] == pd.to_datetime(expiration)]
        strikes = sorted(exp_data['strike'].unique())
        
        print(f"[OK] Available strikes for {symbol} {expiration}: {len(strikes)} strikes")
        return strikes
    
    def validate_data_integrity(self) -> bool:
        """
        Validate that the loaded data is properly formatted.
        
        Returns:
            True if data is valid, False otherwise
        """
        print("[TEST] Validating data integrity...")
        
        # Check stock data
        if self.stock_data is not None:
            required_stock_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in self.stock_data.columns for col in required_stock_cols):
                print("[FAIL] Stock data missing required columns")
                return False
            
            if not isinstance(self.stock_data.index, pd.MultiIndex):
                print("[FAIL] Stock data should have MultiIndex (symbol, datetime)")
                return False
        
        # Check options data
        if self.options_data:
            required_option_cols = ['strike', 'expiration', 'option_type', 'last_price']
            for symbol, option_data in self.options_data.items():
                if not all(col in option_data.columns for col in required_option_cols):
                    print(f"[FAIL] Options data for {symbol} missing required columns")
                    return False
        
        print("[OK] Data integrity validation passed")
        return True

    def get_datetime_range(self):
        """
        Get the datetime range of available data.

        Returns:
            Tuple of (start_datetime, end_datetime) or (None, None) if no data
        """
        if self.stock_data is None or self.stock_data.empty:
            return (None, None)

        # Get the datetime index (second level of MultiIndex)
        datetime_index = self.stock_data.index.get_level_values(1)

        start_datetime = datetime_index.min()
        end_datetime = datetime_index.max()

        return (start_datetime, end_datetime)


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing PandasOptionsDataSource...")
    
    # Initialize data source
    data_source = PandasOptionsDataSource()
    
    # Validate data
    if data_source.validate_data_integrity():
        print("[OK] Data source initialized successfully")
        
        # Test with SPY
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        
        # Test get_chains
        chains = data_source.get_chains(spy_asset)
        if chains:
            print(f"[OK] Retrieved chains with {len(chains)} expirations")
        
        # Test get_last_price
        last_price = data_source.get_last_price(spy_asset)
        if last_price:
            print(f"[OK] Last price: ${last_price:.2f}")
        
        # Test get_available_expirations
        expirations = data_source.get_available_expirations("SPY")
        print(f"[OK] Available expirations: {len(expirations)}")
        
    else:
        print("[FAIL] Data validation failed")
