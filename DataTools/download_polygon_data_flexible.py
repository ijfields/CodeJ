#!/usr/bin/env python3
"""
Flexible Polygon.io Data Downloader for Lumibot Backtesting
Supports multiple symbols, date ranges, and timeframes
"""

import os
import sys
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from polygon import RESTClient
import time

load_dotenv()

class PolygonDataDownloader:
    """Flexible data downloader for Polygon.io with Lumibot integration"""
    
    def __init__(self, api_key=None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("❌ POLYGON_API_KEY not found in .env or provided")
        
        self.client = RESTClient(self.api_key)
        
    def download_data(self, symbols, start_date, end_date, timeframe='minute', 
                     multiplier=1, output_dir=None, description=""):
        """
        Download data for multiple symbols and date range
        
        Args:
            symbols: List of symbols (e.g., ['SPY', 'V', 'QQQ'])
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            timeframe: 'minute', 'hour', 'day', 'week', 'month'
            multiplier: Bar size (1, 5, 15, 30, 60 for minutes)
            output_dir: Output directory (auto-generated if None)
            description: Description for output folder
        """
        
        # Convert string dates to datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Create output directory
        if output_dir is None:
            date_str = start_date.strftime('%Y%m%d')
            output_dir = f"data/polygon/{description}_{date_str}" if description else f"data/polygon/{date_str}"
        
        data_dir = Path(output_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print("POLYGON.IO DATA DOWNLOADER")
        print("=" * 80)
        print(f"📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"⏱️  Timeframe: {multiplier} {timeframe}")
        print(f"📊 Symbols: {', '.join(symbols)}")
        print(f"📁 Output: {data_dir}")
        print("=" * 80)
        
        success_count = 0
        total_size = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 📥 Downloading {symbol}...")
            
            try:
                # Download data
                aggs = self.client.get_aggs(
                    symbol,
                    multiplier,
                    timeframe,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                aggs_list = list(aggs)
                
                if not aggs_list:
                    print(f"   ⚠️ No data found for {symbol}")
                    continue
                
                # Convert to DataFrame
                df = self._convert_to_dataframe(aggs_list)
                
                # Save to CSV
                filename = f"{symbol}_{multiplier}{timeframe[0]}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
                output_file = data_dir / filename
                df.to_csv(output_file)
                
                file_size = output_file.stat().st_size / (1024 * 1024)
                total_size += file_size
                success_count += 1
                
                print(f"   ✅ Saved {len(df)} bars to {filename}")
                print(f"   📅 Range: {df.index.min()} to {df.index.max()}")
                print(f"   💵 Price: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
                print(f"   📦 Size: {file_size:.1f} MB")
                
                # Rate limiting for free tier
                if i < len(symbols):
                    time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error downloading {symbol}: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully downloaded: {success_count}/{len(symbols)} symbols")
        print(f"📁 Output directory: {data_dir}")
        print(f"📦 Total size: {total_size:.1f} MB")
        
        if success_count > 0:
            print("\n📋 Files created:")
            for f in data_dir.glob("*.csv"):
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"   - {f.name} ({size_mb:.1f} MB)")
        
        return success_count > 0
    
    def _convert_to_dataframe(self, aggs_list):
        """Convert Polygon aggregates to pandas DataFrame"""
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
        return df
    
    def create_lumibot_data_dict(self, data_dir):
        """Create data dictionary for Lumibot PandasDataBacktesting"""
        data_dict = {}
        
        for csv_file in Path(data_dir).glob("*.csv"):
            symbol = csv_file.stem.split('_')[0]  # Extract symbol from filename
            df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
            data_dict[symbol] = df
        
        return data_dict

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="Download Polygon.io data for Lumibot backtesting")
    
    # Required arguments
    parser.add_argument('symbols', nargs='+', help='Symbols to download (e.g., SPY V QQQ)')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    
    # Optional arguments
    parser.add_argument('--timeframe', default='minute', 
                       choices=['minute', 'hour', 'day', 'week', 'month'],
                       help='Timeframe (default: minute)')
    parser.add_argument('--multiplier', type=int, default=1,
                       help='Bar size multiplier (default: 1)')
    parser.add_argument('--output-dir', help='Output directory (auto-generated if not provided)')
    parser.add_argument('--description', default='', help='Description for output folder')
    
    args = parser.parse_args()
    
    try:
        # Initialize downloader
        downloader = PolygonDataDownloader()
        
        # Download data
        success = downloader.download_data(
            symbols=args.symbols,
            start_date=args.start_date,
            end_date=args.end_date,
            timeframe=args.timeframe,
            multiplier=args.multiplier,
            output_dir=args.output_dir,
            description=args.description
        )
        
        if success:
            print("\n" + "=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print("""
1. ✅ Data downloaded successfully
2. Use with Lumibot PandasDataBacktesting:
   
   from lumibot.backtesting import PandasDataBacktesting
   from lumibot.data_sources import PandasData
   
   # Load your data
   data_dict = load_polygon_data('path/to/your/data')
   
   # Run backtest
   strategy.backtest(
       PandasDataBacktesting,
       start_date, end_date,
       pandas_data=data_dict
   )
            """)
        else:
            print("\n❌ Download failed - check errors above")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

# Predefined configurations for common use cases
def download_zero_loss_butterfly_data():
    """Download data specifically for Zero Loss Butterfly strategy"""
    
    downloader = PolygonDataDownloader()
    
    # Configuration for Zero Loss Butterfly
    configs = [
        {
            "name": "SPY 6-Month Test",
            "symbols": ["SPY"],
            "start_date": "2024-05-01",
            "end_date": "2024-10-31",
            "timeframe": "day",
            "multiplier": 1,
            "description": "spy_6month_butterfly"
        },
        {
            "name": "V April-October",
            "symbols": ["V"],
            "start_date": "2024-04-15",
            "end_date": "2024-10-17",
            "timeframe": "day",
            "multiplier": 1,
            "description": "v_apr_oct_butterfly"
        },
        {
            "name": "V August-October",
            "symbols": ["V"],
            "start_date": "2024-08-21",
            "end_date": "2024-10-17",
            "timeframe": "day",
            "multiplier": 1,
            "description": "v_aug_oct_butterfly"
        }
    ]
    
    print("🎯 ZERO LOSS BUTTERFLY DATA DOWNLOAD")
    print("=" * 80)
    
    for config in configs:
        print(f"\n📊 {config['name']}")
        print("-" * 40)
        
        success = downloader.download_data(
            symbols=config["symbols"],
            start_date=config["start_date"],
            end_date=config["end_date"],
            timeframe=config["timeframe"],
            multiplier=config["multiplier"],
            description=config["description"]
        )
        
        if not success:
            print(f"   ❌ Failed to download {config['name']}")
    
    print("\n✅ Zero Loss Butterfly data download complete!")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show help
        print("🎯 POLYGON.IO DATA DOWNLOADER")
        print("=" * 80)
        print("""
Usage Examples:

1. Download SPY data for Zero Loss Butterfly:
   python download_polygon_data_flexible.py SPY --start-date 2024-04-15 --end-date 2024-10-17

2. Download multiple symbols:
   python download_polygon_data_flexible.py SPY V QQQ --start-date 2024-01-01 --end-date 2024-12-31

3. Download minute data:
   python download_polygon_data_flexible.py SPY --start-date 2024-11-01 --end-date 2024-11-30 --timeframe minute

4. Download hourly data:
   python download_polygon_data_flexible.py SPY --start-date 2024-01-01 --end-date 2024-12-31 --timeframe hour --multiplier 4

5. Predefined Zero Loss Butterfly data:
   python -c "from download_polygon_data_flexible import download_zero_loss_butterfly_data; download_zero_loss_butterfly_data()"

For more options, run: python download_polygon_data_flexible.py --help
        """)
    else:
        main()

