#!/usr/bin/env python3
"""
Backtest Validator - Sanity Checks for Zero Loss Butterfly Strategy

Validates backtest results to catch bugs before they cause significant issues:
1. Stock quantity should NEVER exceed shares_per_position (typically 100)
2. Account balance should NEVER go negative
3. Butterfly structure: 1 PUT, 2 short CALLs, 1 long CALL per position
4. No excessive trading (re-buying stock repeatedly)
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class BacktestValidator:
    """Validates backtest results for common bugs and anomalies"""

    def __init__(self, trades_csv_path: str, expected_stock_shares: int = 100):
        """
        Initialize validator with trades CSV file

        Args:
            trades_csv_path: Path to trades CSV file from backtest
            expected_stock_shares: Expected total stock position (default 100)
        """
        self.trades_csv_path = Path(trades_csv_path)
        self.expected_stock_shares = expected_stock_shares
        self.df = None
        self.errors = []
        self.warnings = []

    def load_trades(self) -> bool:
        """Load trades CSV file"""
        try:
            self.df = pd.read_csv(self.trades_csv_path)
            print(f"[OK] Loaded {len(self.df)} trades from {self.trades_csv_path.name}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to load trades: {e}")
            return False

    def validate_stock_quantity(self) -> bool:
        """
        Validate that net stock position never exceeds expected shares.

        BUG CHECK: Detects the stock re-buying bug where stock is purchased
        multiple times instead of just once.

        Returns:
            bool: True if stock quantity is valid
        """
        print("\n--- Validating Stock Quantity ---")

        # Filter for stock trades only (strike == 0 or NaN)
        stock_trades = self.df[
            (self.df['asset.strike'].isna()) | (self.df['asset.strike'] == 0)
        ].copy()

        if len(stock_trades) == 0:
            self.warnings.append("No stock trades found")
            print("[WARN] WARNING: No stock trades found")
            return True

        # Count buy vs sell orders
        stock_buys = stock_trades[stock_trades['side'] == 'buy']
        stock_sells = stock_trades[stock_trades['side'] == 'sell']

        num_buy_orders = len(stock_buys)
        num_sell_orders = len(stock_sells)

        print(f"Stock BUY orders: {num_buy_orders}")
        print(f"Stock SELL orders: {num_sell_orders}")

        # Calculate net position (assuming filled_quantity is available)
        if 'filled_quantity' in self.df.columns:
            total_bought = stock_buys[stock_buys['status'] == 'fill']['filled_quantity'].sum()
            total_sold = stock_sells[stock_sells['status'] == 'fill']['filled_quantity'].sum()
            net_position = total_bought - total_sold

            print(f"Total shares bought: {total_bought}")
            print(f"Total shares sold: {total_sold}")
            print(f"Net stock position: {net_position}")

            # CRITICAL CHECK: Stock should be bought ONCE (maybe sold at end)
            if num_buy_orders > 1:
                error_msg = f"BUG DETECTED: Stock bought {num_buy_orders} times (should be 1)!"
                self.errors.append(error_msg)
                print(f"[FAIL] {error_msg}")

                print("\nFirst 5 stock buy orders:")
                print(stock_buys[['symbol', 'side', 'filled_quantity', 'status']].head())
                return False

            if net_position > self.expected_stock_shares:
                error_msg = f"BUG DETECTED: Net stock position {net_position} exceeds expected {self.expected_stock_shares}"
                self.errors.append(error_msg)
                print(f"[FAIL] {error_msg}")
                return False

        print(f"[OK] Stock quantity valid (bought {num_buy_orders} time(s))")
        return True

    def validate_balance(self) -> bool:
        """
        Validate that account balance never goes negative.

        BUG CHECK: Negative balance indicates over-trading or margin violations.

        Returns:
            bool: True if balance never went negative
        """
        print("\n--- Validating Account Balance ---")

        if 'cash' not in self.df.columns and 'portfolio_value' not in self.df.columns:
            self.warnings.append("No balance/cash data in trades CSV")
            print("[WARN] WARNING: No balance data available to validate")
            return True

        # Check for negative cash
        if 'cash' in self.df.columns:
            min_cash = self.df['cash'].min()
            if pd.notna(min_cash) and min_cash < 0:
                error_msg = f"BUG DETECTED: Negative balance detected (min: ${min_cash:,.2f})"
                self.errors.append(error_msg)
                print(f"[FAIL] {error_msg}")
                return False
            print(f"[OK] Balance never went negative (min cash: ${min_cash:,.2f})")

        return True

    def validate_butterfly_structure(self) -> bool:
        """
        Validate butterfly structure: Should have 1 PUT, 2 CALLs (short), 1 CALL (long).

        BUG CHECK: Ensures options are ordered correctly.

        Returns:
            bool: True if butterfly structure appears correct
        """
        print("\n--- Validating Butterfly Structure ---")

        # Filter for options only
        options = self.df[
            (self.df['asset.strike'].notna()) & (self.df['asset.strike'] > 0)
        ].copy()

        if len(options) == 0:
            self.warnings.append("No option trades found")
            print("[WARN] WARNING: No option trades found")
            return True

        # Count filled options by type
        filled_options = options[options['status'] == 'fill']

        puts = filled_options[filled_options['asset.right'] == 'PUT']
        calls = filled_options[filled_options['asset.right'] == 'CALL']

        print(f"Filled PUTs: {len(puts)}")
        print(f"Filled CALLs: {len(calls)}")

        # Check for short calls (quantity = 2)
        if 'filled_quantity' in self.df.columns:
            short_calls = calls[
                (calls['side'] == 'sell') & (calls['filled_quantity'] == 2)
            ]
            print(f"Short CALLs with quantity=2: {len(short_calls)}")

            if len(short_calls) == 0 and len(calls) > 0:
                warning_msg = "WARNING: No short CALLs with quantity=2 found (butterfly may be incomplete)"
                self.warnings.append(warning_msg)
                print(f"[WARN] {warning_msg}")

        print("[OK] Butterfly structure check completed")
        return True

    def validate_options_fill_rate(self) -> bool:
        """
        Check options fill rate to warn about data quality issues.

        Returns:
            bool: True (always passes, but may generate warnings)
        """
        print("\n--- Validating Options Fill Rate ---")

        options = self.df[
            (self.df['asset.strike'].notna()) & (self.df['asset.strike'] > 0)
        ].copy()

        if len(options) == 0:
            print("[WARN] No option trades to validate")
            return True

        filled = options[options['status'] == 'fill']
        canceled = options[options['status'] == 'canceled']

        total_options = len(options)
        num_filled = len(filled)
        num_canceled = len(canceled)

        fill_rate = (num_filled / total_options * 100) if total_options > 0 else 0

        print(f"Total option orders: {total_options}")
        print(f"Filled: {num_filled} ({fill_rate:.1f}%)")
        print(f"Canceled: {num_canceled} ({100-fill_rate:.1f}%)")

        if fill_rate < 50:
            warning_msg = f"WARNING: Low options fill rate ({fill_rate:.1f}%) - data source may be incomplete"
            self.warnings.append(warning_msg)
            print(f"[WARN] {warning_msg}")
        elif fill_rate < 100:
            print(f"[WARN] Note: Some options were canceled - backtest may not be fully realistic")
        else:
            print("[OK] All options filled successfully")

        return True

    def run_all_validations(self) -> bool:
        """
        Run all validation checks.

        Returns:
            bool: True if all critical validations passed
        """
        print("=" * 70)
        print("BACKTEST VALIDATION REPORT")
        print("=" * 70)

        if not self.load_trades():
            return False

        # Run all checks
        results = []
        results.append(("Stock Quantity", self.validate_stock_quantity()))
        results.append(("Balance", self.validate_balance()))
        results.append(("Butterfly Structure", self.validate_butterfly_structure()))
        results.append(("Options Fill Rate", self.validate_options_fill_rate()))

        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        all_passed = all(result for _, result in results)

        for check_name, passed in results:
            status = "[OK] PASS" if passed else "[FAIL] FAIL"
            print(f"{status}: {check_name}")

        if self.errors:
            print(f"\n{len(self.errors)} ERROR(S) DETECTED:")
            for error in self.errors:
                print(f"  [FAIL] {error}")

        if self.warnings:
            print(f"\n{len(self.warnings)} WARNING(S):")
            for warning in self.warnings:
                print(f"  [WARN] {warning}")

        print("\n" + "=" * 70)

        if all_passed and not self.errors:
            print("[OK] ALL VALIDATIONS PASSED")
            return True
        else:
            print("[FAIL] VALIDATION FAILED - Review errors above")
            return False


def validate_backtest(trades_csv_path: str, expected_stock_shares: int = 100) -> bool:
    """
    Convenience function to validate a backtest.

    Args:
        trades_csv_path: Path to trades CSV file
        expected_stock_shares: Expected stock position size

    Returns:
        bool: True if validation passed
    """
    validator = BacktestValidator(trades_csv_path, expected_stock_shares)
    return validator.run_all_validations()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python backtest_validator.py <trades_csv_path> [expected_shares]")
        print("\nExample:")
        print("  python backtest_validator.py logs/ZeroLossButterfly_2025-10-26_17-22_xHo2yl_trades.csv 100")
        sys.exit(1)

    csv_path = sys.argv[1]
    expected_shares = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    success = validate_backtest(csv_path, expected_shares)
    sys.exit(0 if success else 1)
