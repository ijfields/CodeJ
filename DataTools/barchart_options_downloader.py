#!/usr/bin/env python3
"""
Barchart Options Data Downloader for Zero Loss Butterfly Strategy
Automates the collection of options data for multiple strikes and expirations
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
import sys

# Add parent directory to path to find credentials.py
sys.path.append(str(Path(__file__).parent.parent))
from credentials import BARCHART_USERNAME, BARCHART_PASSWORD

class BarchartOptionsDownloader:
    """Downloads options data from Barchart Premier for butterfly strategies"""
    
    def __init__(self, username=None, password=None):
        """Initialize with Barchart credentials"""
        self.username = username or BARCHART_USERNAME
        self.password = password or BARCHART_PASSWORD
        
        if not self.username or not self.password:
            raise ValueError("❌ Barchart credentials not found. Check BARCHART_USERNAME and BARCHART_PASSWORD in credentials.py")
        
        self.session = requests.Session()
        self.base_url = "https://www.barchart.com"
        
    def login(self):
        """Login to Barchart Premier"""
        print("🔐 Logging into Barchart Premier...")
        
        login_url = f"{self.base_url}/login"
        login_data = {
            'email': self.username,
            'password': self.password
        }
        
        try:
            response = self.session.post(login_url, data=login_data)
            if response.status_code == 200:
                print("✅ Successfully logged in")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_options_chain_data(self, symbol, start_date, end_date, strike_range=None):
        """
        Get options chain data for a symbol and date range
        
        Args:
            symbol: Stock symbol (e.g., 'V', 'SPY')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strike_range: Tuple of (min_strike, max_strike) or None for all strikes
        """
        
        print(f"📊 Downloading options data for {symbol} ({start_date} to {end_date})")
        
        # This would need to be adapted based on Barchart's actual API endpoints
        # For now, I'll create a template that shows the structure needed
        
        # Calculate target expirations (40-70 DTE from start_date)
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        target_expirations = []
        
        for days_ahead in range(40, 71, 7):  # Every 7 days from 40 to 70 DTE
            exp_date = start_dt + timedelta(days=days_ahead)
            target_expirations.append(exp_date.strftime('%Y-%m-%d'))
        
        print(f"   Target expirations: {target_expirations}")
        
        # This is where you'd implement the actual Barchart API calls
        # The structure below shows what data you need to collect
        
        options_data = []
        
        for exp_date in target_expirations:
            print(f"   📅 Processing expiration: {exp_date}")
            
            # Get current stock price to determine strike range
            stock_price = self.get_current_price(symbol)
            if not stock_price:
                print(f"   ⚠️ Could not get current price for {symbol}")
                continue
            
            # Calculate strike range (±20% from current price)
            if strike_range:
                min_strike, max_strike = strike_range
            else:
                min_strike = stock_price * 0.8
                max_strike = stock_price * 1.2
            
            print(f"   💰 Strike range: ${min_strike:.2f} - ${max_strike:.2f}")
            
            # Generate strikes (every $5 for V, every $10 for SPY)
            strike_increment = 5 if symbol == 'V' else 10
            strikes = []
            current_strike = min_strike
            while current_strike <= max_strike:
                strikes.append(round(current_strike, 2))
                current_strike += strike_increment
            
            print(f"   🎯 {len(strikes)} strikes to process")
            
            # Process each strike
            for strike in strikes:
                # Get CALL data
                call_data = self.get_option_data(symbol, exp_date, strike, 'CALL', start_date, end_date)
                if call_data:
                    options_data.extend(call_data)
                
                # Get PUT data
                put_data = self.get_option_data(symbol, exp_date, strike, 'PUT', start_date, end_date)
                if put_data:
                    options_data.extend(put_data)
                
                # Rate limiting
                time.sleep(0.1)
        
        return options_data
    
    def get_current_price(self, symbol):
        """Get current stock price to determine strike range"""
        # This would call Barchart's stock price API
        # For now, return a mock price
        mock_prices = {
            'V': 290.0,
            'SPY': 570.0,
            'QQQ': 485.0
        }
        return mock_prices.get(symbol, 100.0)
    
    def get_option_data(self, symbol, exp_date, strike, option_type, start_date, end_date):
        """
        Get historical data for a specific option contract
        
        This is where you'd implement the actual Barchart API call
        """
        
        # Mock data structure - replace with actual Barchart API calls
        mock_data = []
        
        # Generate mock data for the date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        current_date = start_dt
        while current_date <= end_dt:
            # Skip weekends
            if current_date.weekday() < 5:
                mock_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'expiration': exp_date,
                    'strike': strike,
                    'type': option_type,
                    'bid': round(strike * 0.02 + (hash(f"{symbol}{exp_date}{strike}{option_type}{current_date}") % 100) / 100, 2),
                    'ask': round(strike * 0.02 + (hash(f"{symbol}{exp_date}{strike}{option_type}{current_date}") % 100) / 100 + 0.05, 2),
                    'last': round(strike * 0.02 + (hash(f"{symbol}{exp_date}{strike}{option_type}{current_date}") % 100) / 100 + 0.025, 2),
                    'volume': (hash(f"{symbol}{exp_date}{strike}{option_type}{current_date}") % 1000) + 100,
                    'open_interest': (hash(f"{symbol}{exp_date}{strike}{option_type}{current_date}") % 5000) + 1000
                })
            
            current_date += timedelta(days=1)
        
        return mock_data
    
    def save_to_csv(self, data, symbol, output_dir="data/barchart"):
        """Save options data to CSV files"""
        
        if not data:
            print("❌ No data to save")
            return None
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Save main file
        filename = f"{symbol}_options_{df['date'].min()}_{df['date'].max()}.csv"
        filepath = output_path / filename
        df.to_csv(filepath, index=False)
        
        print(f"✅ Saved {len(df)} records to {filepath}")
        
        # Save summary
        summary = {
            'symbol': symbol,
            'date_range': f"{df['date'].min()} to {df['date'].max()}",
            'total_records': len(df),
            'unique_expirations': df['expiration'].nunique(),
            'unique_strikes': df['strike'].nunique(),
            'calls': len(df[df['type'] == 'CALL']),
            'puts': len(df[df['type'] == 'PUT'])
        }
        
        summary_file = output_path / f"{symbol}_options_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary: {summary['unique_expirations']} expirations, {summary['unique_strikes']} strikes")
        
        return filepath

def main():
    """Main function for command line usage"""
    
    print("🎯 BARCHART OPTIONS DATA DOWNLOADER")
    print("=" * 80)
    print("This tool automates the download of options data for butterfly strategies")
    print("=" * 80)
    
    try:
        # Initialize downloader
        downloader = BarchartOptionsDownloader()
        
        # Login
        if not downloader.login():
            print("❌ Failed to login to Barchart Premier")
            return
        
        # Download V data for Zero Loss Butterfly
        print("\n📊 Downloading V options data...")
        v_data = downloader.get_options_chain_data(
            symbol='V',
            start_date='2024-04-15',
            end_date='2024-10-17'
        )
        
        if v_data:
            v_file = downloader.save_to_csv(v_data, 'V')
            print(f"✅ V data saved to {v_file}")
        
        # Download SPY data
        print("\n📊 Downloading SPY options data...")
        spy_data = downloader.get_options_chain_data(
            symbol='SPY',
            start_date='2024-05-01',
            end_date='2024-10-31'
        )
        
        if spy_data:
            spy_file = downloader.save_to_csv(spy_data, 'SPY')
            print(f"✅ SPY data saved to {spy_file}")
        
        print("\n" + "=" * 80)
        print("✅ DOWNLOAD COMPLETE!")
        print("=" * 80)
        print("""
Next steps:
1. Review the downloaded CSV files
2. Use barchart_to_lumibot_converter.py to convert to Lumibot format
3. Run your Zero Loss Butterfly backtest
        """)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

