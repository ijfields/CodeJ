"""
Test with Python logging configured to show console output
"""

import sys
import logging
from pathlib import Path

# Configure logging to show on console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output to console
        logging.FileHandler('debug_backtest.log')  # Also save to file
    ]
)

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

# Import the strategy
from no_loss_strategy import NoLossStrategy

print("=" * 70)
print("TEST WITH LOGGING ENABLED")
print("=" * 70)
print("Log messages should now appear below...")
print()

# Short backtest - just 3 days
NoLossStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2024, 1, 2),
    datetime(2024, 1, 5),
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
    show_plot=False,
    show_tearsheet=False,
    save_tearsheet=False
)

print()
print("=" * 70)
print("Test complete! Check debug_backtest.log for full logs")
print("=" * 70)
