"""
Get SPY 644C and 640C option data for several days before 8/20/2025 to find when price was $1.12
"""
import requests
from datetime import datetime, timedelta
import os
from credentials import POLYGON_CONFIG

def get_spy_options_multi_days():
    """Get SPY option data for several days to find $1.12 price"""
    
    api_key = POLYGON_CONFIG.get("API_KEY")
    
    # Try different strikes and dates
    strikes = [640, 644]
    dates = [
        "2025-08-15",  # 5 days before
        "2025-08-16",  # 4 days before  
        "2025-08-17",  # 3 days before
        "2025-08-18",  # 2 days before
        "2025-08-19",  # 1 day before
        "2025-08-20",  # Same day
    ]
    
    for strike in strikes:
        print(f"\n{'='*60}")
        print(f"CHECKING SPY {strike}C OPTIONS")
        print(f"{'='*60}")
        
        for date in dates:
            print(f"\n--- {date} ---")
            
            # Try different expiration dates for this strike
            # Format: O:SPY250820C00640000 (strike * 1000)
            option_ticker = f"O:SPY{date.replace('-', '')[2:]}C{strike:06d}000"
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{option_ticker}/range/1/minute/{date}/{date}"
            
            params = {
                "adjusted": "true",
                "sort": "asc",
                "limit": 50000,
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "OK" and data.get("results"):
                    results = data["results"]
                    
                    if results:
                        # Find min/max prices
                        min_price = min(bar["l"] for bar in results)
                        max_price = max(bar["h"] for bar in results)
                        
                        # Check if price range includes $1.12
                        if min_price <= 1.12 <= max_price:
                            print(f"✅ FOUND! SPY {strike}C on {date}: ${min_price:.2f} - ${max_price:.2f}")
                            
                            # Find specific bars around $1.12
                            matches = []
                            for bar in results:
                                timestamp = datetime.fromtimestamp(bar["t"] / 1000)
                                close_price = bar["c"]
                                
                                if 1.07 <= close_price <= 1.17:
                                    matches.append({
                                        "time": timestamp,
                                        "close": close_price
                                    })
                            
                            if matches:
                                print(f"   Found {len(matches)} bars around $1.12:")
                                for match in matches[:5]:  # Show first 5
                                    print(f"   {match['time'].strftime('%H:%M:%S')} - ${match['close']:.2f}")
                        else:
                            print(f"   Range: ${min_price:.2f} - ${max_price:.2f} (no $1.12)")
                    else:
                        print(f"   No data")
                else:
                    print(f"   No data found")
            else:
                print(f"   Error: {response.status_code}")

if __name__ == "__main__":
    get_spy_options_multi_days()

