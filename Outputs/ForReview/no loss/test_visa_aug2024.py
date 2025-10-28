"""
Test with the actual dates and symbol from the video:
- Symbol: V (Visa)
- Period: July-August 2024
- When the actual trade was happening
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
print("Testing with VISA (V) - July-August 2024")
print("This is the actual period from the video!")
print("=" * 70)

# Test period from the video timeline
NoLossStrategy.backtest(
    PolygonDataBacktesting,
    datetime(2024, 7, 22),  # About a week before Aug 29 expiry
    datetime(2024, 8, 21),  # Day of video recording
    parameters={
        "symbol": "V",       # VISA (from transcript)
        "shares_per_position": 100,
        "dte_min": 30,
        "dte_max": 90,
        "max_net_debit": 35000,  # Much higher for V (~$343/share = $34,300 for 100 shares)
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="V",
    show_plot=False,
    show_tearsheet=True,
    save_tearsheet=True,
    tearsheet_file="visa_aug2024_tearsheet.html"
)

print("\nDone! Check visa_aug2024_tearsheet.html")
