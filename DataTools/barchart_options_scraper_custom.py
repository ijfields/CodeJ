#!/usr/bin/env python3
"""
Custom Barchart Options Scraper for Zero Loss Butterfly Strategy
Uses the same approach as the GitHub scraper but with better error handling
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
import urllib.parse

class BarchartOptionsScraper:
    def __init__(self, symbol):
        self.symbol = symbol.upper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_options_chain(self, expiration_date=None):
        """
        Get options chain data for a specific symbol and expiration
        """
        try:
            # Try the public API first
            url = f"https://core-api.barchart.com/v1/options/chain"
            params = {
                'symbol': self.symbol,
                'fields': 'strikePrice,lastPrice,percentFromLast,bidPrice,midpoint,askPrice,priceChange,percentChange,volatility,volume,openInterest,optionType,daysToExpiration,expirationDate,symbolCode,symbolType',
                'groupBy': 'optionType',
                'raw': '1',
                'meta': 'field.shortName,field.type,field.description'
            }
            
            if expiration_date:
                params['expirationDate'] = expiration_date
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except Exception as e:
            print(f"❌ API Error for {self.symbol}: {e}")
            return None
    
    def get_available_expirations(self):
        """
        Get all available expiration dates for the symbol
        """
        data = self.get_options_chain()
        if data and 'meta' in data and 'expirations' in data['meta']:
            return data['meta']['expirations']
        return []
    
    def get_options_dataframe(self, expiration_date=None):
        """
        Get options data as pandas DataFrame
        """
        data = self.get_options_chain(expiration_date)
        if not data or 'data' not in data:
            return None
        
        calls_data = []
        puts_data = []
        
        # Process calls
        if 'Call' in data['data']:
            for call in data['data']['Call']:
                if 'raw' in call:
                    calls_data.append(call['raw'])
        
        # Process puts
        if 'Put' in data['data']:
            for put in data['data']['Put']:
                if 'raw' in put:
                    puts_data.append(put['raw'])
        
        # Create DataFrames
        calls_df = pd.DataFrame(calls_data) if calls_data else pd.DataFrame()
        puts_df = pd.DataFrame(puts_data) if puts_data else pd.DataFrame()
        
        return calls_df, puts_df
    
    def get_all_options_data(self, save_to_csv=True):
        """
        Get all available options data for the symbol
        """
        print(f"🔍 Getting options data for {self.symbol}...")
        
        expirations = self.get_available_expirations()
        if not expirations:
            print(f"❌ No expirations found for {self.symbol}")
            return None
        
        print(f"📅 Found {len(expirations)} expiration dates")
        
        all_calls = []
        all_puts = []
        
        for i, exp in enumerate(expirations):
            print(f"📊 Processing expiration {i+1}/{len(expirations)}: {exp}")
            
            calls_df, puts_df = self.get_options_dataframe(exp)
            
            if not calls_df.empty:
                calls_df['expiration'] = exp
                calls_df['option_type'] = 'Call'
                all_calls.append(calls_df)
            
            if not puts_df.empty:
                puts_df['expiration'] = exp
                puts_df['option_type'] = 'Put'
                all_puts.append(puts_df)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Combine all data
        if all_calls or all_puts:
            combined_data = []
            if all_calls:
                combined_data.extend(all_calls)
            if all_puts:
                combined_data.extend(all_puts)
            
            final_df = pd.concat(combined_data, ignore_index=True)
            
            if save_to_csv:
                filename = f"data/barchart/{self.symbol}_options_data_{datetime.now().strftime('%Y%m%d')}.csv"
                final_df.to_csv(filename, index=False)
                print(f"💾 Saved to {filename}")
            
            return final_df
        
        return None

def main():
    """
    Test the scraper with V and SPY
    """
    symbols = ['V', 'SPY']
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"🎯 Testing {symbol} Options Data")
        print(f"{'='*50}")
        
        scraper = BarchartOptionsScraper(symbol)
        
        # Test getting expirations
        expirations = scraper.get_available_expirations()
        if expirations:
            print(f"✅ Found {len(expirations)} expirations")
            print(f"📅 First 5 expirations: {expirations[:5]}")
        else:
            print(f"❌ No expirations found for {symbol}")
            continue
        
        # Test getting options data
        options_data = scraper.get_all_options_data()
        if options_data is not None:
            print(f"✅ Successfully retrieved {len(options_data)} option contracts")
            print(f"📊 Columns: {list(options_data.columns)}")
        else:
            print(f"❌ Failed to retrieve options data for {symbol}")

if __name__ == "__main__":
    main()

