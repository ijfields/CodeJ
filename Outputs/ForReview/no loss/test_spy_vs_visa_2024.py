#!/usr/bin/env python3
"""
Compare Zero Loss Butterfly strategy on SPY vs VISA
Using 2024 historical data (Aug 21 - Oct 17, 2024)
This uses complete historical data for reliable comparison
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

def test_symbol(symbol, label):
    """Test strategy on a given symbol"""
    print("="*70)
    print(f"TESTING: {label}")
    print("="*70)
    print()

    # Use 2024 dates (complete historical data)
    start_date = datetime(2024, 8, 21)
    end_date = datetime(2024, 10, 17)

    strategy_params = {
        "symbol": symbol,
        "shares_per_position": 100,
        "dte_target": 57,
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,
        "put_offset": -10,      # Adjust for each symbol's price
        "center_offset": -5,
        "upper_offset": 5,
        "roll_days_before_exp": 7,
        "check_frequency": "1D",
    }

    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"Symbol: {symbol}")
    print(f"Target DTE: {strategy_params['dte_target']} days")
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
            show_tearsheet=True,
            save_tearsheet=True,
            show_indicators=False,
            benchmark_asset=symbol
        )

        print()
        print("="*70)
        print(f"{label} TEST COMPLETED")
        print("="*70)
        print()

        return results

    except Exception as e:
        print()
        print("="*70)
        print(f"ERROR DURING {label} TEST")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*70)
    print("ZERO LOSS BUTTERFLY - SPY vs VISA COMPARISON")
    print("="*70)
    print()
    print("Testing strategy on both symbols with 2024 historical data")
    print("This allows direct comparison with complete options data")
    print()

    # Test SPY first (most liquid)
    spy_results = test_symbol("SPY", "SPY (S&P 500 ETF)")

    print("\n" + "="*70)
    print("PAUSE BETWEEN TESTS")
    print("="*70 + "\n")

    # Test VISA
    visa_results = test_symbol("V", "VISA")

    print()
    print("="*70)
    print("COMPARISON COMPLETE")
    print("="*70)
    print()
    print("Check the tearsheet files in logs/ directory for detailed comparison:")
    print("  - SPY tearsheet: ZeroLossButterfly_*_SPY_*_tearsheet.html")
    print("  - VISA tearsheet: ZeroLossButterfly_*_V_*_tearsheet.html")
    print()

if __name__ == "__main__":
    main()
