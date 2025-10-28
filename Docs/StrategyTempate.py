
import os
from datetime import datetime, timedelta

from lumibot.backtesting import PolygonDataBacktesting
from lumibot.entities import Asset, TradingFee
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader

from credentials import IS_BACKTESTING

class StrategyTemplate(Strategy):
    parameters = {
    }

    def initialize(self, parameters=None):
        super().initialize(parameters)

    def on_trading_iteration(self):
        super().on_trading_iteration()

    def before_market_opens(self):
        super().before_market_opens()

    def before_starting_trading(self):
        super().before_starting_trading()

    def before_market_closes(self):
        super().before_market_closes()

    def after_market_closes(self):
        super().after_market_closes()

    def on_abrupt_closing(self):
        super().on_abrupt_closing()

    def on_bot_crash(self, error):
        super().on_bot_crash(error)

    def trace_stats(self, context, snapshot_before):
        super().trace_stats(context, snapshot_before)

    def on_new_order(self, order):
        super().on_new_order(order)

    def on_partially_filled_order(self, position, order, price, quantity, multiplier):
        super().on_partially_filled_order(position, order, price, quantity, multiplier)

    def on_filled_order(self, position, order, price, quantity, multiplier):
        super().on_filled_order(position, order, price, quantity, multiplier)

    def on_canceled_order(self, order):
        super().on_canceled_order(order)

    def on_parameters_updated(self, parameters):
        super().on_parameters_updated(parameters)

if __name__ == "__main__":
    if not IS_BACKTESTING:
        ####
        # Run the strategy live
        ####

        trader = Trader()

        from lumibot.brokers import Tradier

        from credentials import TRADIER_CONFIG

        broker = Tradier(TRADIER_CONFIG)

        strategy = StrategyTemplate(
            broker=broker,
            discord_webhook_url=os.environ.get("DISCORD_WEBHOOK_URL"),
            account_history_db_connection_str=os.environ.get(
                "ACCOUNT_HISTORY_DB_CONNECTION_STR"
            ),
        )
        trader.add_strategy(strategy)
        trader.run_all()

    else:
        ############################################
        # Backtest the strategy
        ############################################
        from credentials import POLYGON_CONFIG

        ####
        # Configuration Options
        ####

        backtesting_start = datetime(2023, 3, 1)
        backtesting_end = datetime(2024, 2, 8)
        trading_fee = TradingFee(percent_fee=0.001)  # 0.1% fee per trade

        # Set the name of the strategy based on the parameters
        params = StrategyTemplate.parameters
        strategy_name = f"Overnight Pop Trade on {params['symbol']} with {params['days_to_expiration']} DTE"

        ####
        # Start Backtesting
        ####

        StrategyTemplate.backtest(
            PolygonDataBacktesting,
            backtesting_start,
            backtesting_end,
            benchmark_asset="SPY",
            buy_trading_fees=[trading_fee],
            sell_trading_fees=[trading_fee],
            polygon_api_key=POLYGON_CONFIG["API_KEY"],
            polygon_has_paid_subscription=False,
            name=strategy_name,
        )
