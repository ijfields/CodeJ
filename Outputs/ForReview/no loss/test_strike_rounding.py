#!/usr/bin/env python3
"""
Quick test of strike rounding fix - Jan 2024 only (1 month)
Tests if rounding strikes to $5 intervals improves options fill rate
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load .env and change to project root
project_root = Path(__file__).resolve().parents[3]
env_path = project_root / '.env'
load_dotenv(env_path)
os.chdir(project_root)

from lumibot.backtesting import PolygonDataBacktesting

# Add script directory to path
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))
from zero_loss_butterfly import ZeroLossButterfly
from credentials import POLYGON_CONFIG

def main():
    print("="*70)
    print("STRIKE ROUNDING TEST - January 2024")
    print("="*70)
    print()
    print("Testing if $5 strike rounding improves options fill rate...")
    print()

    # Test with January 2024 only (short test)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)

    strategy_params = {
        "symbol": "SPY",
        "shares_per_position": 100,
        "dte_target": 57,
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,
        "put_offset": -10,
        "center_offset": -5,
        "upper_offset": 5,
        "roll_days_before_exp": 7,
        "check_frequency": "1D",
    }

    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"Symbol: {strategy_params['symbol']}")
    print()

    try:
        results = ZeroLossButterfly.run_backtest(
            PolygonDataBacktesting,
            start_date,
            end_date,
            parameters=strategy_params,
            polygon_api_key=POLYGON_CONFIG["API_KEY"],
            polygon_has_paid_subscription=POLYGON_CONFIG["HAS_PAID_SUBSCRIPTION"],
            show_plot=False,
            show_tearsheet=False,
            save_tearsheet=False,
            show_indicators=False,
            benchmark_asset="SPY"
        )

        print()
        print("="*70)
        print("TEST COMPLETED")
        print("="*70)
        print()

        # Results summary
        if results and len(results) > 1:
            stats = results[1]  # Second element is stats dict
            if isinstance(stats, dict):
                print(f"Total return: {stats.get('total_return', 'N/A')}")
                print(f"Max drawdown: {stats.get('max_drawdown', 'N/A')}")

    except Exception as e:
        print()
        print("="*70)
        print("ERROR DURING TEST")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
