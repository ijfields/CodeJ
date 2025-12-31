#!/usr/bin/env python3
"""
Polygon Data Manager for Zero Loss Butterfly Strategy
Integrates with existing credentials system and provides easy data management
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import pickle
from download_polygon_data_flexible import PolygonDataDownloader

# Import your existing credentials
try:
    import sys
    from pathlib import Path
    # Add parent directory to path to find credentials.py
    sys.path.append(str(Path(__file__).parent.parent))
    from credentials import POLYGON_CONFIG
except ImportError:
    print("❌ credentials.py not found. Please ensure it exists with POLYGON_CONFIG")
    sys.exit(1)

class PolygonDataManager:
    """Manages Polygon data for Zero Loss Butterfly backtesting"""
    
    def __init__(self):
        """Initialize with credentials from credentials.py"""
        self.api_key = POLYGON_CONFIG.get("API_KEY")
        if not self.api_key:
            raise ValueError("❌ POLYGON_CONFIG['API_KEY'] not found in credentials.py")
        
        self.downloader = PolygonDataDownloader(self.api_key)
        self.data_dir = Path("data/polygon")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_butterfly_data(self, symbol="V", start_date="2024-04-15", end_date="2024-10-17"):
        """
        Download data specifically for Zero Loss Butterfly strategy
        
        Args:
            symbol: Stock symbol (V, SPY, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        
        print(f"🎯 DOWNLOADING {symbol} DATA FOR ZERO LOSS BUTTERFLY")
        print("=" * 80)
        
        # Create descriptive folder name
        start_str = start_date.replace('-', '')
        end_str = end_date.replace('-', '')
        folder_name = f"{symbol.lower()}_butterfly_{start_str}_{end_str}"
        output_dir = self.data_dir / folder_name
        
        success = self.downloader.download_data(
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            timeframe='day',  # Daily bars for butterfly strategy
            multiplier=1,
            output_dir=str(output_dir),
            description=f"{symbol}_butterfly"
        )
        
        if success:
            print(f"\n✅ {symbol} data downloaded successfully!")
            print(f"📁 Location: {output_dir}")
            return str(output_dir)
        else:
            print(f"\n❌ Failed to download {symbol} data")
            return None
    
    def download_multiple_periods(self, symbol="V"):
        """Download multiple time periods for comprehensive testing"""
        
        periods = [
            {
                "name": "April-October 2024",
                "start": "2024-04-15",
                "end": "2024-10-17"
            },
            {
                "name": "August-October 2024", 
                "start": "2024-08-21",
                "end": "2024-10-17"
            },
            {
                "name": "SPY 6-Month Test",
                "symbol": "SPY",
                "start": "2024-05-01", 
                "end": "2024-10-31"
            }
        ]
        
        downloaded_dirs = []
        
        for period in periods:
            print(f"\n📊 {period['name']}")
            print("-" * 40)
            
            period_symbol = period.get('symbol', symbol)
            output_dir = self.download_butterfly_data(
                symbol=period_symbol,
                start_date=period['start'],
                end_date=period['end']
            )
            
            if output_dir:
                downloaded_dirs.append(output_dir)
        
        return downloaded_dirs
    
    def create_lumibot_data_dict(self, data_dir):
        """Create data dictionary for Lumibot PandasDataBacktesting"""
        
        data_dict = {}
        data_path = Path(data_dir)
        
        if not data_path.exists():
            print(f"❌ Data directory not found: {data_dir}")
            return None
        
        # Find all CSV files
        csv_files = list(data_path.glob("*.csv"))
        
        if not csv_files:
            print(f"❌ No CSV files found in {data_dir}")
            return None
        
        for csv_file in csv_files:
            # Extract symbol from filename (e.g., V_1d_20240415_20241017.csv -> V)
            symbol = csv_file.stem.split('_')[0]
            
            try:
                df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                data_dict[symbol] = df
                print(f"✅ Loaded {symbol}: {len(df)} bars")
            except Exception as e:
                print(f"❌ Error loading {csv_file.name}: {e}")
        
        return data_dict
    
    def save_lumibot_data(self, data_dict, output_file):
        """Save data dictionary as pickle for easy loading"""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(data_dict, f)
        
        print(f"✅ Saved Lumibot data to {output_file}")
        return output_path
    
    def load_lumibot_data(self, pickle_file):
        """Load data dictionary from pickle file"""
        
        with open(pickle_file, 'rb') as f:
            data_dict = pickle.load(f)
        
        print(f"✅ Loaded Lumibot data from {pickle_file}")
        return data_dict
    
    def get_data_summary(self, data_dict):
        """Get summary of loaded data"""
        
        print("\n📊 DATA SUMMARY")
        print("=" * 50)
        
        for symbol, df in data_dict.items():
            print(f"\n{symbol}:")
            print(f"  📅 Date range: {df.index.min()} to {df.index.max()}")
            print(f"  📊 Bars: {len(df)}")
            print(f"  💵 Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
            print(f"  📈 Avg volume: {df['volume'].mean():,.0f}")

def main():
    """Main function for command line usage"""
    
    print("🎯 POLYGON DATA MANAGER FOR ZERO LOSS BUTTERFLY")
    print("=" * 80)
    
    try:
        manager = PolygonDataManager()
        
        # Check if we have command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "download":
                # Download specific data
                symbol = sys.argv[2] if len(sys.argv) > 2 else "V"
                start_date = sys.argv[3] if len(sys.argv) > 3 else "2024-04-15"
                end_date = sys.argv[4] if len(sys.argv) > 4 else "2024-10-17"
                
                output_dir = manager.download_butterfly_data(symbol, start_date, end_date)
                
                if output_dir:
                    # Create Lumibot data dict
                    data_dict = manager.create_lumibot_data_dict(output_dir)
                    if data_dict:
                        # Save as pickle
                        pickle_file = f"data/polygon/{symbol.lower()}_lumibot_data.pkl"
                        manager.save_lumibot_data(data_dict, pickle_file)
                        manager.get_data_summary(data_dict)
            
            elif command == "multi":
                # Download multiple periods
                symbol = sys.argv[2] if len(sys.argv) > 2 else "V"
                manager.download_multiple_periods(symbol)
            
            elif command == "convert":
                # Convert existing data to Lumibot format
                data_dir = sys.argv[2] if len(sys.argv) > 2 else "data/polygon"
                data_dict = manager.create_lumibot_data_dict(data_dir)
                if data_dict:
                    pickle_file = f"data/polygon/lumibot_data.pkl"
                    manager.save_lumibot_data(data_dict, pickle_file)
                    manager.get_data_summary(data_dict)
            
            else:
                print(f"❌ Unknown command: {command}")
                print("Available commands: download, multi, convert")
        
        else:
            # Interactive mode
            print("""
Available commands:

1. Download single period:
   python polygon_data_manager.py download V 2024-04-15 2024-10-17

2. Download multiple periods:
   python polygon_data_manager.py multi V

3. Convert existing data:
   python polygon_data_manager.py convert data/polygon/v_butterfly_20240415_20241017

4. Quick start (download V April-October):
   python polygon_data_manager.py download
            """)
            
            # Quick start - download V data
            choice = input("\nDownload V April-October data? (y/n): ").lower()
            if choice == 'y':
                output_dir = manager.download_butterfly_data()
                if output_dir:
                    data_dict = manager.create_lumibot_data_dict(output_dir)
                    if data_dict:
                        manager.save_lumibot_data(data_dict, "data/polygon/v_lumibot_data.pkl")
                        manager.get_data_summary(data_dict)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
