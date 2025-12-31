#!/usr/bin/env python3
"""
Download SPY/QQQ data from Polygon.io for Lumibot PandasDataBacktesting
This will match the November 2024 Optionsful log
"""

import os
import sys
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from polygon import RESTClient

load_dotenv()

def download_spy_qqq_november_2024():
    """
    Download SPY and QQQ 1-minute data for November 2024
    This will be used with PandasDataBacktesting in Lumibot
    """
    
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("❌ ERROR: POLYGON_API_KEY not found in .env")
        return False
    
    client = RESTClient(api_key)
    
    # Create data directory for Lumibot
    data_dir = Path("data/polygon/november_2024")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("DOWNLOADING POLYGON DATA FOR LUMIBOT BACKTESTING")
    print("November 2024 - Matching Optionsful Log")
    print("=" * 80)
    
    symbols = ['SPY', 'QQQ']
    
    for symbol in symbols:
        print(f"\n📥 Downloading {symbol} 1-minute data...")
        
        try:
            # Get 1-minute bars for November 2024
            aggs = client.get_aggs(
                symbol,
                1,           # 1-minute bars
                'minute',
                '2024-11-01',  # November 1
                '2024-11-30'   # November 30
            )
            
            aggs_list = list(aggs)
            
            if not aggs_list:
                print(f"   ⚠️ No data found for {symbol}")
                continue
            
            # Convert to DataFrame
            data = []
            for agg in aggs_list:
                dt = datetime.fromtimestamp(agg.timestamp / 1000)
                data.append({
                    'timestamp': dt,
                    'open': agg.open,
                    'high': agg.high,
                    'low': agg.low,
                    'close': agg.close,
                    'volume': agg.volume,
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            # Save to CSV for PandasDataBacktesting
            output_file = data_dir / f"{symbol}_1min_nov2024.csv"
            df.to_csv(output_file)
            
            print(f"   ✅ Saved {len(df)} bars to {output_file.name}")
            print(f"   📅 Date range: {df.index.min()} to {df.index.max()}")
            print(f"   💵 Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 80)
    print(f"\n📁 Data saved to: {data_dir}")
    print("\n📋 Files created:")
    for f in data_dir.glob("*.csv"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"   - {f.name} ({size_mb:.1f} MB)")
    
    return True

if __name__ == "__main__":
    print("\n🎯 GOAL: Download data for Lumibot PandasDataBacktesting")
    print("   This will be used to backtest November 2024")
    print("   Matching the Optionsful log with 54 trades!\n")
    
    success = download_spy_qqq_november_2024()
    
    if success:
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
1. ✅ SPY/QQQ data downloaded
2. Create credentials.py with API keys and backtest flag
3. Build Lumibot strategy with PandasDataBacktesting
4. Run backtest on November 2024
5. Compare with Optionsful log (54 trades)
6. Switch to Tradier for paper/live trading

📊 Lumibot Pattern:
   - Backtesting: PandasDataBacktesting(df_dict)
   - Live/Paper: Tradier broker with real-time data
   - Same strategy code for both!
        """)
    else:
        print("\n❌ Download failed - check errors above")

