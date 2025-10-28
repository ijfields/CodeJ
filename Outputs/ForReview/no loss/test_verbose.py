"""
Quick test to see what the strategy is doing with verbose logging.
This will run just a few days and show all log messages.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

# Import the strategy
from no_loss_strategy import NoLossStrategy

print("=" * 70)
print("VERBOSE TEST - No-Loss Strategy")
print("=" * 70)
print("Running just 3 days to see what happens...")
print()

# Very short backtest - just 3 days
NoLossStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2024, 1, 2),   # Start Tuesday (markets open)
    datetime(2024, 1, 5),   # End Friday (just 3 trading days)
    parameters={
        "symbol": "SPY",
        "shares_per_position": 100,
        "dte_min": 30,
        "dte_max": 90,
        "max_net_debit": 100,
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="SPY",
    show_plot=False,        # Don't show plot for this quick test
    show_tearsheet=False,   # Don't show tearsheet
    save_tearsheet=False    # Don't save tearsheet
)

print()
print("=" * 70)
print("Test complete! Check the logs above to see what happened.")
print("=" * 70)
