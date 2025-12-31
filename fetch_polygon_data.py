#!/usr/bin/env python3
"""
Polygon.io Data Fetcher for Forward Factor Calendar Strategy

Fetches historical options data from Polygon.io and saves it in the parquet format
expected by the backtesting system. Supports both direct API calls and MCP server integration.

Usage:
    python fetch_polygon_data.py --config backtest_config.yaml
    python fetch_polygon_data.py --tickers AAPL MSFT --start-date 2022-01-01 --end-date 2024-01-01
    python fetch_polygon_data.py --mode mcp --tickers AAPL
"""

import os
import sys
import argparse
import logging
import yaml
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import time
import json

import pandas as pd
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_polygon_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolygonDataFetcher:
    """Fetches options data from Polygon.io and saves as parquet files."""
    
    def __init__(self, api_key: str, output_dir: str = "data/mcp_parquet"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir.parent / "corporate_events").mkdir(exist_ok=True)
        
    def _make_request(self, endpoint: str, params: Dict = None, max_retries: int = 3) -> Optional[Dict]:
        """Make API request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'OK':
                    return data
                else:
                    logger.warning(f"API returned status: {data.get('status')}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed after {max_retries} attempts: {e}")
                    return None
                    
        return None
    
    def _get_trading_dates(self, start_date: str, end_date: str) -> List[date]:
        """Get list of trading dates (excludes weekends)."""
        # Handle both string and date objects
        if isinstance(start_date, date):
            start = start_date
        else:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()

        if isinstance(end_date, date):
            end = end_date
        else:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        trading_dates = []
        current = start
        
        while current <= end:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                trading_dates.append(current)
            current += timedelta(days=1)
            
        return trading_dates
    
    def fetch_options_snapshot(self, ticker: str, date: date) -> Optional[pd.DataFrame]:
        """Fetch options snapshot for a specific ticker and date."""
        date_str = date.strftime('%Y-%m-%d')
        endpoint = f"/v3/snapshot/options/{ticker.upper()}"
        params = {'date': date_str}
        
        logger.info(f"Fetching options snapshot for {ticker} on {date_str}")
        data = self._make_request(endpoint, params)
        
        if not data or 'results' not in data:
            logger.warning(f"No options data found for {ticker} on {date_str}")
            return None
            
        options = data['results']
        if not options:
            logger.warning(f"Empty options data for {ticker} on {date_str}")
            return None
            
        # Transform to required schema
        records = []
        for option in options:
            # Extract details from the option contract
            details = option.get('details', {})
            last_quote = option.get('last_quote', {})
            
            # Skip if no pricing data
            if not last_quote:
                continue
                
            records.append({
                'timestamp': pd.to_datetime(date_str),
                'expiry': pd.to_datetime(details.get('expiration_date', '')).date(),
                'strike': float(details.get('strike_price', 0)),
                'option_type': details.get('contract_type', '').lower(),
                'bid': float(last_quote.get('bid', 0)),
                'ask': float(last_quote.get('ask', 0)),
                'mid': (float(last_quote.get('bid', 0)) + float(last_quote.get('ask', 0))) / 2,
                'implied_vol': float(last_quote.get('implied_volatility', 0)),
                'delta': float(last_quote.get('greeks', {}).get('delta', 0)),
                'volume': int(last_quote.get('volume', 0)),
                'open_interest': int(last_quote.get('open_interest', 0))
            })
            
        if not records:
            logger.warning(f"No valid options records for {ticker} on {date_str}")
            return None
            
        df = pd.DataFrame(records)
        
        # Filter for liquid options (volume > 0 or open_interest > 0)
        df = df[(df['volume'] > 0) | (df['open_interest'] > 0)]
        
        if df.empty:
            logger.warning(f"No liquid options for {ticker} on {date_str}")
            return None
            
        return df
    
    def fetch_earnings_calendar(self, tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch earnings calendar for given tickers and date range."""
        logger.info(f"Fetching earnings calendar for {tickers}")
        
        earnings_data = []
        
        for ticker in tickers:
            endpoint = f"/v2/reference/financials"
            params = {
                'ticker': ticker.upper(),
                'timeframe': 'quarterly',
                'limit': 50
            }
            
            data = self._make_request(endpoint, params)
            if not data or 'results' not in data:
                logger.warning(f"No earnings data found for {ticker}")
                continue
                
            for result in data['results']:
                earnings_date = result.get('reporting_date')
                if earnings_date:
                    # Parse and check if within date range
                    try:
                        earnings_date_obj = datetime.strptime(earnings_date, '%Y-%m-%d').date()

                        # Handle both string and date objects
                        if isinstance(start_date, date):
                            start_obj = start_date
                        else:
                            start_obj = datetime.strptime(start_date, '%Y-%m-%d').date()

                        if isinstance(end_date, date):
                            end_obj = end_date
                        else:
                            end_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                        
                        if start_obj <= earnings_date_obj <= end_obj:
                            earnings_data.append({
                                'ticker': ticker.upper(),
                                'date': earnings_date,
                                'time': 'BMO'  # Default assumption
                            })
                    except ValueError:
                        logger.warning(f"Invalid earnings date format for {ticker}: {earnings_date}")
                        continue
                        
        return pd.DataFrame(earnings_data)
    
    def save_parquet(self, df: pd.DataFrame, ticker: str, date: date) -> bool:
        """Save DataFrame as parquet file."""
        ticker_dir = self.output_dir / ticker.upper()
        ticker_dir.mkdir(exist_ok=True)
        
        filename = f"{ticker.upper()}_{date.strftime('%Y-%m-%d')}.parquet"
        filepath = ticker_dir / filename
        
        try:
            df.to_parquet(filepath, index=False)
            logger.info(f"Saved {len(df)} options to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save parquet file {filepath}: {e}")
            return False
    
    def fetch_ticker_data(self, ticker: str, start_date: str, end_date: str, 
                         skip_existing: bool = True) -> Dict[str, int]:
        """Fetch all options data for a ticker within date range."""
        trading_dates = self._get_trading_dates(start_date, end_date)
        
        stats = {'total_dates': len(trading_dates), 'successful': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Fetching data for {ticker} across {len(trading_dates)} trading days")
        
        for trade_date in tqdm(trading_dates, desc=f"Fetching {ticker}"):
            # Check if file already exists
            if skip_existing:
                ticker_dir = self.output_dir / ticker.upper()
                filename = f"{ticker.upper()}_{trade_date.strftime('%Y-%m-%d')}.parquet"
                if (ticker_dir / filename).exists():
                    stats['skipped'] += 1
                    continue
            
            # Fetch options snapshot
            df = self.fetch_options_snapshot(ticker, trade_date)
            
            if df is not None and not df.empty:
                if self.save_parquet(df, ticker, trade_date):
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1
            else:
                stats['failed'] += 1
                
            # Rate limiting - be respectful to API
            time.sleep(0.1)
            
        return stats
    
    def fetch_all_data(self, tickers: List[str], start_date: str, end_date: str, 
                      skip_existing: bool = True) -> Dict[str, Dict[str, int]]:
        """Fetch options data for all tickers."""
        all_stats = {}
        
        # Fetch options data for each ticker
        for ticker in tickers:
            logger.info(f"Starting data fetch for {ticker}")
            stats = self.fetch_ticker_data(ticker, start_date, end_date, skip_existing)
            all_stats[ticker] = stats
            
            # Summary for this ticker
            logger.info(f"{ticker} Summary: {stats['successful']}/{stats['total_dates']} successful, "
                       f"{stats['skipped']} skipped, {stats['failed']} failed")
        
        # Fetch earnings calendar
        logger.info("Fetching earnings calendar...")
        earnings_df = self.fetch_earnings_calendar(tickers, start_date, end_date)
        
        if not earnings_df.empty:
            earnings_path = self.output_dir.parent / "corporate_events" / "earnings_calendar.csv"
            earnings_df.to_csv(earnings_path, index=False)
            logger.info(f"Saved earnings calendar with {len(earnings_df)} entries to {earnings_path}")
        else:
            logger.warning("No earnings data found")
            
        return all_stats

def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='Fetch Polygon.io options data for backtesting')
    parser.add_argument('--config', type=str, help='Path to config file (backtest_config.yaml)')
    parser.add_argument('--tickers', nargs='+', help='Tickers to fetch (e.g., AAPL MSFT)')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output-dir', type=str, default='data/mcp_parquet', 
                       help='Output directory for parquet files')
    parser.add_argument('--mode', choices=['api', 'mcp'], default='api',
                       help='Data fetching mode (api or mcp)')
    parser.add_argument('--no-skip', action='store_true', 
                       help='Don\'t skip existing files (re-download)')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
        tickers = config.get('universe', ['AAPL', 'MSFT', 'TSLA', 'QQQ'])
        start_date = config.get('start_date', '2022-01-01')
        end_date = config.get('end_date', '2024-01-01')
    else:
        tickers = args.tickers or ['AAPL', 'MSFT', 'TSLA', 'QQQ']
        start_date = args.start_date or '2022-01-01'
        end_date = args.end_date or '2024-01-01'
    
    # Get API key
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        logger.error("POLYGON_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize fetcher
    fetcher = PolygonDataFetcher(api_key, args.output_dir)
    
    # Fetch data
    logger.info(f"Starting data fetch for {tickers} from {start_date} to {end_date}")
    logger.info(f"Mode: {args.mode}, Output: {args.output_dir}")
    
    start_time = time.time()
    stats = fetcher.fetch_all_data(tickers, start_date, end_date, not args.no_skip)
    end_time = time.time()
    
    # Print summary
    logger.info("=" * 60)
    logger.info("FETCH SUMMARY")
    logger.info("=" * 60)
    
    total_successful = 0
    total_failed = 0
    total_skipped = 0
    
    for ticker, ticker_stats in stats.items():
        logger.info(f"{ticker}: {ticker_stats['successful']} successful, "
                   f"{ticker_stats['skipped']} skipped, {ticker_stats['failed']} failed")
        total_successful += ticker_stats['successful']
        total_skipped += ticker_stats['skipped']
        total_failed += ticker_stats['failed']
    
    logger.info(f"Total: {total_successful} successful, {total_skipped} skipped, {total_failed} failed")
    logger.info(f"Time elapsed: {end_time - start_time:.1f} seconds")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()



