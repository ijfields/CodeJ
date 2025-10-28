"""
Debug version - uses print() instead of log_message() to see what's happening
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

class DebugNoLossStrategy(Strategy):
    """Debug version with print statements"""

    parameters = {
        "symbol": "SPY",
        "shares_per_position": 100,
        "dte_min": 30,
        "dte_max": 90,
        "max_net_debit": 100,
    }

    def initialize(self):
        self.sleeptime = "1D"
        self.symbol = self.parameters.get("symbol", "SPY")
        self.dte_min = self.parameters.get("dte_min", 30)
        self.dte_max = self.parameters.get("dte_max", 90)
        print("\n" + "=" * 70)
        print(f"INITIALIZED: Symbol={self.symbol}, DTE range={self.dte_min}-{self.dte_max}")
        print("=" * 70)

    def on_trading_iteration(self):
        try:
            current_date = self.get_datetime().date()
            print(f"\n[{current_date}] === Trading Iteration Started ===")

            # Get current price
            price = self.get_last_price(self.symbol)
            print(f"[{current_date}] Current {self.symbol} price: ${price:.2f}")

            # Try to get option chains
            print(f"[{current_date}] Attempting to get option chains...")
            chains = self.get_chains(Asset(self.symbol))

            if not chains:
                print(f"[{current_date}] ERROR: No option chains available!")
                return

            print(f"[{current_date}] SUCCESS: Got option chains")

            # Get expirations
            expiries = chains.expirations("PUT")
            if not expiries:
                print(f"[{current_date}] ERROR: No expirations found!")
                return

            print(f"[{current_date}] Found {len(expiries)} expirations")
            print(f"[{current_date}] First 5 expirations: {expiries[:5]}")

            # Filter to DTE range
            today = self.get_datetime().date()
            target_expiries = [
                exp for exp in expiries
                if self.dte_min <= (exp - today).days <= self.dte_max
            ]

            if not target_expiries:
                print(f"[{current_date}] NO expirations in {self.dte_min}-{self.dte_max} DTE range")
                all_dtes = [(exp - today).days for exp in expiries[:10]]
                print(f"[{current_date}] Available DTEs (first 10): {all_dtes}")
                return

            print(f"[{current_date}] Found {len(target_expiries)} expirations in DTE range")
            target_expiry = target_expiries[0]
            dte = (target_expiry - today).days
            print(f"[{current_date}] Selected expiration: {target_expiry} ({dte} DTE)")

            # Get strikes
            strikes = sorted(chains.strikes(target_expiry))
            print(f"[{current_date}] Available strikes for {target_expiry}: {len(strikes)} strikes")
            print(f"[{current_date}] Strike range: ${strikes[0]:.2f} to ${strikes[-1]:.2f}")

            # Calculate target strikes
            put_strike = min(strikes, key=lambda s: abs(s - price))
            long_call_strike = min(strikes, key=lambda s: abs(s - price))
            short_call_strike = min(strikes, key=lambda s: abs(s - price * 1.08))

            print(f"[{current_date}] Selected strikes:")
            print(f"[{current_date}]   Put: ${put_strike:.2f}")
            print(f"[{current_date}]   Long Call: ${long_call_strike:.2f}")
            print(f"[{current_date}]   Short Call: ${short_call_strike:.2f}")

            # Try to get option prices
            put_asset = Asset(
                symbol=self.symbol,
                asset_type=Asset.AssetType.OPTION,
                expiration=target_expiry,
                strike=put_strike,
                right=Asset.OptionRight.PUT
            )

            put_price = self.get_last_price(put_asset)
            print(f"[{current_date}] Put price: ${put_price}" if put_price else f"[{current_date}] ERROR: Could not get put price!")

            print(f"[{current_date}] === End Iteration ===\n")

        except Exception as e:
            print(f"[{current_date}] EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()

print("=" * 70)
print("DEBUG TEST - Checking what data is available")
print("=" * 70)

DebugNoLossStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2024, 1, 2),
    datetime(2024, 1, 4),  # Just 2 days
    parameters={
        "symbol": "SPY",
        "dte_min": 30,
        "dte_max": 90,
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    show_plot=False,
    show_tearsheet=False,
    save_tearsheet=False
)

print("\n" + "=" * 70)
print("Debug test complete!")
print("=" * 70)
