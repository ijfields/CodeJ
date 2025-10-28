#!/usr/bin/env python3
"""
Simple test of PandasOptionsDataSource with Zero Loss Butterfly

Direct integration test - no complex backtesting framework, just verify:
1. Data source loads correctly
2. Strategy can get chains
3. Strategy can get prices
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date
from dotenv import load_dotenv

# Setup paths
project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / '.env')
os.chdir(project_root)

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(project_root))

from DataTools.pandas_options_data_source import PandasOptionsDataSource
from lumibot.entities import Asset

def main():
    print("="*70)
    print("SIMPLE DATA SOURCE TEST")
    print("="*70)
    print()

    # Test 1: Load data source
    print("Test 1: Loading PandasOptionsDataSource...")
    try:
        data_source = PandasOptionsDataSource(data_dir="data/lumibot")
        print("[OK] Data source loaded successfully")
        print()
    except Exception as e:
        print(f"[FAIL] Failed to load data source: {e}")
        return

    # Test 2: Get options chains for SPY
    print("Test 2: Getting options chains for SPY...")
    try:
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        chains = data_source.get_chains(spy_asset)

        if chains:
            print(f"[OK] Got chains with {len(chains)} expirations")

            # Show first few expirations
            expirations = sorted(chains.keys())
            print(f"\nAvailable expirations (first 5):")
            for exp_date in expirations[:5]:
                num_strikes = len(chains[exp_date])
                print(f"  {exp_date}: {num_strikes} strikes")

                # Show sample strikes for first expiration
                if exp_date == expirations[0]:
                    strikes = sorted(chains[exp_date].keys())
                    print(f"    Sample strikes: {strikes[:5]}")

                    # Show sample contract data
                    first_strike = strikes[0]
                    contract_types = list(chains[exp_date][first_strike].keys())
                    print(f"    Contract types at strike {first_strike}: {contract_types}")

                    if 'CALL' in chains[exp_date][first_strike]:
                        call_data = chains[exp_date][first_strike]['CALL']
                        print(f"    Sample CALL data: strike={call_data['strike']}, last_price={call_data['last_price']}")
        else:
            print("[FAIL] No chains data returned")
            return
        print()
    except Exception as e:
        print(f"[FAIL] Error getting chains: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 3: Get stock price
    print("Test 3: Getting last price for SPY...")
    try:
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        last_price = data_source.get_last_price(spy_asset)

        if last_price:
            print(f"[OK] Last price: ${last_price:.2f}")
        else:
            print("[FAIL] No price returned")
            return
        print()
    except Exception as e:
        print(f"[FAIL] Error getting last price: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 4: Get historical prices
    print("Test 4: Getting historical prices for SPY...")
    try:
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        historical = data_source.get_historical_prices(spy_asset, length=10, timestep="1D")

        if historical is not None and not historical.empty:
            print(f"[OK] Got {len(historical)} historical prices")
            print(f"    Date range: {historical.index[0]} to {historical.index[-1]}")
            print(f"    Latest close: ${historical['close'].iloc[-1]:.2f}")
        else:
            print("[FAIL] No historical data returned")
            return
        print()
    except Exception as e:
        print(f"[FAIL] Error getting historical prices: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test 5: Simulate what Zero Loss Butterfly needs
    print("Test 5: Simulating Zero Loss Butterfly requirements...")
    try:
        # The strategy needs to:
        # 1. Get current stock price
        stock_price = data_source.get_last_price(Asset("SPY"))
        print(f"  Current SPY price: ${stock_price:.2f}")

        # 2. Find options with ~57 DTE
        target_dte = 57
        chains = data_source.get_chains(Asset("SPY"))
        current_date = date.today()

        suitable_expirations = []
        for exp_date in chains.keys():
            dte = (exp_date - current_date).days
            if 50 <= dte <= 65:  # DTE range 50-65
                suitable_expirations.append((exp_date, dte))

        if suitable_expirations:
            suitable_expirations.sort(key=lambda x: abs(x[1] - target_dte))
            best_exp, best_dte = suitable_expirations[0]
            print(f"  Best expiration: {best_exp} ({best_dte} DTE)")

            # 3. Find strikes for butterfly
            strikes = sorted(chains[best_exp].keys())
            print(f"  Available strikes: {len(strikes)} (from ${min(strikes):.0f} to ${max(strikes):.0f})")

            # Calculate butterfly strikes (simplified)
            # PUT: $10 below stock
            # Center CALL: $5 below stock
            # Upper CALL: $5 above center
            put_target = stock_price - 10
            center_target = stock_price - 5
            upper_target = center_target + 10

            # Find closest strikes
            put_strike = min(strikes, key=lambda x: abs(x - put_target))
            center_strike = min(strikes, key=lambda x: abs(x - center_target))
            upper_strike = min(strikes, key=lambda x: abs(x - upper_target))

            print(f"  Butterfly strikes:")
            print(f"    PUT: ${put_strike:.0f}")
            print(f"    Center CALL: ${center_strike:.0f}")
            print(f"    Upper CALL: ${upper_strike:.0f}")

            # Check if we have data for these contracts
            if put_strike in chains[best_exp] and 'PUT' in chains[best_exp][put_strike]:
                put_contract = chains[best_exp][put_strike]['PUT']
                print(f"    PUT contract: last_price=${put_contract['last_price']:.2f}")

            if center_strike in chains[best_exp] and 'CALL' in chains[best_exp][center_strike]:
                center_contract = chains[best_exp][center_strike]['CALL']
                print(f"    Center CALL contract: last_price=${center_contract['last_price']:.2f}")

            if upper_strike in chains[best_exp] and 'CALL' in chains[best_exp][upper_strike]:
                upper_contract = chains[best_exp][upper_strike]['CALL']
                print(f"    Upper CALL contract: last_price=${upper_contract['last_price']:.2f}")

            print(f"\n[OK] All requirements for Zero Loss Butterfly are available!")
        else:
            print(f"[WARN] No expirations found in DTE range 50-65")
            print(f"  Available expirations:")
            all_exp = sorted(chains.keys())
            for exp in all_exp[:5]:
                dte = (exp - current_date).days
                print(f"    {exp}: {dte} DTE")

        print()
    except Exception as e:
        print(f"[FAIL] Error simulating butterfly requirements: {e}")
        import traceback
        traceback.print_exc()
        return

    print("="*70)
    print("ALL TESTS PASSED - Data source ready for use!")
    print("="*70)
    print()
    print("Next step: Integrate with Zero Loss Butterfly strategy")
    print()


if __name__ == "__main__":
    main()
