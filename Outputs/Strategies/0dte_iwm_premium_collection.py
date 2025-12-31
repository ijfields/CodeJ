"""
0DTE IWM Options Premium Collection Strategy

Strategy Overview:
- Sells out-of-the-money (OTM) puts and calls on IWM at market open
- Targets 0DTE (same-day expiration) options
- Buys back options when premium decays to target levels
- High-frequency intraday monitoring

Entry Conditions:
- Sell 10 OTM puts (strike: current price - $5)
- Sell 5 OTM calls at higher strike ($191 or current + offset)
- Sell 5 OTM calls at mid strike ($190 or current + offset)
- Entry within first 30 minutes of market open

Exit Conditions:
- Buy back puts when premium <= $0.02
- Buy back high calls when premium <= $0.15
- Buy back mid calls when premium <= $0.07
- Auto-close all positions 15 minutes before market close

Risk Management:
- 0DTE only (expires same day)
- Premium collection strategy
- Maximum position size controlled via parameters

Author: lumibot-coder
Date: 2025-01-26
"""

from lumibot.strategies import Strategy
from lumibot.entities import Asset
from lumibot.backtesting import PolygonDataBacktesting
from datetime import datetime, date, time, timedelta
import pandas as pd
import traceback

from credentials import IS_BACKTESTING, POLYGON_CONFIG


