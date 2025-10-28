"""
Quick diagnostic: Check what options data is actually available for V in Aug-Oct 2025
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.strategies import Strategy
from lumibot.entities import Asset
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

class DataCheckStrategy(Strategy):
    """Simple strategy to check what data is available"""

    parameters = {"symbol": "V"}

    def initialize(self):
        self.sleeptime = "1D"
        self.symbol = self.parameters.get("symbol", "V")
        self.checked = False

    def on_trading_iteration(self):
        if self.checked:
            return

        self.checked = True
        current_date = self.get_datetime().date()

        print("\n" + "=" * 70)
        print(f"DATA CHECK on {current_date}")
        print("=" * 70)

        # Get current price
        price = self.get_last_price(self.symbol)
        print(f"\n1. Current {self.symbol} price: ${price:.2f}")

        # Get option chains
        print(f"\n2. Fetching option chains for {self.symbol}...")
        chains_dict = self.get_chains(Asset(self.symbol))

        if not chains_dict or 'Chains' not in chains_dict:
            print("   ERROR: No option chains available!")
            return

        print("   SUCCESS: Got option chains")

        chains = chains_dict['Chains']

        # Check PUT options
        if 'PUT' in chains:
            put_chains = chains['PUT']
            put_expirations = sorted(list(put_chains.keys()))
            print(f"\n3. PUT Options Available:")
            print(f"   Total expirations: {len(put_expirations)}")
            print(f"   First 10 expirations: {put_expirations[:10]}")

            # Calculate DTEs for first 10
            from datetime import datetime as dt
            today = current_date
            print(f"\n   DTEs (Days to Expiration) for first 10:")
            for exp_str in put_expirations[:10]:
                exp_date = dt.strptime(exp_str, '%Y-%m-%d').date()
                dte = (exp_date - today).days
                print(f"      {exp_str}: {dte} DTE")

            # Check if Oct 17, 2025 exists
            target_exp = "2025-10-17"
            if target_exp in put_chains:
                exp_date = dt.strptime(target_exp, '%Y-%m-%d').date()
                dte = (exp_date - today).days
                print(f"\n   ✓ TARGET FOUND: {target_exp} ({dte} DTE)")

                # Get strikes for Oct 17
                strikes = sorted([float(s) for s in put_chains[target_exp].keys()])
                print(f"   Available strikes: {len(strikes)} total")
                print(f"   Strike range: ${strikes[0]:.0f} to ${strikes[-1]:.0f}")
                print(f"   First 10 strikes: {[f'${s:.0f}' for s in strikes[:10]]}")
                print(f"   Around current price (${price:.0f}): {[f'${s:.0f}' for s in strikes if abs(s - price) < 20]}")
            else:
                print(f"\n   ✗ TARGET NOT FOUND: {target_exp}")
                print(f"   Available expirations in Oct 2025:")
                oct_exps = [e for e in put_expirations if e.startswith('2025-10')]
                print(f"      {oct_exps}")

        # Check CALL options
        if 'CALL' in chains:
            call_chains = chains['CALL']
            call_expirations = sorted(list(call_chains.keys()))
            print(f"\n4. CALL Options Available:")
            print(f"   Total expirations: {len(call_expirations)}")

            # Check Oct 17 calls
            target_exp = "2025-10-17"
            if target_exp in call_chains:
                print(f"   ✓ Oct 17, 2025 CALLS exist")
                strikes = sorted([float(s) for s in call_chains[target_exp].keys()])
                print(f"   Available strikes: {len(strikes)} total")
            else:
                print(f"   ✗ Oct 17, 2025 CALLS NOT found")

        print("\n" + "=" * 70)
        print("DATA CHECK COMPLETE")
        print("=" * 70 + "\n")

print("=" * 70)
print("CHECKING OPTIONS DATA AVAILABILITY")
print("Symbol: V (Visa)")
print("Period: Aug 21 - Oct 17, 2025")
print("=" * 70)

DataCheckStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2025, 8, 21),  # Just check one day
    datetime(2025, 8, 22),
    parameters={"symbol": "V"},
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    show_plot=False,
    show_tearsheet=False,
    save_tearsheet=False
)
