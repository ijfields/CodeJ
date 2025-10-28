"""
Test the Zero Loss Butterfly Strategy - Aug 21 to Oct 17, 2025
Using Visa (V) with corrected butterfly structure (sell 2 calls at center!)
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime

# Import the corrected butterfly strategy
from zero_loss_butterfly import ZeroLossButterfly

print("=" * 70)
print("Testing Zero Loss Butterfly Strategy")
print("Symbol: V (Visa)")
print("Period: Aug 21 - Oct 17, 2025")
print("This is the corrected strategy with 2 short calls at center!")
print("=" * 70)

# Test with the video's actual period
ZeroLossButterfly.backtest(
    PolygonDataBacktesting,
    datetime(2025, 8, 21),  # Recording date from video
    datetime(2025, 10, 17), # October expiration from video
    parameters={
        "symbol": "V",               # VISA from video
        "shares_per_position": 100,
        "dte_target": 57,            # Exactly from video
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,          # $10 wide from video
        "check_frequency": "1D",
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="V",
    show_plot=False,
    show_tearsheet=True,
    save_tearsheet=True,
    tearsheet_file="zero_loss_butterfly_tearsheet.html"
)

print("\n" + "=" * 70)
print("Done! Check zero_loss_butterfly_tearsheet.html")
print("=" * 70)
