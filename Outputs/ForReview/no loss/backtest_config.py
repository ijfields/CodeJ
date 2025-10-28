"""
Centralized Backtesting Configuration

This module provides a consistent way to get backtesting parameters
across all test scripts. It prioritizes .env settings but allows overrides.

Usage:
    from backtest_config import get_backtest_dates, get_polygon_config

    start, end = get_backtest_dates()
    polygon_config = get_polygon_config()
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from project root
project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / '.env')


def get_backtest_dates(start_override=None, end_override=None):
    """
    Get backtesting date range with consistent priority:
    1. Explicit overrides (passed as parameters)
    2. Environment variables (BACKTESTING_START/END in .env)
    3. Sensible defaults

    Args:
        start_override: Optional datetime to override all other sources
        end_override: Optional datetime to override all other sources

    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    # Priority 1: Explicit overrides
    if start_override and end_override:
        print("[Config] Using parameter overrides for dates")
        return start_override, end_override

    # Priority 2: Environment variables
    env_start = os.getenv("BACKTESTING_START")
    env_end = os.getenv("BACKTESTING_END")

    if env_start and env_end:
        try:
            start_date = datetime.strptime(env_start, "%Y-%m-%d")
            end_date = datetime.strptime(env_end, "%Y-%m-%d")
            print(f"[Config] Using dates from .env: {env_start} to {env_end}")
            return start_date, end_date
        except ValueError as e:
            print(f"[Config] Warning: Invalid date format in .env: {e}")
            print("[Config] Falling back to defaults")

    # Priority 3: Sensible defaults (Q1 2024)
    print("[Config] Using default dates: 2024-01-01 to 2024-03-31")
    print("[Config] (Set BACKTESTING_START/END in .env to change)")
    return datetime(2024, 1, 1), datetime(2024, 3, 31)


def get_polygon_config():
    """
    Get Polygon.io configuration from environment.

    Returns:
        dict: Configuration dictionary with keys:
            - api_key: Polygon API key
            - has_paid_subscription: Boolean indicating subscription level
    """
    api_key = os.getenv("POLYGON_API_KEY")
    has_paid = os.getenv("POLYGON_IS_PAID_SUBSCRIPTION", "false").lower() == "true"

    if not api_key:
        print("[Config] Warning: POLYGON_API_KEY not set in .env")
    else:
        print(f"[Config] Polygon API key loaded (length: {len(api_key)})")

    print(f"[Config] Paid subscription: {has_paid}")

    return {
        "api_key": api_key,
        "has_paid_subscription": has_paid
    }


def get_strategy_params(symbol="SPY", **overrides):
    """
    Get default strategy parameters with optional overrides.

    Args:
        symbol: Stock symbol to trade
        **overrides: Any parameters to override defaults

    Returns:
        dict: Strategy parameters
    """
    defaults = {
        "symbol": symbol,
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
        "max_cost_vs_protection": 1.0,
    }

    # Apply overrides
    defaults.update(overrides)

    print(f"[Config] Strategy: {defaults['symbol']}")
    print(f"[Config] Target DTE: {defaults['dte_target']} days")

    return defaults


def print_config_summary():
    """Print a summary of all configuration settings."""
    print("\n" + "="*70)
    print("BACKTESTING CONFIGURATION SUMMARY")
    print("="*70)

    start, end = get_backtest_dates()
    polygon = get_polygon_config()

    days_diff = (end - start).days

    print(f"\nDate Range:")
    print(f"  Start: {start.strftime('%Y-%m-%d')}")
    print(f"  End:   {end.strftime('%Y-%m-%d')}")
    print(f"  Days:  {days_diff} calendar days (~{days_diff * 5/7:.0f} trading days)")

    print(f"\nPolygon Configuration:")
    print(f"  API Key: {'[OK] Set' if polygon['api_key'] else '[X] Not set'}")
    print(f"  Paid Plan: {'[OK] Yes' if polygon['has_paid_subscription'] else '[X] No (Free tier)'}")

    print(f"\nEnvironment:")
    print(f"  IS_BACKTESTING: {os.getenv('IS_BACKTESTING', 'not set')}")

    print("="*70 + "\n")


if __name__ == "__main__":
    # When run directly, print configuration summary
    print("Testing backtest_config.py\n")

    # Test getting dates
    start, end = get_backtest_dates()
    print(f"\nDates: {start} to {end}")

    # Test getting Polygon config
    polygon = get_polygon_config()
    print(f"\nPolygon config: {polygon}")

    # Test getting strategy params
    params = get_strategy_params("SPY")
    print(f"\nStrategy params: {params}")

    # Print full summary
    print_config_summary()

    # Test with overrides
    print("\nTesting with overrides:")
    custom_start = datetime(2023, 6, 1)
    custom_end = datetime(2023, 8, 31)
    start, end = get_backtest_dates(custom_start, custom_end)
    print(f"Overridden dates: {start} to {end}")
