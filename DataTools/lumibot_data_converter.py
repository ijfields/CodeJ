#!/usr/bin/env python3
"""
Lumibot Data Converter
Converts CSV data from Barchart and Yahoo Finance to Lumibot-compatible format
"""

import pandas as pd
import pickle
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os

class LumibotDataConverter:
    def __init__(self, data_dir="data/barchart"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("data/lumibot")
        self.output_dir.mkdir(exist_ok=True)
        
    def convert_stock_data(self, csv_file):
        """
        Convert Barchart stock CSV to Lumibot format
        
        Expected format:
        - MultiIndex: (symbol, datetime)
        - Columns: open, high, low, close, volume
        """
        print(f"📊 Converting stock data from {csv_file}")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Convert Time to datetime
        df['datetime'] = pd.to_datetime(df['Time'])
        
        # Set MultiIndex
        df = df.set_index(['Symbol', 'datetime'])
        
        # Rename columns to match Lumibot expectations
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Last': 'close',
            'Volume': 'volume'
        })
        
        # Select only required columns
        stock_data = df[['open', 'high', 'low', 'close', 'volume']]
        
        # Sort by symbol and datetime
        stock_data = stock_data.sort_index()
        
        print(f"✅ Converted {len(stock_data)} stock records")
        print(f"📈 Symbols: {stock_data.index.get_level_values('Symbol').unique().tolist()}")
        print(f"📅 Date range: {stock_data.index.get_level_values('datetime').min()} to {stock_data.index.get_level_values('datetime').max()}")
        
        return stock_data
    
    def convert_options_data(self, csv_file):
        """
        Convert Yahoo options CSV to Lumibot format
        
        Expected format:
        - Dictionary of DataFrames by symbol
        - Each DataFrame contains options contracts with metadata
        """
        print(f"📊 Converting options data from {csv_file}")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Convert expiration to datetime
        df['expiration'] = pd.to_datetime(df['expiration'])
        
        # Create option symbol in Lumibot format
        # Format: SYMBOL_YYMMDD_TYPE_STRIKE
        df['option_symbol'] = df.apply(lambda x: 
            f"{x['symbol']}_{x['expiration'].strftime('%y%m%d')}_{x['option_type'][0].upper()}_{x['strike']:.0f}", 
            axis=1
        )
        
        # Add additional required fields
        df['bid'] = df.get('bid', np.nan)
        df['ask'] = df.get('ask', np.nan)
        df['last_price'] = df.get('lastPrice', np.nan)
        df['volume'] = df.get('volume', 0)
        df['open_interest'] = df.get('openInterest', 0)
        
        # Group by symbol
        options_by_symbol = {}
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol].copy()
            
            # Set option_symbol as index
            symbol_data = symbol_data.set_index('option_symbol')
            
            # Select required columns
            symbol_data = symbol_data[[
                'strike', 'expiration', 'option_type', 'last_price', 
                'bid', 'ask', 'volume', 'open_interest', 'days_to_expiry'
            ]]
            
            options_by_symbol[symbol] = symbol_data
            
            print(f"✅ {symbol}: {len(symbol_data)} options contracts")
        
        return options_by_symbol
    
    def create_lumibot_data_structure(self, stock_data, options_data):
        """
        Create the complete data structure for Lumibot backtesting
        """
        print("🔧 Creating Lumibot data structure...")
        
        # Create the main data structure
        lumibot_data = {
            'stocks': stock_data,
            'options': options_data,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'stock_symbols': stock_data.index.get_level_values('Symbol').unique().tolist(),
                'options_symbols': list(options_data.keys()),
                'date_range': {
                    'start': stock_data.index.get_level_values('datetime').min().isoformat(),
                    'end': stock_data.index.get_level_values('datetime').max().isoformat()
                }
            }
        }
        
        return lumibot_data
    
    def save_lumibot_data(self, lumibot_data, filename="backtest_data.pkl"):
        """
        Save data in Lumibot-compatible format
        """
        output_path = self.output_dir / filename
        
        print(f"💾 Saving Lumibot data to {output_path}")
        
        with open(output_path, "wb") as f:
            pickle.dump(lumibot_data, f)
        
        # Also save as separate files for easier access
        with open(self.output_dir / "stock_data.pkl", "wb") as f:
            pickle.dump(lumibot_data['stocks'], f)
        
        with open(self.output_dir / "options_data.pkl", "wb") as f:
            pickle.dump(lumibot_data['options'], f)
        
        # Save metadata as JSON
        import json
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(lumibot_data['metadata'], f, indent=2, default=str)
        
        print(f"✅ Data saved successfully")
        print(f"📁 Files created:")
        print(f"   - {output_path}")
        print(f"   - {self.output_dir / 'stock_data.pkl'}")
        print(f"   - {self.output_dir / 'options_data.pkl'}")
        print(f"   - {self.output_dir / 'metadata.json'}")
    
    def load_lumibot_data(self, filename="backtest_data.pkl"):
        """
        Load Lumibot data from pickle file
        """
        output_path = self.output_dir / filename
        
        if not output_path.exists():
            raise FileNotFoundError(f"Data file not found: {output_path}")
        
        print(f"📂 Loading Lumibot data from {output_path}")
        
        with open(output_path, "rb") as f:
            data = pickle.load(f)
        
        return data
    
    def validate_data(self, lumibot_data):
        """
        Validate the converted data structure
        """
        print("🔍 Validating data structure...")
        
        # Check stock data
        stocks = lumibot_data['stocks']
        required_stock_cols = ['open', 'high', 'low', 'close', 'volume']
        
        if not all(col in stocks.columns for col in required_stock_cols):
            print("❌ Stock data missing required columns")
            return False
        
        if not isinstance(stocks.index, pd.MultiIndex):
            print("❌ Stock data should have MultiIndex (symbol, datetime)")
            return False
        
        # Check options data
        options = lumibot_data['options']
        required_option_cols = ['strike', 'expiration', 'option_type', 'last_price']
        
        for symbol, option_data in options.items():
            if not all(col in option_data.columns for col in required_option_cols):
                print(f"❌ Options data for {symbol} missing required columns")
                return False
        
        print("✅ Data structure validation passed")
        return True
    
    def convert_all_data(self):
        """
        Convert all available data files
        """
        print("🚀 Starting complete data conversion...")
        
        # Find data files
        stock_file = None
        options_files = []
        
        for file in self.data_dir.glob("*.csv"):
            if "daily-historical" in file.name:
                stock_file = file
            elif "options_yahoo" in file.name:
                options_files.append(file)
        
        if not stock_file:
            raise FileNotFoundError("Stock data file not found")
        
        if not options_files:
            raise FileNotFoundError("Options data files not found")
        
        # Convert stock data
        stock_data = self.convert_stock_data(stock_file)
        
        # Convert options data
        all_options = {}
        for options_file in options_files:
            symbol_options = self.convert_options_data(options_file)
            all_options.update(symbol_options)
        
        # Create complete data structure
        lumibot_data = self.create_lumibot_data_structure(stock_data, all_options)
        
        # Validate data
        if not self.validate_data(lumibot_data):
            raise ValueError("Data validation failed")
        
        # Save data
        self.save_lumibot_data(lumibot_data)
        
        print("🎉 Data conversion completed successfully!")
        return lumibot_data

def main():
    """
    Main function to run the data conversion
    """
    print("=" * 60)
    print("🎯 LUMIBOT DATA CONVERTER")
    print("=" * 60)
    
    # Initialize converter
    converter = LumibotDataConverter()
    
    try:
        # Convert all data
        lumibot_data = converter.convert_all_data()
        
        # Display summary
        print("\n📊 CONVERSION SUMMARY")
        print("=" * 30)
        
        stocks = lumibot_data['stocks']
        options = lumibot_data['options']
        
        print(f"📈 Stock Records: {len(stocks):,}")
        print(f"📈 Stock Symbols: {', '.join(stocks.index.get_level_values('Symbol').unique())}")
        print(f"📅 Date Range: {stocks.index.get_level_values('datetime').min().date()} to {stocks.index.get_level_values('datetime').max().date()}")
        
        total_options = sum(len(data) for data in options.values())
        print(f"📊 Options Contracts: {total_options:,}")
        for symbol, data in options.items():
            print(f"   {symbol}: {len(data):,} contracts")
        
        print(f"\n✅ Data ready for Lumibot backtesting!")
        print(f"📁 Output directory: {converter.output_dir}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

if __name__ == "__main__":
    main()

