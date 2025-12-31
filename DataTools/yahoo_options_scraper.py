#!/usr/bin/env python3
"""
Yahoo Finance Options Scraper for Zero Loss Butterfly Strategy
Free alternative to Barchart
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class YahooOptionsScraper:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.ticker = yf.Ticker(symbol)
    
    def get_options_chain(self, expiration_date=None):
        """
        Get options chain data from Yahoo Finance
        """
        try:
            # Get all available expiration dates
            expirations = self.ticker.options
            if not expirations:
                print(f"❌ No options found for {self.symbol}")
                return None, None
            
            print(f"📅 Found {len(expirations)} expiration dates for {self.symbol}")
            
            if expiration_date:
                if expiration_date in expirations:
                    expirations = [expiration_date]
                else:
                    print(f"❌ Expiration {expiration_date} not found")
                    return None, None
            
            all_calls = []
            all_puts = []
            
            for i, exp in enumerate(expirations):
                print(f"📊 Processing expiration {i+1}/{len(expirations)}: {exp}")
                
                try:
                    # Get options chain for this expiration
                    options_chain = self.ticker.option_chain(exp)
                    
                    if options_chain.calls is not None and not options_chain.calls.empty:
                        calls_df = options_chain.calls.copy()
                        calls_df['expiration'] = exp
                        calls_df['option_type'] = 'Call'
                        calls_df['symbol'] = self.symbol
                        all_calls.append(calls_df)
                    
                    if options_chain.puts is not None and not options_chain.puts.empty:
                        puts_df = options_chain.puts.copy()
                        puts_df['expiration'] = exp
                        puts_df['option_type'] = 'Put'
                        puts_df['symbol'] = self.symbol
                        all_puts.append(puts_df)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️ Error processing {exp}: {e}")
                    continue
            
            # Combine all data
            combined_data = []
            if all_calls:
                combined_data.extend(all_calls)
            if all_puts:
                combined_data.extend(all_puts)
            
            if combined_data:
                final_df = pd.concat(combined_data, ignore_index=True)
                return final_df, expirations
            else:
                return None, None
                
        except Exception as e:
            print(f"❌ Error getting options data for {self.symbol}: {e}")
            return None, None
    
    def get_filtered_options(self, days_to_expiry_min=40, days_to_expiry_max=70, 
                           strike_range_pct=0.20, current_price=None):
        """
        Get filtered options data for Zero Loss Butterfly strategy
        """
        options_data, expirations = self.get_options_chain()
        
        if options_data is None or options_data.empty:
            return None
        
        # Get current stock price if not provided
        if current_price is None:
            try:
                hist = self.ticker.history(period="1d")
                current_price = hist['Close'].iloc[-1]
            except:
                print(f"❌ Could not get current price for {self.symbol}")
                return None
        
        print(f"💰 Current {self.symbol} price: ${current_price:.2f}")
        
        # Calculate date range for DTE filtering
        today = datetime.now().date()
        min_date = today + timedelta(days=days_to_expiry_min)
        max_date = today + timedelta(days=days_to_expiry_max)
        
        # Filter by expiration date (DTE)
        options_data['expiration_date'] = pd.to_datetime(options_data['expiration'])
        options_data['days_to_expiry'] = (options_data['expiration_date'].dt.date - today).apply(lambda x: x.days)
        
        filtered_data = options_data[
            (options_data['days_to_expiry'] >= days_to_expiry_min) &
            (options_data['days_to_expiry'] <= days_to_expiry_max)
        ]
        
        if filtered_data.empty:
            print(f"❌ No options found in DTE range {days_to_expiry_min}-{days_to_expiry_max}")
            return None
        
        # Filter by strike price range
        strike_min = current_price * (1 - strike_range_pct)
        strike_max = current_price * (1 + strike_range_pct)
        
        filtered_data = filtered_data[
            (filtered_data['strike'] >= strike_min) &
            (filtered_data['strike'] <= strike_max)
        ]
        
        if filtered_data.empty:
            print(f"❌ No options found in strike range ${strike_min:.2f}-${strike_max:.2f}")
            return None
        
        print(f"✅ Found {len(filtered_data)} options in range")
        print(f"📊 Strike range: ${filtered_data['strike'].min():.2f} - ${filtered_data['strike'].max():.2f}")
        print(f"📅 DTE range: {filtered_data['days_to_expiry'].min()} - {filtered_data['days_to_expiry'].max()} days")
        
        return filtered_data

def main():
    """
    Test the Yahoo Finance scraper
    """
    symbols = ['V', 'SPY']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"🎯 Testing {symbol} Options Data (Yahoo Finance)")
        print(f"{'='*60}")
        
        scraper = YahooOptionsScraper(symbol)
        
        # Get filtered options data for Zero Loss Butterfly
        options_data = scraper.get_filtered_options(
            days_to_expiry_min=40,
            days_to_expiry_max=70,
            strike_range_pct=0.20
        )
        
        if options_data is not None:
            # Save to CSV
            filename = f"data/barchart/{symbol}_options_yahoo_{datetime.now().strftime('%Y%m%d')}.csv"
            options_data.to_csv(filename, index=False)
            print(f"💾 Saved to {filename}")
            
            # Show sample data
            print(f"\n📊 Sample data:")
            print(options_data[['symbol', 'expiration', 'strike', 'option_type', 'lastPrice', 'volume', 'openInterest', 'days_to_expiry']].head(10))
        else:
            print(f"❌ Failed to get options data for {symbol}")

if __name__ == "__main__":
    main()
