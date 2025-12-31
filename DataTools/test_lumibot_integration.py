#!/usr/bin/env python3
"""
Test script to verify Lumibot data integration
"""

import pickle
import pandas as pd
from datetime import datetime

def test_lumibot_data_format():
    """Test that our downloaded data works with Lumibot format"""
    
    print("🧪 TESTING LUMIBOT DATA INTEGRATION")
    print("=" * 80)
    
    # Load the combined data we created
    try:
        with open('data/polygon/combined_lumibot_data.pkl', 'rb') as f:
            data_dict = pickle.load(f)
        
        print("✅ Successfully loaded Lumibot data")
        print(f"📊 Symbols available: {list(data_dict.keys())}")
        
        # Test each symbol
        for symbol, df in data_dict.items():
            print(f"\n📈 {symbol} Data:")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Index type: {type(df.index)}")
            print(f"   Date range: {df.index.min()} to {df.index.max()}")
            print(f"   Sample data:")
            print(f"   {df.head(2).to_string()}")
            
            # Verify required columns for Lumibot
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"   ❌ Missing columns: {missing_cols}")
            else:
                print(f"   ✅ All required columns present")
            
            # Verify data types
            print(f"   Data types:")
            for col in required_cols:
                print(f"     {col}: {df[col].dtype}")
        
        print("\n✅ Lumibot data format verification complete!")
        return True
        
    except FileNotFoundError:
        print("❌ Combined data file not found. Run example_usage.py first.")
        return False
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def test_pandas_data_backtesting_import():
    """Test that we can import Lumibot components"""
    
    print("\n🧪 TESTING LUMIBOT IMPORTS")
    print("=" * 80)
    
    try:
        from lumibot.backtesting import PandasDataBacktesting
        print("✅ PandasDataBacktesting imported successfully")
        
        from lumibot.data_sources import PandasData
        print("✅ PandasData imported successfully")
        
        print("✅ All Lumibot imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure Lumibot is installed: pip install lumibot")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_usage_example():
    """Show how to use the data in a Lumibot strategy"""
    
    print("\n📋 LUMIBOT USAGE EXAMPLE")
    print("=" * 80)
    
    example_code = '''
# Example Zero Loss Butterfly strategy using our data

import pickle
from datetime import datetime
from lumibot.backtesting import PandasDataBacktesting
from lumibot.strategies import Strategy

class ZeroLossButterfly(Strategy):
    def initialize(self):
        self.symbol = self.parameters.get("symbol", "V")
        self.target_dte = self.parameters.get("target_dte", 57)
        # ... your strategy logic here
    
    def on_trading_iteration(self):
        # ... your trading logic here
        pass

# Load our downloaded data
with open('data/polygon/combined_lumibot_data.pkl', 'rb') as f:
    data_dict = pickle.load(f)

# Run backtest
ZeroLossButterfly.backtest(
    PandasDataBacktesting,
    datetime(2024, 4, 15),  # Start date
    datetime(2024, 10, 17), # End date
    pandas_data=data_dict,  # Our downloaded data
    parameters={
        "symbol": "V",
        "target_dte": 57,
        "strike_spacing": 10,
    }
)
    '''
    
    print("Copy this code into your strategy:")
    print(example_code)

def main():
    """Run all tests"""
    
    print("🎯 POLYGON DATA TOOLS - LUMIBOT INTEGRATION TEST")
    print("=" * 80)
    
    # Test 1: Data format
    data_ok = test_lumibot_data_format()
    
    # Test 2: Lumibot imports
    imports_ok = test_pandas_data_backtesting_import()
    
    # Show usage example
    show_usage_example()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Data Format: {'✅ PASS' if data_ok else '❌ FAIL'}")
    print(f"Lumibot Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    
    if data_ok and imports_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Polygon data is ready for Lumibot backtesting!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

