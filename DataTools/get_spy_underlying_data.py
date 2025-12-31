"""
Get SPY underlying price data for 8/20/2025 to see price action around 644
"""
import requests
from datetime import datetime
import os
from credentials import POLYGON_CONFIG

def get_spy_underlying_data():
    """Get SPY underlying price data for 8/20/2025"""
    
    api_key = POLYGON_CONFIG.get("API_KEY")
    
    # Get minute bars for SPY on 8/20/2025
    url = f"https://api.polygon.io/v2/aggs/ticker/SPY/range/1/minute/2025-08-20/2025-08-20"
    
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }
    
    print(f"Fetching SPY underlying data for 8/20/2025...")
    print(f"URL: {url}")
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == "OK" and data.get("results"):
            results = data["results"]
            print(f"\nFound {len(results)} minute bars for SPY on 8/20/2025")
            print("\nTime                      Open    High    Low     Close   Volume")
            print("=" * 75)
            
            # Find when price was around 644
            matches_644 = []
            for bar in results:
                timestamp = datetime.fromtimestamp(bar["t"] / 1000)
                open_price = bar["o"]
                high_price = bar["h"]
                low_price = bar["l"]
                close_price = bar["c"]
                volume = bar["v"]
                
                # Check if price was around 644 (within $2)
                if 642 <= close_price <= 646:
                    matches_644.append({
                        "time": timestamp,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "volume": volume
                    })
                    print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}  ${open_price:.2f}  ${high_price:.2f}  ${low_price:.2f}  ${close_price:.2f}  {volume:,}")
            
            if matches_644:
                print(f"\n\nFound {len(matches_644)} bars where SPY was around $644")
                print("\nFirst occurrence:")
                first = matches_644[0]
                print(f"Time: {first['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Price: ${first['close']:.2f}")
                
                print("\nLast occurrence:")
                last = matches_644[-1]
                print(f"Time: {last['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Price: ${last['close']:.2f}")
            else:
                print("\n\nNo bars found with SPY around $644")
                print("Showing price range for the day:")
                
                # Find min/max prices
                min_price = min(bar["l"] for bar in results)
                max_price = max(bar["h"] for bar in results)
                print(f"SPY range on 8/20/2025: ${min_price:.2f} - ${max_price:.2f}")
                
                # Show first 20 bars
                print("\nFirst 20 bars:")
                for bar in results[:20]:
                    timestamp = datetime.fromtimestamp(bar["t"] / 1000)
                    print(f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}  ${bar['o']:.2f}  ${bar['h']:.2f}  ${bar['l']:.2f}  ${bar['c']:.2f}  {bar['v']:,}")
        else:
            print(f"\nNo data found. Response: {data}")
    else:
        print(f"\nError: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_spy_underlying_data()

