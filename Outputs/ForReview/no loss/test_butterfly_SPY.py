"""
Test Zero Loss Butterfly with SPY instead of V
SPY has the most liquid options market and should have available data

This will prove whether our strategy code works correctly when data exists.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

from zero_loss_butterfly import ZeroLossButterfly

print("=" * 70)
print("Testing Zero Loss Butterfly Strategy with SPY")
print("Symbol: SPY (S&P 500 ETF - most liquid options)")
print("Period: Nov 1 - Dec 27, 2024")
print("Testing if strategy works when options data IS available")
print("=" * 70)

# Use dates where we know SPY options data exists
ZeroLossButterfly.backtest(
    PolygonDataBacktesting,
    datetime(2024, 11, 1),  # Start from where Lumibot was running
    datetime(2024, 12, 27), # Through Dec expiry
    parameters={
        "symbol": "SPY",               # Use SPY instead of V
        "shares_per_position": 100,
        "dte_target": 45,              # ~45 days to Dec 27 from Nov 1
        "dte_min": 40,
        "dte_max": 50,
        "strike_width": 10,            # $10 wide butterfly
        "check_frequency": "1D",
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="SPY",
    show_plot=False,
    show_tearsheet=True,
    save_tearsheet=True,
    tearsheet_file="SPY_butterfly_test_tearsheet.html"
)

print("\n" + "=" * 70)
print("Done! Check:")
print("  - SPY_butterfly_test_tearsheet.html")
print("  - ZeroLossButterfly_*_trades.csv")
print("")
print("Look for:")
print("  - Did PUT order FILL (not canceled)?")
print("  - Did 2x CALL orders FILL (not canceled)?")
print("  - Did upper CALL order FILL (not canceled)?")
print("=" * 70)
