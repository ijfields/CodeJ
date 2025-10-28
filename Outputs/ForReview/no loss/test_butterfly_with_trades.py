"""
Test the Zero Loss Butterfly Strategy with explicit trades output
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
print("=" * 70)

# Test with explicit output directory
results = ZeroLossButterfly.backtest(
    PolygonDataBacktesting,
    datetime(2025, 8, 21),
    datetime(2025, 10, 17),
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
    tearsheet_file="butterfly_detailed_tearsheet.html",
    save_logfile=True,
    logfile="butterfly_backtest.log"
)

print("\n" + "=" * 70)
print("BACKTEST RESULTS")
print("=" * 70)

if hasattr(results, 'portfolio_value'):
    print(f"Final Portfolio Value: ${results.portfolio_value:,.2f}")

if hasattr(results, 'returns'):
    print(f"Total Return: {results.returns * 100:.2f}%")

if hasattr(results, 'positions'):
    print(f"\nTotal Trades: {len(results.positions)}")
    print("\nFirst 5 Trades:")
    for i, trade in enumerate(results.positions[:5]):
        print(f"  {i+1}. {trade}")

print("\n" + "=" * 70)
print("Files generated:")
print("  - butterfly_detailed_tearsheet.html")
print("  - butterfly_backtest.log")
print("=" * 70)
