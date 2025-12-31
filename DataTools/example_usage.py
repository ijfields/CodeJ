#!/usr/bin/env python3
"""
Example usage of Polygon data tools for Zero Loss Butterfly strategy
"""

from polygon_data_manager import PolygonDataManager
from download_polygon_data_flexible import download_zero_loss_butterfly_data
import pandas as pd

def example_download_and_convert():
    """Example: Download data and convert for Lumibot"""
    
    print("🎯 EXAMPLE: Download and Convert Data for Zero Loss Butterfly")
    print("=" * 80)
    
    # Initialize manager
    manager = PolygonDataManager()
    
    # Download V data for April-October 2024
    print("\n1. Downloading V data...")
    output_dir = manager.download_butterfly_data(
        symbol="V",
        start_date="2024-04-15", 
        end_date="2024-10-17"
    )
    
    if output_dir:
        # Convert to Lumibot format
        print("\n2. Converting to Lumibot format...")
        data_dict = manager.create_lumibot_data_dict(output_dir)
        
        if data_dict:
            # Save as pickle for easy loading
            pickle_file = "data/polygon/v_lumibot_data.pkl"
            manager.save_lumibot_data(data_dict, pickle_file)
            
            # Show summary
            manager.get_data_summary(data_dict)
            
            print(f"\n✅ Data ready for Lumibot backtesting!")
            print(f"📁 Use this in your strategy: {pickle_file}")
            
            return data_dict
    
    return None

def example_use_with_lumibot():
    """Example: How to use the data with Lumibot"""
    
    print("\n🎯 EXAMPLE: Using Data with Lumibot")
    print("=" * 80)
    
    # This is how you would use it in your Lumibot strategy
    example_code = '''
# In your Zero Loss Butterfly strategy file:

import pickle
from lumibot.backtesting import PandasDataBacktesting
from lumibot.data_sources import PandasData

# Load the data we downloaded
with open('data/polygon/v_lumibot_data.pkl', 'rb') as f:
    data_dict = pickle.load(f)

# Run backtest with PandasDataBacktesting
strategy.backtest(
    PandasDataBacktesting,
    datetime(2024, 4, 15),
    datetime(2024, 10, 17),
    pandas_data=data_dict,  # Use our downloaded data
    parameters={
        "symbol": "V",
        "target_dte": 57,
        "strike_spacing": 10,
        # ... other parameters
    }
)
    '''
    
    print("Copy this code into your strategy:")
    print(example_code)

def example_download_multiple_symbols():
    """Example: Download data for multiple symbols"""
    
    print("\n🎯 EXAMPLE: Download Multiple Symbols")
    print("=" * 80)
    
    manager = PolygonDataManager()
    
    # Download both V and SPY data
    symbols = ["V", "SPY"]
    data_dicts = {}
    
    for symbol in symbols:
        print(f"\n📊 Downloading {symbol}...")
        
        if symbol == "V":
            start_date, end_date = "2024-04-15", "2024-10-17"
        else:  # SPY
            start_date, end_date = "2024-05-01", "2024-10-31"
        
        output_dir = manager.download_butterfly_data(symbol, start_date, end_date)
        
        if output_dir:
            data_dict = manager.create_lumibot_data_dict(output_dir)
            if data_dict:
                data_dicts.update(data_dict)
    
    if data_dicts:
        # Save combined data
        manager.save_lumibot_data(data_dicts, "data/polygon/combined_lumibot_data.pkl")
        manager.get_data_summary(data_dicts)
        
        print(f"\n✅ Combined data ready: {len(data_dicts)} symbols")

def main():
    """Run examples"""
    
    print("🎯 POLYGON DATA TOOLS - USAGE EXAMPLES")
    print("=" * 80)
    
    try:
        # Example 1: Download and convert V data
        data_dict = example_download_and_convert()
        
        # Example 2: Show Lumibot usage
        example_use_with_lumibot()
        
        # Example 3: Download multiple symbols
        example_download_multiple_symbols()
        
        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETE!")
        print("=" * 80)
        print("""
Next steps:
1. Use the downloaded data in your Zero Loss Butterfly strategy
2. Run backtest with PandasDataBacktesting
3. Compare results with your previous tests
4. If options data is still missing, use Barchart Premier data
        """)
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")

if __name__ == "__main__":
    main()

