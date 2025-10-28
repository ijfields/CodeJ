#!/usr/bin/env python3
"""
Custom Backtesting Class for Pandas Options Data Source

Extends Lumibot's backtesting framework to work with PandasOptionsDataSource.
"""

from datetime import datetime
from typing import Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from lumibot.backtesting import BacktestingBroker
from DataTools.pandas_options_data_source import PandasOptionsDataSource


class PandasBacktesting:
    """
    Backtesting class that integrates PandasOptionsDataSource with Lumibot strategies.

    Usage:
        results = MyStrategy.run_backtest(
            PandasBacktesting,
            start_date,
            end_date,
            parameters=strategy_params,
            data_dir="data/lumibot"
        )
    """

    # This flag tells Lumibot this is a valid backtesting class
    IS_BACKTESTING_BROKER = True

    def __init__(self,
                 datetime_start: datetime,
                 datetime_end: datetime,
                 data_dir: str = "data/lumibot",
                 **kwargs):
        """
        Initialize the backtesting environment with pandas data source.

        Args:
            datetime_start: Start date for backtest
            datetime_end: End date for backtest
            data_dir: Directory containing stock_data.pkl and options_data.pkl
            **kwargs: Additional arguments passed to BacktestingBroker
        """
        self.datetime_start = datetime_start
        self.datetime_end = datetime_end
        self.data_dir = data_dir

        print(f"\n[OK] Initializing PandasBacktesting")
        print(f"     Data directory: {data_dir}")
        print(f"     Period: {datetime_start.date()} to {datetime_end.date()}")

        # Load the data source
        self.data_source = PandasOptionsDataSource(data_dir=data_dir)

        # Create the backtesting broker with our data source
        # Don't pass kwargs - they're for other components
        self.broker = BacktestingBroker(data_source=self.data_source)

        # Override broker methods to use our data source
        print(f"[OK] Broker initialized - data source will be used automatically")

    def _patch_broker_DEPRECATED(self):
        """
        Patch the broker's data retrieval methods to use our data source.
        """
        # Store reference to our data source in the broker
        self.broker._pandas_data_source = self.data_source

        # Override get_chains to use our data source
        original_get_chains = self.broker.get_chains

        def patched_get_chains(asset, quote=None):
            result = self.data_source.get_chains(asset, quote)
            if result:
                # Lumibot expects {' Chains': chains} format
                return {'Chains': result}
            return original_get_chains(asset, quote)

        self.broker.get_chains = patched_get_chains

        # Override get_last_price to use our data source
        original_get_last_price = self.broker.get_last_price

        def patched_get_last_price(asset):
            result = self.data_source.get_last_price(asset)
            if result is not None:
                return result
            return original_get_last_price(asset)

        self.broker.get_last_price = patched_get_last_price

        # Override get_historical_prices to use our data source
        original_get_historical_prices = self.broker.get_historical_prices

        def patched_get_historical_prices(asset, length, timestep="1D", timeshift=None, chunk_size=100, quote=None):
            result = self.data_source.get_historical_prices(asset, length, timestep)
            if result is not None:
                return result
            return original_get_historical_prices(asset, length, timestep, timeshift, chunk_size, quote)

        self.broker.get_historical_prices = patched_get_historical_prices

        print(f"[OK] Broker patched with custom data source methods")

    def run(self, strategy_class, parameters=None, **kwargs):
        """
        Run the backtest with the specified strategy.

        Args:
            strategy_class: The strategy class to backtest
            parameters: Dictionary of strategy parameters
            **kwargs: Additional arguments

        Returns:
            Backtest results
        """
        from lumibot.traders import Trader

        print(f"\n[OK] Starting backtest with {strategy_class.__name__}")

        # Create strategy instance
        strategy = strategy_class(
            broker=self.broker,
            parameters=parameters or {}
        )

        # Create trader and add strategy
        trader = Trader()
        trader.add_strategy(strategy)

        # Run the backtest
        trader.run_all(
            between_dates=[self.datetime_start, self.datetime_end],
            show_plot=kwargs.get('show_plot', False),
            show_tearsheet=kwargs.get('show_tearsheet', True),
            save_tearsheet=kwargs.get('save_tearsheet', True)
        )

        # Return results
        if hasattr(trader, 'results') and trader.results:
            return trader.results[0]

        return None


# Make it compatible with Lumibot's run_backtest() method
def create_backtesting_broker(datetime_start, datetime_end, data_dir="data/lumibot", **kwargs):
    """
    Factory function to create a PandasBacktesting instance.

    This allows it to be used with Strategy.run_backtest() like:
        results = MyStrategy.run_backtest(
            PandasBacktesting,
            start_date,
            end_date,
            parameters=params,
            data_dir="data/lumibot"
        )
    """
    return PandasBacktesting(datetime_start, datetime_end, data_dir=data_dir, **kwargs)
