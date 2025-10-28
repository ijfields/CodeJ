"""
Test the actual video period: Aug 21 - Oct 17, 2025
Using Visa (V) with corrected butterfly structure
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

# Import the strategy
from no_loss_strategy import NoLossStrategy

print("=" * 70)
print("Testing VISA (V): Aug 21 - Oct 17, 2025")
print("This is the exact period from the video!")
print("=" * 70)

# Test with the video's actual period
NoLossStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2025, 8, 21),  # Recording date
    datetime(2025, 10, 17), # October expiration
    parameters={
        "symbol": "V",               # VISA
        "shares_per_position": 100,
        "dte_min": 50,               # Around 57 days (from video)
        "dte_max": 65,               # Narrow range to find Oct 17 expiry
        "max_net_debit": 40000,      # High enough for V @ ~$343
        "check_frequency": "1D",
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="V",
    show_plot=False,
    show_tearsheet=True,
    save_tearsheet=True,
    tearsheet_file="visa_aug_oct_2025_tearsheet.html"
)

print("\n" + "=" * 70)
print("Done! Check visa_aug_oct_2025_tearsheet.html")
print("=" * 70)
