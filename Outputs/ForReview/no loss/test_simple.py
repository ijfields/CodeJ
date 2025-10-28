#!/usr/bin/env python3
"""
Simple diagnostic test - just check if Polygon has ANY options data for SPY in 2024
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env
project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / '.env')
os.chdir(project_root)

from lumibot.entities import Asset
from lumibot.backtesting import PolygonDataBacktesting

# Create a minimal data source
class TestDataCheck:
    def __init__(self):
        self.polygon_api_key = os.getenv("POLYGON_API_KEY")

    def check_options_data(self):
        print("Testing Polygon options data availability...")
        print(f"API Key: {self.polygon_api_key[:10]}..." if self.polygon_api_key else "NO API KEY")

        # Try to get options chains for SPY on a specific date in 2024
        test_date = datetime(2024, 7, 1)  # Mid-2024

        data_source = PolygonDataBacktesting(
            datetime(2024, 6, 1),
            datetime(2024, 7, 31),
            polygon_api_key=self.polygon_api_key,
            polygon_has_paid_subscription=False
        )

        # Try to get chains
        print(f"\nTrying to get options chains for SPY on {test_date.date()}...")

        try:
            chains = data_source.get_chains(Asset("SPY"), quote=None)

            if chains and 'Chains' in chains:
                print(f"SUCCESS: Got chains!")
                print(f"Chain keys: {chains['Chains'].keys()}")

                if 'CALL' in chains['Chains']:
                    call_chain = chains['Chains']['CALL']
                    print(f"Number of CALL expirations: {len(call_chain)}")
                    print(f"First 3 expirations: {list(call_chain.keys())[:3]}")

                if 'PUT' in chains['Chains']:
                    put_chain = chains['Chains']['PUT']
                    print(f"Number of PUT expirations: {len(put_chain)}")
            else:
                print("FAIL: No chains data returned")
                print(f"Response: {chains}")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    checker = TestDataCheck()
    checker.check_options_data()