class ZeroDTE_IWM_PremiumCollection(Strategy):
    """
    0DTE Options Premium Collection on IWM

    Sells OTM puts and calls at market open,
    buys back when premium decays to target levels.
    """

    parameters = {
        # Core settings
        "symbol": "IWM",

        # Position sizing
        "num_puts": 10,
        "num_calls_high": 5,  # Higher strike calls (191)
        "num_calls_mid": 5,   # Mid strike calls (190)

        # Strike selection
        "put_strike_offset": 5,      # Puts $5 OTM below current price
        "call_strike_high": 191,     # Target high strike (or None for dynamic)
        "call_strike_mid": 190,      # Target mid strike (or None for dynamic)
        "call_high_offset": 3,       # If no fixed strike, use offset from current
        "call_mid_offset": 2,        # If no fixed strike, use offset from current

        # Exit targets (premium thresholds)
        "exit_put_premium": 0.02,
        "exit_call_high_premium": 0.15,
        "exit_call_mid_premium": 0.07,

        # Timing
        "entry_time_minutes": 30,  # Enter within 30 min of market open
        "check_frequency_minutes": 5,  # Check positions every 5 minutes

        # Safety settings
        "close_before_eod_minutes": 15,  # Close all 15 min before market close
        "enable_dynamic_strikes": True,  # Use dynamic strikes if fixed not available
    }

    def initialize(self):
        """
        Initialize strategy parameters and state

        Sets up:
        - Trading frequency
        - Market timing rules
        - State tracking variables
        - Parameter loading
        """
        try:
            # =================================================================
            # TRADING FREQUENCY
            # =================================================================
            # Check positions every 5 minutes for intraday 0DTE management
            check_freq = self.parameters.get("check_frequency_minutes", 5)
            self.sleeptime = f"{check_freq}M"

            self.log_message("=" * 80)
            self.log_message("INITIALIZING 0DTE IWM PREMIUM COLLECTION STRATEGY")
            self.log_message("=" * 80)

            # =================================================================
            # MARKET TIMING
            # =================================================================
            self.minutes_before_closing = self.parameters.get("close_before_eod_minutes", 15)
            self.minutes_before_opening = 0  # Trade immediately at open

            self.log_message(f"Trading frequency: Every {check_freq} minutes")
            self.log_message(f"Auto-close before EOD: {self.minutes_before_closing} minutes")

            # =================================================================
            # SYMBOL CONFIGURATION
            # =================================================================
            self.symbol = self.parameters.get("symbol", "IWM")
            self.log_message(f"Underlying symbol: {self.symbol}")

            # =================================================================
            # POSITION SIZING
            # =================================================================
            self.num_puts = self.parameters.get("num_puts", 10)
            self.num_calls_high = self.parameters.get("num_calls_high", 5)
            self.num_calls_mid = self.parameters.get("num_calls_mid", 5)

            self.log_message(f"Position sizing: {self.num_puts} puts, "
                           f"{self.num_calls_high} high calls, "
                           f"{self.num_calls_mid} mid calls")

            # =================================================================
            # STRIKE CONFIGURATION
            # =================================================================
            self.put_strike_offset = self.parameters.get("put_strike_offset", 5)
            self.call_strike_high = self.parameters.get("call_strike_high", 191)
            self.call_strike_mid = self.parameters.get("call_strike_mid", 190)
            self.call_high_offset = self.parameters.get("call_high_offset", 3)
            self.call_mid_offset = self.parameters.get("call_mid_offset", 2)
            self.enable_dynamic_strikes = self.parameters.get("enable_dynamic_strikes", True)

            self.log_message(f"Put strike: Current - ${self.put_strike_offset}")
            self.log_message(f"Call high strike: ${self.call_strike_high} (or dynamic: Current + ${self.call_high_offset})")
            self.log_message(f"Call mid strike: ${self.call_strike_mid} (or dynamic: Current + ${self.call_mid_offset})")

            # =================================================================
            # EXIT THRESHOLDS
            # =================================================================
            self.exit_put_premium = self.parameters.get("exit_put_premium", 0.02)
            self.exit_call_high_premium = self.parameters.get("exit_call_high_premium", 0.15)
            self.exit_call_mid_premium = self.parameters.get("exit_call_mid_premium", 0.07)

            self.log_message(f"Exit targets - Puts: ${self.exit_put_premium:.2f}, "
                           f"High calls: ${self.exit_call_high_premium:.2f}, "
                           f"Mid calls: ${self.exit_call_mid_premium:.2f}")

            # =================================================================
            # TIMING CONFIGURATION
            # =================================================================
            self.entry_window_minutes = self.parameters.get("entry_time_minutes", 30)
            self.log_message(f"Entry window: First {self.entry_window_minutes} minutes of trading")

            # =================================================================
            # STATE VARIABLES
            # =================================================================
            # Track if we've entered positions today
            self.positions_entered = False

            # Track entry premiums for each position type
            self.entry_premium_puts = None
            self.entry_premium_calls_high = None
            self.entry_premium_calls_mid = None

            # Track actual option contracts
            self.option_asset_puts = None
            self.option_asset_calls_high = None
            self.option_asset_calls_mid = None

            # Track current trading day
            self.current_trading_day = None

            # Track if positions were closed
            self.positions_closed_puts = False
            self.positions_closed_calls_high = False
            self.positions_closed_calls_mid = False

            self.log_message("State variables initialized")
            self.log_message("=" * 80)
            self.log_message("INITIALIZATION COMPLETE")
            self.log_message("=" * 80)

        except Exception as e:
            self.log_message(f"ERROR in initialize(): {str(e)}")
            self.log_message(traceback.format_exc())
            raise

    def on_trading_iteration(self):
        """
        Main trading logic executed every iteration

        Flow:
        1. Check if new trading day (reset state)
        2. Check if within entry window
        3. Enter positions if not entered
        4. Monitor and exit positions based on premium decay
        5. Force close all positions before market close
        """
        try:
            self._execute_trading_logic()

        except Exception as e:
            self.log_message(f"ERROR in trading iteration: {str(e)}")
            self.log_message(traceback.format_exc())

    def _execute_trading_logic(self):
        """
        Wrapped trading logic with comprehensive error handling
        """
        # =================================================================
        # STEP 1: CHECK FOR NEW TRADING DAY
        # =================================================================
        current_datetime = self.get_datetime()
        current_day = current_datetime.date()

        if self.current_trading_day != current_day:
            self.log_message("=" * 80)
            self.log_message(f"NEW TRADING DAY: {current_day}")
            self.log_message("=" * 80)
            self._reset_daily_state()
            self.current_trading_day = current_day

        # =================================================================
        # STEP 2: GET CURRENT MARKET DATA
        # =================================================================
        current_price = self.get_last_price(self.symbol)

        if current_price is None or current_price <= 0:
            self.log_message(f"WARNING: Invalid price for {self.symbol}: {current_price}")
            return

        self.log_message(f"Current {self.symbol} price: ${current_price:.2f}")

        # =================================================================
        # STEP 3: CHECK IF IN ENTRY WINDOW
        # =================================================================
        is_in_entry_window = self._is_within_entry_window(current_datetime)

        if is_in_entry_window:
            self.log_message("Within entry window (first 30 minutes of trading)")

        # =================================================================
        # STEP 4: ENTRY LOGIC
        # =================================================================
        if not self.positions_entered and is_in_entry_window:
            self.log_message("Attempting to enter positions...")
            self._enter_positions(current_price)

        # =================================================================
        # STEP 5: EXIT LOGIC (Monitor existing positions)
        # =================================================================
        elif self.positions_entered:
            self.log_message("Monitoring positions for exit conditions...")
            self._monitor_and_exit_positions()

        # =================================================================
        # STEP 6: FORCE CLOSE BEFORE EOD
        # =================================================================
        if self._should_close_all_positions(current_datetime):
            self.log_message("APPROACHING END OF DAY - CLOSING ALL POSITIONS")
            self._force_close_all_positions()

    def _reset_daily_state(self):
        """Reset state variables for new trading day"""
        self.log_message("Resetting daily state...")

        self.positions_entered = False
        self.entry_premium_puts = None
        self.entry_premium_calls_high = None
        self.entry_premium_calls_mid = None
        self.option_asset_puts = None
        self.option_asset_calls_high = None
        self.option_asset_calls_mid = None
        self.positions_closed_puts = False
        self.positions_closed_calls_high = False
        self.positions_closed_calls_mid = False

        self.log_message("Daily state reset complete")

    def _is_within_entry_window(self, current_datetime):
        """
        Check if current time is within entry window

        Entry window: First N minutes after market open
        Market open: 9:30 AM ET
        """
        market_open_time = time(9, 30)  # 9:30 AM
        current_time = current_datetime.time()

        # Calculate entry window end time
        market_open_datetime = datetime.combine(current_datetime.date(), market_open_time)
        entry_window_end = market_open_datetime + timedelta(minutes=self.entry_window_minutes)
        entry_window_end_time = entry_window_end.time()

        # Check if current time is within window
        is_within = current_time >= market_open_time and current_time <= entry_window_end_time

        if is_within:
            self.log_message(f"Time {current_time} is within entry window "
                           f"({market_open_time} to {entry_window_end_time})")

        return is_within

    def _should_close_all_positions(self, current_datetime):
        """Check if should force close all positions before EOD"""
        market_close_time = time(16, 0)  # 4:00 PM
        current_time = current_datetime.time()

        # Calculate force close time
        market_close_datetime = datetime.combine(current_datetime.date(), market_close_time)
        force_close_datetime = market_close_datetime - timedelta(minutes=self.minutes_before_closing)
        force_close_time = force_close_datetime.time()

        # Check if past force close time
        should_close = current_time >= force_close_time

        if should_close and self.positions_entered:
            self.log_message(f"Time {current_time} >= force close time {force_close_time}")

        return should_close

    def _enter_positions(self, current_price):
        """
        Enter all positions: sell puts and calls

        Args:
            current_price: Current price of underlying
        """
        self.log_message("-" * 80)
        self.log_message("ENTERING POSITIONS")
        self.log_message("-" * 80)

        # Get 0DTE option contracts
        put_option = self._get_0dte_put_contract(current_price)
        call_high_option = self._get_0dte_call_contract(current_price, "high")
        call_mid_option = self._get_0dte_call_contract(current_price, "mid")

        # Validate we got all contracts
        if put_option is None:
            self.log_message("ERROR: Could not find 0DTE put contract")
        if call_high_option is None:
            self.log_message("ERROR: Could not find 0DTE high call contract")
        if call_mid_option is None:
            self.log_message("ERROR: Could not find 0DTE mid call contract")

        # Only proceed if we got all contracts
        if put_option is None or call_high_option is None or call_mid_option is None:
            self.log_message("WARNING: Not all option contracts found, skipping entry")
            return

        # Store option assets
        self.option_asset_puts = put_option
        self.option_asset_calls_high = call_high_option
        self.option_asset_calls_mid = call_mid_option

        # Get current premiums
        put_premium = self.get_last_price(put_option)
        call_high_premium = self.get_last_price(call_high_option)
        call_mid_premium = self.get_last_price(call_mid_option)

        # Validate premiums
        if put_premium is None or put_premium <= 0:
            self.log_message(f"WARNING: Invalid put premium: {put_premium}")
            return
        if call_high_premium is None or call_high_premium <= 0:
            self.log_message(f"WARNING: Invalid high call premium: {call_high_premium}")
            return
        if call_mid_premium is None or call_mid_premium <= 0:
            self.log_message(f"WARNING: Invalid mid call premium: {call_mid_premium}")
            return

        # Store entry premiums
        self.entry_premium_puts = put_premium
        self.entry_premium_calls_high = call_high_premium
        self.entry_premium_calls_mid = call_mid_premium

        self.log_message(f"Entry premiums - Puts: ${put_premium:.2f}, "
                       f"High calls: ${call_high_premium:.2f}, "
                       f"Mid calls: ${call_mid_premium:.2f}")

        # Execute orders: SELL to open (premium collection)
        success = True

        # Sell puts
        try:
            self.log_message(f"SELLING {self.num_puts} PUT contracts at ${put_option.strike} "
                           f"@ ${put_premium:.2f} premium")
            order_puts = self.create_order(
                asset=put_option,
                quantity=self.num_puts,
                side="sell"
            )
            self.submit_order(order_puts)
            self.log_message(f"✓ Put order submitted successfully")
        except Exception as e:
            self.log_message(f"ERROR selling puts: {str(e)}")
            success = False

        # Sell high calls
        try:
            self.log_message(f"SELLING {self.num_calls_high} CALL contracts at ${call_high_option.strike} "
                           f"@ ${call_high_premium:.2f} premium")
            order_calls_high = self.create_order(
                asset=call_high_option,
                quantity=self.num_calls_high,
                side="sell"
            )
            self.submit_order(order_calls_high)
            self.log_message(f"✓ High call order submitted successfully")
        except Exception as e:
            self.log_message(f"ERROR selling high calls: {str(e)}")
            success = False

        # Sell mid calls
        try:
            self.log_message(f"SELLING {self.num_calls_mid} CALL contracts at ${call_mid_option.strike} "
                           f"@ ${call_mid_premium:.2f} premium")
            order_calls_mid = self.create_order(
                asset=call_mid_option,
                quantity=self.num_calls_mid,
                side="sell"
            )
            self.submit_order(order_calls_mid)
            self.log_message(f"✓ Mid call order submitted successfully")
        except Exception as e:
            self.log_message(f"ERROR selling mid calls: {str(e)}")
            success = False

        if success:
            self.positions_entered = True
            total_premium = (put_premium * self.num_puts * 100 +
                           call_high_premium * self.num_calls_high * 100 +
                           call_mid_premium * self.num_calls_mid * 100)
            self.log_message("-" * 80)
            self.log_message(f"✓ ALL POSITIONS ENTERED SUCCESSFULLY")
            self.log_message(f"Total premium collected: ${total_premium:.2f}")
            self.log_message("-" * 80)
        else:
            self.log_message("WARNING: Some orders failed, check logs above")

    def _monitor_and_exit_positions(self):
        """
        Monitor existing positions and exit when premium targets reached
        """
        # Check each position type separately

        # -----------------------------------------------------------------
        # PUTS
        # -----------------------------------------------------------------
        if not self.positions_closed_puts and self.option_asset_puts:
            position = self.get_position(self.option_asset_puts)

            if position and position.quantity > 0:
                current_premium = self.get_last_price(self.option_asset_puts)

                if current_premium is not None and current_premium > 0:
                    self.log_message(f"PUT position - Entry: ${self.entry_premium_puts:.2f}, "
                                   f"Current: ${current_premium:.2f}, "
                                   f"Target: ${self.exit_put_premium:.2f}")

                    if current_premium <= self.exit_put_premium:
                        self._close_position(self.option_asset_puts, "PUTS", current_premium)
                        self.positions_closed_puts = True

        # -----------------------------------------------------------------
        # HIGH CALLS
        # -----------------------------------------------------------------
        if not self.positions_closed_calls_high and self.option_asset_calls_high:
            position = self.get_position(self.option_asset_calls_high)

            if position and position.quantity > 0:
                current_premium = self.get_last_price(self.option_asset_calls_high)

                if current_premium is not None and current_premium > 0:
                    self.log_message(f"HIGH CALL position - Entry: ${self.entry_premium_calls_high:.2f}, "
                                   f"Current: ${current_premium:.2f}, "
                                   f"Target: ${self.exit_call_high_premium:.2f}")

                    if current_premium <= self.exit_call_high_premium:
                        self._close_position(self.option_asset_calls_high, "HIGH CALLS", current_premium)
                        self.positions_closed_calls_high = True

        # -----------------------------------------------------------------
        # MID CALLS
        # -----------------------------------------------------------------
        if not self.positions_closed_calls_mid and self.option_asset_calls_mid:
            position = self.get_position(self.option_asset_calls_mid)

            if position and position.quantity > 0:
                current_premium = self.get_last_price(self.option_asset_calls_mid)

                if current_premium is not None and current_premium > 0:
                    self.log_message(f"MID CALL position - Entry: ${self.entry_premium_calls_mid:.2f}, "
                                   f"Current: ${current_premium:.2f}, "
                                   f"Target: ${self.exit_call_mid_premium:.2f}")

                    if current_premium <= self.exit_call_mid_premium:
                        self._close_position(self.option_asset_calls_mid, "MID CALLS", current_premium)
                        self.positions_closed_calls_mid = True

    def _close_position(self, option_asset, position_name, current_premium):
        """
        Close a specific option position

        Args:
            option_asset: Asset object for the option
            position_name: Name for logging (e.g., "PUTS", "HIGH CALLS")
            current_premium: Current premium value
        """
        try:
            self.log_message("-" * 80)
            self.log_message(f"CLOSING {position_name} POSITION")
            self.log_message(f"Premium decayed to target: ${current_premium:.2f}")

            position = self.get_position(option_asset)
            if position and position.quantity > 0:
                # Create buy-to-close order
                order = self.create_order(
                    asset=option_asset,
                    quantity=position.quantity,
                    side="buy"  # Buy to close short position
                )
                self.submit_order(order)

                # Calculate profit
                if position_name == "PUTS" and self.entry_premium_puts:
                    profit_per_contract = (self.entry_premium_puts - current_premium) * 100
                    total_profit = profit_per_contract * position.quantity
                elif position_name == "HIGH CALLS" and self.entry_premium_calls_high:
                    profit_per_contract = (self.entry_premium_calls_high - current_premium) * 100
                    total_profit = profit_per_contract * position.quantity
                elif position_name == "MID CALLS" and self.entry_premium_calls_mid:
                    profit_per_contract = (self.entry_premium_calls_mid - current_premium) * 100
                    total_profit = profit_per_contract * position.quantity
                else:
                    total_profit = 0

                self.log_message(f"✓ {position_name} position closed")
                self.log_message(f"Estimated profit: ${total_profit:.2f}")
                self.log_message("-" * 80)

        except Exception as e:
            self.log_message(f"ERROR closing {position_name}: {str(e)}")
            self.log_message(traceback.format_exc())

    def _force_close_all_positions(self):
        """Force close all positions before end of day"""
        try:
            self.log_message("=" * 80)
            self.log_message("FORCE CLOSING ALL POSITIONS (END OF DAY)")
            self.log_message("=" * 80)

            self.sell_all()

            self.positions_closed_puts = True
            self.positions_closed_calls_high = True
            self.positions_closed_calls_mid = True

            self.log_message("✓ All positions closed")
            self.log_message("=" * 80)

        except Exception as e:
            self.log_message(f"ERROR force closing positions: {str(e)}")
            self.log_message(traceback.format_exc())

    def _get_0dte_put_contract(self, current_price):
        """
        Find 0DTE put contract

        Args:
            current_price: Current price of underlying

        Returns:
            Asset object for put option, or None if not found
        """
        try:
            self.log_message(f"Searching for 0DTE PUT contract...")

            # Get option chains
            chains = self.get_chains(Asset(self.symbol))

            if chains is None:
                self.log_message("ERROR: No option chains available")
                return None

            # Get put expirations
            expiries = chains.expirations("PUT")

            if not expiries:
                self.log_message("ERROR: No PUT expirations found")
                return None

            # Filter for 0DTE (expires today)
            today = date.today()
            dte_0 = [exp for exp in expiries if exp == today]

            if not dte_0:
                self.log_message(f"WARNING: No 0DTE options found for {today}")
                self.log_message(f"Available expirations: {expiries[:5]}")
                return None

            expiry = dte_0[0]
            self.log_message(f"Found 0DTE expiration: {expiry}")

            # Get strikes
            strikes = chains.strikes(expiry, "PUT")

            if not strikes:
                self.log_message("ERROR: No strikes found for PUT")
                return None

            self.log_message(f"Available PUT strikes: {len(strikes)} strikes")

            # Select strike: $5 below current price
            target_strike = current_price - self.put_strike_offset
            otm_strikes = [s for s in strikes if s <= target_strike]

            if not otm_strikes:
                self.log_message(f"WARNING: No OTM PUT strikes found below ${target_strike:.2f}")
                return None

            # Get closest strike to target
            selected_strike = max(otm_strikes)

            self.log_message(f"Selected PUT strike: ${selected_strike:.2f} "
                           f"(target: ${target_strike:.2f}, current: ${current_price:.2f})")

            # Create option Asset
            option = Asset(
                symbol=self.symbol,
                asset_type=Asset.AssetType.OPTION,
                expiration=expiry,
                strike=selected_strike,
                right=Asset.OptionRight.PUT
            )

            return option

        except Exception as e:
            self.log_message(f"ERROR in _get_0dte_put_contract: {str(e)}")
            self.log_message(traceback.format_exc())
            return None

    def _get_0dte_call_contract(self, current_price, call_type="high"):
        """
        Find 0DTE call contract

        Args:
            current_price: Current price of underlying
            call_type: "high" or "mid" to select strike level

        Returns:
            Asset object for call option, or None if not found
        """
        try:
            self.log_message(f"Searching for 0DTE CALL contract ({call_type})...")

            # Get option chains
            chains = self.get_chains(Asset(self.symbol))

            if chains is None:
                self.log_message("ERROR: No option chains available")
                return None

            # Get call expirations
            expiries = chains.expirations("CALL")

            if not expiries:
                self.log_message("ERROR: No CALL expirations found")
                return None

            # Filter for 0DTE (expires today)
            today = date.today()
            dte_0 = [exp for exp in expiries if exp == today]

            if not dte_0:
                self.log_message(f"WARNING: No 0DTE options found for {today}")
                return None

            expiry = dte_0[0]
            self.log_message(f"Found 0DTE expiration: {expiry}")

            # Get strikes
            strikes = chains.strikes(expiry, "CALL")

            if not strikes:
                self.log_message("ERROR: No strikes found for CALL")
                return None

            self.log_message(f"Available CALL strikes: {len(strikes)} strikes")

            # Select strike based on type
            if call_type == "high":
                # Try fixed strike first
                if self.call_strike_high and self.call_strike_high in strikes:
                    selected_strike = self.call_strike_high
                    self.log_message(f"Using fixed high strike: ${selected_strike:.2f}")

                # Fall back to dynamic
                elif self.enable_dynamic_strikes:
                    target_strike = current_price + self.call_high_offset
                    otm_strikes = [s for s in strikes if s >= target_strike]

                    if otm_strikes:
                        selected_strike = min(otm_strikes)
                        self.log_message(f"Using dynamic high strike: ${selected_strike:.2f} "
                                       f"(target: ${target_strike:.2f})")
                    else:
                        self.log_message(f"WARNING: No OTM CALL strikes found above ${target_strike:.2f}")
                        return None
                else:
                    self.log_message(f"WARNING: Fixed strike ${self.call_strike_high} not available and dynamic disabled")
                    return None

            else:  # mid
                # Try fixed strike first
                if self.call_strike_mid and self.call_strike_mid in strikes:
                    selected_strike = self.call_strike_mid
                    self.log_message(f"Using fixed mid strike: ${selected_strike:.2f}")

                # Fall back to dynamic
                elif self.enable_dynamic_strikes:
                    target_strike = current_price + self.call_mid_offset
                    otm_strikes = [s for s in strikes if s >= target_strike]

                    if otm_strikes:
                        selected_strike = min(otm_strikes)
                        self.log_message(f"Using dynamic mid strike: ${selected_strike:.2f} "
                                       f"(target: ${target_strike:.2f})")
                    else:
                        self.log_message(f"WARNING: No OTM CALL strikes found above ${target_strike:.2f}")
                        return None
                else:
                    self.log_message(f"WARNING: Fixed strike ${self.call_strike_mid} not available and dynamic disabled")
                    return None

            self.log_message(f"Selected {call_type.upper()} CALL strike: ${selected_strike:.2f} "
                           f"(current: ${current_price:.2f})")

            # Create option Asset
            option = Asset(
                symbol=self.symbol,
                asset_type=Asset.AssetType.OPTION,
                expiration=expiry,
                strike=selected_strike,
                right=Asset.OptionRight.CALL
            )

            return option

        except Exception as e:
            self.log_message(f"ERROR in _get_0dte_call_contract ({call_type}): {str(e)}")
            self.log_message(traceback.format_exc())
            return None


