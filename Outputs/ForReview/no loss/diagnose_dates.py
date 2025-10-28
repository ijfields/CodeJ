"""
Diagnose why backtest shows wrong dates
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from credentials import POLYGON_CONFIG
from lumibot.backtesting import PolygonDataBacktesting
from lumibot.strategies import Strategy
from datetime import datetime

class DateDiagnostic(Strategy):
    """Simple strategy to check what date the backtest thinks it is"""

    def initialize(self):
        self.sleeptime = "1D"
        self.iterations = 0

    def on_trading_iteration(self):
        self.iterations += 1
        current_dt = self.get_datetime()

        print(f"\n{'='*50}")
        print(f"Iteration #{self.iterations}")
        print(f"get_datetime() returns: {current_dt}")
        print(f"  Date: {current_dt.date()}")
        print(f"  Type: {type(current_dt)}")
        print(f"{'='*50}\n")

        if self.iterations >= 3:
            # Stop after 3 iterations
            return

print("Testing date handling in Lumibot backtest")
print("Expected: Aug 21 - Oct 17, 2025")
print("-" * 50)

DateDiagnostic.backtest(
    PolygonDataBacktesting,
    datetime(2025, 8, 21),
    datetime(2025, 8, 24),  # Just 3 days
    parameters={},
    polygon_api_key=POLYGON_CONFIG["API_KEY"],
    polygon_has_paid_subscription=True,
    show_plot=False,
    show_tearsheet=False
)
