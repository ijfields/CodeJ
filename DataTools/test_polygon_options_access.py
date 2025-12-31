#!/usr/bin/env python3
"""
Test script to check Polygon options data access
"""

import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to find credentials.py
sys.path.append(str(Path(__file__).parent.parent))
from credentials import POLYGON_CONFIG

def test_polygon_options_access():
    """Test what options data is available with current subscription"""
    
    print("🧪 TESTING POLYGON OPTIONS DATA ACCESS")
    print("=" * 80)
    
    api_key = POLYGON_CONFIG.get("API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Test different endpoints
    endpoints_to_test = [
        {
            "name": "Options Snapshot (Current)",
            "url": f"https://api.polygon.io/v3/snapshot/options/SPY",
            "params": {"apiKey": api_key}
        },
        {
            "name": "Options Aggregates (Historical)",
            "url": f"https://api.polygon.io/v2/aggs/ticker/O:SPY241117C00570000/range/1/day/2024-11-01/2024-11-02",
            "params": {"apiKey": api_key}
        },
        {
            "name": "Options Trades",
            "url": f"https://api.polygon.io/v3/trades/O:SPY241117C00570000",
            "params": {"apiKey": api_key, "limit": 10}
        },
        {
            "name": "Options Quotes",
            "url": f"https://api.polygon.io/v3/quotes/O:SPY241117C00570000",
            "params": {"apiKey": api_key, "limit": 10}
        }
    ]
    
    results = {}
    
    for test in endpoints_to_test:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        try:
            response = requests.get(test['url'], params=test['params'], timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'Unknown')
                results_count = len(data.get('results', []))
                
                print(f"   ✅ Success - Status: {status}, Results: {results_count}")
                
                if results_count > 0:
                    print(f"   📊 Sample data: {str(data['results'][0])[:100]}...")
                
                results[test['name']] = {
                    'status': 'success',
                    'status_code': response.status_code,
                    'data_status': status,
                    'results_count': results_count
                }
            else:
                print(f"   ❌ Failed - {response.status_code}")
                print(f"   Error: {response.text[:200]}...")
                
                results[test['name']] = {
                    'status': 'failed',
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[test['name']] = {
                'status': 'exception',
                'error': str(e)
            }
    
    # Summary
    print("\n" + "=" * 80)
    print("OPTIONS DATA ACCESS SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    total_tests = len(results)
    
    print(f"✅ Successful: {success_count}/{total_tests}")
    
    for name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {name}: {result['status']}")
    
    if success_count == 0:
        print("\n❌ NO OPTIONS DATA ACCESS")
        print("   This confirms the issue in your SUMMARY_AND_SOLUTION.md")
        print("   You need to either:")
        print("   1. Upgrade to Options Developer tier ($79/month)")
        print("   2. Use Barchart Premier data (recommended)")
        print("   3. Use ThetaData ($59/month)")
    elif success_count < total_tests:
        print("\n⚠️ PARTIAL OPTIONS DATA ACCESS")
        print("   Some endpoints work, others don't")
        print("   This suggests subscription tier limitations")
    else:
        print("\n🎉 FULL OPTIONS DATA ACCESS")
        print("   All endpoints working - check Lumibot configuration")
    
    return success_count > 0

def check_subscription_tier():
    """Try to determine what subscription tier you have"""
    
    print("\n🔍 CHECKING SUBSCRIPTION TIER")
    print("=" * 80)
    
    api_key = POLYGON_CONFIG.get("API_KEY")
    
    # Test rate limiting to determine tier
    try:
        # Free tier: 5 calls/minute
        # Paid tiers: Unlimited calls
        
        print("Testing rate limits...")
        
        # Make multiple rapid calls
        for i in range(10):
            response = requests.get(
                "https://api.polygon.io/v2/aggs/ticker/SPY/range/1/day/2024-11-01/2024-11-01",
                params={"apiKey": api_key},
                timeout=10
            )
            
            if response.status_code == 429:  # Rate limited
                print(f"   Rate limited after {i+1} calls - likely free tier")
                return "free"
            elif response.status_code != 200:
                print(f"   Error after {i+1} calls: {response.status_code}")
                return "unknown"
        
        print("   No rate limiting detected - likely paid tier")
        return "paid"
        
    except Exception as e:
        print(f"   Error testing rate limits: {e}")
        return "unknown"

def main():
    """Run all tests"""
    
    print("🎯 POLYGON OPTIONS DATA DIAGNOSTIC")
    print("=" * 80)
    
    # Test 1: Check subscription tier
    tier = check_subscription_tier()
    print(f"\n📊 Detected tier: {tier}")
    
    # Test 2: Test options data access
    options_available = test_polygon_options_access()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    if not options_available:
        print("\n💡 RECOMMENDATIONS:")
        print("1. ✅ Use Barchart Premier (you already have access)")
        print("2. 💰 Upgrade to Polygon Options Developer ($79/month)")
        print("3. 💰 Try ThetaData ($59/month)")
        print("\nThe Barchart approach is fastest and most reliable!")

if __name__ == "__main__":
    main()
