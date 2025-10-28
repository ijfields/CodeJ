#!/usr/bin/env python3
"""
Test the EXACT video trade: Aug 21 - Oct 17, 2025
VISA (V) @ ~$343 with Oct 17 expiration
This is the actual confirmed trade from the video!
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
    print("ZERO LOSS BUTTERFLY - VIDEO TRADE TEST")
    print("="*70)
    print()
    print("Testing EXACT video trade:")
    print("  Symbol: VISA (V)")
    print("  Entry: August 21, 2025")
    print("  Expiration: October 17, 2025")
    print("  Expected Strikes: $330 PUT / $340 CALL (x2) / $350 CALL")
    print("  Stock Price: ~$343")
    print()
    print("="*70)
    print()

    # EXACT dates from video
    start_date = datetime(2025, 8, 21)   # Entry date from video
    end_date = datetime(2025, 10, 17)    # Expiration from video

    # Strategy parameters matching video trade
    strategy_params = {
        "symbol": "V",               # VISA
        "shares_per_position": 100,
        "dte_target": 57,            # Aug 21 → Oct 17 = 57 days
        "dte_min": 50,
        "dte_max": 65,
        "strike_width": 10,          # $10 between strikes ($330-$340-$350)
        "put_offset": -13,           # $330 PUT when stock at $343
        "center_offset": -3,         # $340 CALL when stock at $343
        "upper_offset": 7,           # $350 CALL when stock at $343
        "roll_days_before_exp": 7,
        "check_frequency": "1D",
    }

    print(f"Period: {start_date.date()} to {end_date.date()}")
    print(f"Symbol: {strategy_params['symbol']}")
    print(f"Target DTE: {strategy_params['dte_target']} days")
    print()
    print("Expected behavior:")
    print("  - Enter 4-leg position on Aug 21")
    print("  - Hold through Oct 17 expiration")
    print("  - Stock purchased ONCE (not 40+ times)")
    print("  - Options should fill at standard $5 strikes")
    print()

    try:
        results = ZeroLossButterfly.run_backtest(
            PolygonDataBacktesting,
            start_date,
            end_date,
            parameters=strategy_params,
            polygon_api_key=POLYGON_CONFIG["API_KEY"],
            polygon_has_paid_subscription=POLYGON_CONFIG["HAS_PAID_SUBSCRIPTION"],
            show_plot=True,
            show_tearsheet=True,
            save_tearsheet=True,
            show_indicators=False,
            benchmark_asset="V"
        )

        print()
        print("="*70)
        print("VIDEO TRADE TEST COMPLETED")
        print("="*70)
        print()

        # Check for trades CSV to validate
        print("Looking for trades CSV to validate...")
        import glob
        csv_files = glob.glob(str(project_root / "logs" / "*ZeroLoss*trades.csv"))
        if csv_files:
            latest_csv = max(csv_files, key=os.path.getmtime)
            print(f"Found: {os.path.basename(latest_csv)}")
            print()
            print("Run validator:")
            print(f'  python backtest_validator.py "{latest_csv}" 100')

    except Exception as e:
        print()
        print("="*70)
        print("ERROR DURING VIDEO TRADE TEST")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("Possible issues:")
        print("  1. No options data available for Oct 17, 2025 expiration")
        print("  2. VISA might have low options volume")
        print("  3. Try with SPY instead (more liquid)")

if __name__ == "__main__":
    main()