# =============================================================================
# BACKTEST EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Run backtest of 0DTE IWM strategy

    Note: Options backtesting requires Polygon.io paid subscription
          for historical options data
    """

    # Check if running in backtest mode
    if not IS_BACKTESTING:
        print("=" * 80)
        print("ERROR: Strategy configured for live trading")
        print("Set IS_BACKTESTING = True in credentials.py to run backtest")
        print("=" * 80)
        exit(1)

    # Validate Polygon API key
    if not POLYGON_CONFIG.get("API_KEY"):
        print("=" * 80)
        print("ERROR: Polygon API key not configured")
        print("Add POLYGON_API_KEY to your .env file")
        print("=" * 80)
        exit(1)

    print("=" * 80)
    print("0DTE IWM PREMIUM COLLECTION STRATEGY - BACKTEST")
    print("=" * 80)
    print()
    print("IMPORTANT NOTES:")
    print("1. Options backtesting requires Polygon.io PAID subscription")
    print("2. Historical options data is required for accurate backtesting")
    print("3. Ensure your Polygon plan includes options data")
    print()
    print("Strategy Parameters:")
    print(f"  - Underlying: IWM")
    print(f"  - Position: 10 puts, 5 high calls, 5 mid calls")
    print(f"  - Put exit: $0.02 premium")
    print(f"  - High call exit: $0.15 premium")
    print(f"  - Mid call exit: $0.07 premium")
    print()
    print("=" * 80)

    # Backtest configuration
    backtesting_start = datetime(2024, 1, 2)
    backtesting_end = datetime(2024, 12, 31)

    print(f"Backtest period: {backtesting_start.date()} to {backtesting_end.date()}")
    print("=" * 80)
    print()

    # Run backtest
    try:
        ZeroDTE_IWM_PremiumCollection.backtest(
            datasource_class=PolygonDataBacktesting,
            backtesting_start=backtesting_start,
            backtesting_end=backtesting_end,

            # Polygon configuration
            polygon_api_key=POLYGON_CONFIG["API_KEY"],
            polygon_has_paid_subscription=True,  # Required for options data

            # Strategy parameters
            parameters={
                "symbol": "IWM",
                "num_puts": 10,
                "num_calls_high": 5,
                "num_calls_mid": 5,
                "put_strike_offset": 5,
                "call_strike_high": 191,
                "call_strike_mid": 190,
                "exit_put_premium": 0.02,
                "exit_call_high_premium": 0.15,
                "exit_call_mid_premium": 0.07,
                "entry_time_minutes": 30,
                "check_frequency_minutes": 5,
                "enable_dynamic_strikes": True,
            },

            # Benchmark
            benchmark_asset="IWM",

            # Show stats
            show_plot=True,
            show_tearsheet=True,
            save_tearsheet=True,
            tearsheet_file="0dte_iwm_tearsheet.html"
        )

        print()
        print("=" * 80)
        print("BACKTEST COMPLETE")
        print("Check the generated tearsheet: 0dte_iwm_tearsheet.html")
        print("=" * 80)

    except Exception as e:
        print()
        print("=" * 80)
        print("BACKTEST ERROR")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        print("Possible issues:")
        print("1. No Polygon.io paid subscription (required for options data)")
        print("2. Invalid API key")
        print("3. No historical options data available for IWM")
        print("4. Network connectivity issues")
        print()
        print("Full traceback:")
        print(traceback.format_exc())
        print("=" * 80)
