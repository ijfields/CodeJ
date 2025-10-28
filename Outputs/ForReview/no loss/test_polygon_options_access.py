#!/usr/bin/env python3
"""
Test Polygon.io Options Starter Plan Access

Verifies that your paid Polygon plan can retrieve historical options data.
Tests the exact data the Zero Loss Butterfly strategy needs.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / '.env')

def test_polygon_access():
    """Test Polygon.io options data access"""

    api_key = os.getenv('POLYGON_API_KEY')

    print("="*70)
    print("POLYGON.IO OPTIONS STARTER PLAN TEST")
    print("="*70)
    print()

    if not api_key:
        print("[FAIL] No POLYGON_API_KEY found in .env file")
        return False

    print(f"[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"     Length: {len(api_key)} characters")
    print()

    # Test with polygon-api-client library
    try:
        from polygon import RESTClient
        print("[OK] polygon-api-client library installed")
    except ImportError:
        print("[FAIL] polygon-api-client not installed")
        print("       Install with: pip install polygon-api-client")
        return False

    print()
    print("-"*70)
    print("TEST 1: Account Status & Plan Features")
    print("-"*70)

    try:
        client = RESTClient(api_key)

        # Get a recent date (within 2 years for Options Starter plan)
        test_date = date(2024, 10, 1)  # October 1, 2024

        print(f"\nTesting data access for: {test_date}")
        print()

    except Exception as e:
        print(f"[FAIL] Error connecting to Polygon: {e}")
        return False

    print("-"*70)
    print("TEST 2: Historical Options Chain Data")
    print("-"*70)
    print()

    try:
        # Test: Get options chain for SPY
        print("Requesting options contracts for SPY...")

        contracts = client.list_options_contracts(
            underlying_ticker="SPY",
            contract_type="call",
            expiration_date_gte=test_date,
            expiration_date_lte=test_date + timedelta(days=90),
            limit=10
        )

        contract_list = list(contracts)

        if len(contract_list) > 0:
            print(f"[OK] Retrieved {len(contract_list)} SPY options contracts")
            print("\nSample contracts:")
            for i, contract in enumerate(contract_list[:3]):
                print(f"  {i+1}. {contract.ticker}")
                print(f"     Strike: ${contract.strike_price}")
                print(f"     Expiration: {contract.expiration_date}")
            print()
        else:
            print("[FAIL] No options contracts found")
            print("      This suggests data access issue")
            return False

    except Exception as e:
        print(f"[FAIL] Error retrieving options contracts: {e}")
        print(f"      Error type: {type(e).__name__}")
        return False

    print("-"*70)
    print("TEST 3: Historical Options Pricing (OHLC)")
    print("-"*70)
    print()

    try:
        # Get a specific option contract
        test_contract = contract_list[0]
        test_ticker = test_contract.ticker

        print(f"Testing pricing data for: {test_ticker}")
        print(f"Date range: {test_date} to {test_date + timedelta(days=5)}")
        print()

        # Request daily bars (aggregates)
        bars = client.get_aggs(
            ticker=test_ticker,
            multiplier=1,
            timespan="day",
            from_=test_date.strftime("%Y-%m-%d"),
            to_=(test_date + timedelta(days=5)).strftime("%Y-%m-%d"),
        )

        bar_list = list(bars)

        if len(bar_list) > 0:
            print(f"[OK] Retrieved {len(bar_list)} price bars")
            print("\nSample data:")
            for bar in bar_list[:3]:
                bar_date = datetime.fromtimestamp(bar.timestamp / 1000).strftime("%Y-%m-%d")
                print(f"  {bar_date}: O=${bar.open:.2f} H=${bar.high:.2f} L=${bar.low:.2f} C=${bar.close:.2f} V={bar.volume}")
            print()
            print("[SUCCESS] Historical options OHLC data is available!")
            print("         This is what backtesting needs!")
        else:
            print("[WARN] No price bars found for this contract")
            print("       This might mean:")
            print("       - Contract wasn't actively traded")
            print("       - Data not available for this specific date")
            print("       Try a more recent date or different contract")

    except Exception as e:
        print(f"[FAIL] Error retrieving price data: {e}")
        print(f"      Error type: {type(e).__name__}")

        if "forbidden" in str(e).lower() or "401" in str(e) or "403" in str(e):
            print()
            print("*** AUTHENTICATION ERROR ***")
            print("This suggests your API key might be:")
            print("  - For the FREE tier (not Options Starter)")
            print("  - Expired or invalid")
            print("  - Not activated for options data")
            print()
            print("Action: Verify your subscription at polygon.io/dashboard")
            return False

    print()
    print("="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    print()
    print("Your Polygon Options Starter Plan should provide:")
    print("  - 2 years of historical options data")
    print("  - All US options tickers")
    print("  - Greeks, IV, Open Interest")
    print("  - Unlimited API calls")
    print()

    if len(bar_list) > 0:
        print("[SUCCESS] Your paid plan is working correctly!")
        print()
        print("CONCLUSION:")
        print("  The 72% canceled orders in previous backtest were likely due to:")
        print("  1. Lumibot requesting data incorrectly")
        print("  2. Specific strikes/expirations not existing")
        print("  3. Framework integration issues")
        print()
        print("  Your Polygon data IS available - just need proper integration!")
        return True
    else:
        print("[INCONCLUSIVE] Could retrieve contracts but not pricing")
        print()
        print("Next steps:")
        print("  1. Verify subscription is active: polygon.io/dashboard")
        print("  2. Try more recent dates (last 30 days)")
        print("  3. Check if specific plan covers historical aggregates")
        return False

if __name__ == "__main__":
    import sys
    success = test_polygon_access()
    sys.exit(0 if success else 1)
