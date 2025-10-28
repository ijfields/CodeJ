"""
Test with 2024 dates - maybe the video was from 2024, not 2025?
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
print("Testing Zero Loss Butterfly Strategy")
print("Symbol: V (Visa)")
print("Period: Aug 21 - Oct 17, 2024 (trying 2024 instead)")
print("=" * 70)

ZeroLossButterfly.backtest(
    PolygonDataBacktesting,
    datetime(2024, 8, 21),  # Use 2024!
    datetime(2024, 10, 17),
    parameters={
        "symbol": "V",
        "shares_per_position": 100,
        "dte_target": 57,
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,
        "check_frequency": "1D",
    },
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    benchmark_asset="V",
    show_plot=False,
    show_tearsheet=True,
    save_tearsheet=True,
    tearsheet_file="butterfly_2024_correct_tearsheet.html"
)

print("\n" + "=" * 70)
print("Done! Check butterfly_2024_correct_tearsheet.html")
print("=" * 70)
