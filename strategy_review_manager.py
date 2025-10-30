"""
Strategy Review Manager

Backend module for loading and parsing Lumibot strategies and backtest results.

This module provides abstraction layer for:
- Discovering and parsing strategy .py files
- Finding and loading backtest output files
- Parsing JSON/CSV data into usable formats
- Handling missing/corrupt files gracefully

Classes:
    StrategyLoader: Discover and parse strategy files
    BacktestManager: Load and parse backtest results

Functions:
    parse_run_id: Extract run ID from filename
    format_metric: Format metric values for display

Author: Claude Code Agent
Date: 2025-10-29
Version: 1.0 (Phase 1 MVP)
"""

import glob
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class StrategyLoader:
    """
    Handles loading and parsing of Lumibot strategy files.

    Responsibilities:
    - List all strategy .py files in Outputs/Strategies/
    - Extract strategy metadata (name, class, parameters)
    - Parse parameters dictionary from strategy code

    Attributes:
        strategies_dir (Path): Path to Outputs/Strategies/ directory
    """

    def __init__(self, strategies_dir: str = "Outputs/Strategies"):
        """
        Initialize StrategyLoader.

        Args:
            strategies_dir: Path to directory containing strategy .py files
        """
        self.strategies_dir = Path(strategies_dir)

    def list_strategies(self) -> List[str]:
        """
        List all strategy .py files in strategies directory.

        Returns:
            List of strategy filenames (e.g., ["ema_crossover_test.py", ...])
            Empty list if directory doesn't exist or contains no .py files

        Example:
            >>> loader = StrategyLoader()
            >>> strategies = loader.list_strategies()
            >>> print(strategies)
            ['ema_crossover_test.py', 'zero_loss_butterfly.py']
        """
        if not self.strategies_dir.exists():
            return []

        pattern = str(self.strategies_dir / "*.py")
        files = glob.glob(pattern)

        # Return just filenames, not full paths
        return [os.path.basename(f) for f in sorted(files)]

    def get_strategy_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Extract strategy metadata from .py file.

        Args:
            filepath: Path to strategy file (can be filename or full path)

        Returns:
            Dictionary with strategy metadata:
            {
                "name": str,           # Strategy filename without .py
                "class_name": str,     # Strategy class name
                "description": str,    # Docstring or ""
                "parameters": dict,    # Parameters dict
                "file_path": str,      # Absolute path
                "file_size": int,      # Size in bytes
                "modified_date": str   # Last modified ISO date
            }
            Returns None if file doesn't exist or can't be parsed

        Example:
            >>> loader = StrategyLoader()
            >>> info = loader.get_strategy_info("ema_crossover_test.py")
            >>> print(info['class_name'])
            'EMACrossoverStrategy'
        """
        # Handle both filename and full path
        if not os.path.isabs(filepath):
            filepath = str(self.strategies_dir / filepath)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract class name
            class_match = re.search(r'class\s+(\w+)\s*\(Strategy\)', content)
            class_name = class_match.group(1) if class_match else "Unknown"

            # Extract docstring (first triple-quoted string after class)
            docstring_match = re.search(
                r'class\s+\w+.*?"""(.*?)"""',
                content,
                re.DOTALL
            )
            description = docstring_match.group(1).strip() if docstring_match else ""

            # Extract parameters
            parameters = self.extract_parameters(filepath)

            # File metadata
            stat = os.stat(filepath)
            file_size = stat.st_size
            modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()

            return {
                "name": os.path.basename(filepath).replace('.py', ''),
                "class_name": class_name,
                "description": description,
                "parameters": parameters,
                "file_path": filepath,
                "file_size": file_size,
                "modified_date": modified_date
            }

        except Exception as e:
            print(f"Error parsing strategy file {filepath}: {e}")
            return None

    def extract_parameters(self, filepath: str) -> Dict[str, Any]:
        """
        Parse parameters dictionary from strategy file.

        Args:
            filepath: Path to strategy file

        Returns:
            Parameters dictionary from strategy, or empty dict if not found

        Implementation:
            Uses regex to extract the `parameters = {...}` dictionary.
            Evaluates the string as Python dict using ast.literal_eval for safety.

        Example:
            >>> loader = StrategyLoader()
            >>> params = loader.extract_parameters("ema_crossover_test.py")
            >>> print(params['symbol'])
            'SPY'
        """
        # Handle both filename and full path
        if not os.path.isabs(filepath):
            filepath = str(self.strategies_dir / filepath)

        if not os.path.exists(filepath):
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find parameters = {...} block
            # Match from 'parameters' to closing brace, handling nested braces
            pattern = r'parameters\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                return {}

            # Extract the dict content
            dict_str = '{' + match.group(1) + '}'

            # Use ast.literal_eval for safe evaluation
            import ast
            params = ast.literal_eval(dict_str)

            return params

        except Exception as e:
            print(f"Error extracting parameters from {filepath}: {e}")
            return {}


class BacktestManager:
    """
    Handles loading and parsing of backtest result files.

    Responsibilities:
    - Find all backtest runs for a strategy
    - Load backtest output files (JSON, CSV, HTML)
    - Parse metrics and trades data
    - Provide consistent data structures to UI

    Attributes:
        logs_dir (Path): Path to logs/ directory
    """

    def __init__(self, logs_dir: str = "logs"):
        """
        Initialize BacktestManager.

        Args:
            logs_dir: Path to directory containing backtest output files
        """
        self.logs_dir = Path(logs_dir)

    def list_backtests(self, strategy_name: str) -> List[Dict[str, Any]]:
        """
        Find all backtest runs for a strategy.

        Args:
            strategy_name: Strategy class name (e.g., "EMACrossoverStrategy")

        Returns:
            List of backtest run metadata dictionaries:
            [
                {
                    "run_id": str,          # Unique run identifier
                    "date": str,            # Run date (YYYY-MM-DD)
                    "time": str,            # Run time (HH:MM)
                    "symbol": str,          # Traded symbol
                    "start_date": str,      # Backtest start
                    "end_date": str,        # Backtest end
                    "total_return": float,  # % return or None
                    "sharpe": float,        # Sharpe ratio or None
                    "max_drawdown": float,  # % drawdown or None
                    "has_html": bool,       # Tearsheet exists?
                    "has_trades": bool      # Trades file exists?
                },
                ...
            ]
            Returns empty list if no backtests found

        Example:
            >>> manager = BacktestManager()
            >>> runs = manager.list_backtests("EMACrossoverStrategy")
            >>> print(runs[0]['run_id'])
            'EMACrossoverStrategy_2025-10-29_14-05_FoWcfI'
        """
        if not self.logs_dir.exists():
            return []

        # Find all settings.json files for this strategy
        pattern = str(self.logs_dir / f"{strategy_name}_*_settings.json")
        settings_files = glob.glob(pattern)

        backtests = []

        for settings_file in sorted(settings_files, reverse=True):
            try:
                # Parse run ID from filename
                run_id = parse_run_id(settings_file)

                # Extract date and time from run_id
                # Format: StrategyName_YYYY-MM-DD_HH-MM_hash
                parts = run_id.split('_')
                if len(parts) >= 4:
                    date = parts[-3]  # YYYY-MM-DD
                    time = parts[-2]  # HH-MM
                else:
                    date = "Unknown"
                    time = "Unknown"

                # Load settings to get symbol and date range
                settings = self.get_settings(run_id)
                symbol = settings.get('parameters', {}).get('symbol', 'Unknown') if settings else 'Unknown'
                start_date = settings.get('backtesting_start', '') if settings else ''
                end_date = settings.get('backtesting_end', '') if settings else ''

                # Format dates for display
                if start_date:
                    start_date = start_date.split('T')[0]  # Extract date part
                if end_date:
                    end_date = end_date.split('T')[0]

                # Load metrics from tearsheet.csv
                metrics_df = self.get_metrics_df(run_id)
                total_return = None
                sharpe = None
                max_drawdown = None

                if metrics_df is not None and not metrics_df.empty:
                    # Extract key metrics
                    total_return = self._extract_metric(metrics_df, 'Total Return', 'Strategy')
                    sharpe = self._extract_metric(metrics_df, 'Sharpe', 'Strategy')
                    max_drawdown = self._extract_metric(metrics_df, 'Max Drawdown', 'Strategy')

                # Check if files exist
                has_html = os.path.exists(str(self.logs_dir / f"{run_id}_tearsheet.html"))
                trades_csv = str(self.logs_dir / f"{run_id}_trades.csv")
                has_trades = os.path.exists(trades_csv) and os.path.getsize(trades_csv) > 100

                backtests.append({
                    "run_id": run_id,
                    "date": date,
                    "time": time.replace('-', ':'),  # Convert HH-MM to HH:MM
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_return": total_return,
                    "sharpe": sharpe,
                    "max_drawdown": max_drawdown,
                    "has_html": has_html,
                    "has_trades": has_trades
                })

            except Exception as e:
                print(f"Error processing backtest {settings_file}: {e}")
                continue

        return backtests

    def _extract_metric(self, metrics_df: pd.DataFrame, metric_name: str, column: str = 'Strategy') -> Optional[float]:
        """
        Extract a metric value from tearsheet DataFrame.

        Args:
            metrics_df: DataFrame from tearsheet.csv
            metric_name: Name of metric to extract
            column: Column name ('Strategy' or 'SPY')

        Returns:
            Float value or None if not found/parseable
        """
        try:
            row = metrics_df[metrics_df['Metric'] == metric_name]
            if row.empty:
                return None

            value_str = row[column].iloc[0]

            # Handle different formats
            if value_str == '-' or value_str == '' or pd.isna(value_str):
                return None

            # Remove % sign and convert to float
            if isinstance(value_str, str):
                value_str = value_str.rstrip('%')
                return float(value_str)

            return float(value_str)

        except (ValueError, KeyError, IndexError):
            return None

    def load_backtest_results(self, run_id: str) -> Dict[str, Any]:
        """
        Load all files for a backtest run.

        Args:
            run_id: Run identifier (e.g., "EMACrossoverStrategy_2025-10-29_14-05_FoWcfI")

        Returns:
            Dictionary with all backtest data:
            {
                "settings": dict,       # From settings.json
                "metrics_df": DataFrame,# From tearsheet.csv
                "trades_df": DataFrame, # From trades.csv
                "stats_df": DataFrame,  # From stats.csv
                "html_path": str,       # Path to HTML file or None
                "run_metadata": dict    # Extracted metadata
            }

        Example:
            >>> manager = BacktestManager()
            >>> results = manager.load_backtest_results(run_id)
            >>> print(results['settings']['parameters']['symbol'])
            'SPY'
        """
        return {
            "settings": self.get_settings(run_id),
            "metrics_df": self.get_metrics_df(run_id),
            "trades_df": self.get_trades_df(run_id),
            "stats_df": self.get_stats_df(run_id),
            "html_path": self._get_file_path(run_id, "tearsheet.html"),
            "run_metadata": self._extract_metadata(run_id)
        }

    def get_tearsheet_html(self, run_id: str) -> Optional[str]:
        """
        Read tearsheet HTML file content.

        Args:
            run_id: Run identifier

        Returns:
            HTML content as string, or None if file doesn't exist

        Example:
            >>> manager = BacktestManager()
            >>> html = manager.get_tearsheet_html(run_id)
            >>> if html:
            ...     print(f"HTML size: {len(html)} bytes")
        """
        html_path = self._get_file_path(run_id, "tearsheet.html")

        if not html_path or not os.path.exists(html_path):
            return None

        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading HTML file {html_path}: {e}")
            return None

    def get_metrics_df(self, run_id: str) -> Optional[pd.DataFrame]:
        """
        Parse tearsheet.csv into DataFrame.

        Args:
            run_id: Run identifier

        Returns:
            DataFrame with columns: Metric, SPY, Strategy
            Returns None if file doesn't exist or can't be parsed

        Example:
            >>> manager = BacktestManager()
            >>> df = manager.get_metrics_df(run_id)
            >>> return_row = df[df['Metric'] == 'Total Return']
            >>> print(return_row['Strategy'].iloc[0])
            '5.2%'
        """
        csv_path = self._get_file_path(run_id, "tearsheet.csv")

        if not csv_path or not os.path.exists(csv_path):
            return None

        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error reading tearsheet CSV {csv_path}: {e}")
            return None

    def get_trades_df(self, run_id: str) -> Optional[pd.DataFrame]:
        """
        Parse trades.csv into DataFrame.

        Args:
            run_id: Run identifier

        Returns:
            DataFrame with trade columns, or None if file doesn't exist
            Returns empty DataFrame if CSV has only headers (no trades)

        Example:
            >>> manager = BacktestManager()
            >>> df = manager.get_trades_df(run_id)
            >>> if df is not None and not df.empty:
            ...     print(f"Number of trades: {len(df)}")
        """
        csv_path = self._get_file_path(run_id, "trades.csv")

        if not csv_path or not os.path.exists(csv_path):
            return None

        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error reading trades CSV {csv_path}: {e}")
            return None

    def get_stats_df(self, run_id: str) -> Optional[pd.DataFrame]:
        """
        Parse stats.csv into DataFrame.

        Args:
            run_id: Run identifier

        Returns:
            DataFrame with time-series portfolio data, or None if file doesn't exist

        Example:
            >>> manager = BacktestManager()
            >>> df = manager.get_stats_df(run_id)
            >>> if df is not None:
            ...     print(df.columns.tolist())
            ['datetime', 'portfolio_value', 'cash', 'positions', 'return']
        """
        csv_path = self._get_file_path(run_id, "stats.csv")

        if not csv_path or not os.path.exists(csv_path):
            return None

        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as e:
            print(f"Error reading stats CSV {csv_path}: {e}")
            return None

    def get_settings(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse settings.json into dictionary.

        Args:
            run_id: Run identifier

        Returns:
            Settings dictionary, or None if file doesn't exist

        Example:
            >>> manager = BacktestManager()
            >>> settings = manager.get_settings(run_id)
            >>> print(settings['name'])
            'EMACrossoverStrategy'
        """
        json_path = self._get_file_path(run_id, "settings.json")

        if not json_path or not os.path.exists(json_path):
            return None

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading settings JSON {json_path}: {e}")
            return None

    def _get_file_path(self, run_id: str, file_type: str) -> Optional[str]:
        """
        Construct file path for a backtest run file.

        Args:
            run_id: Run identifier
            file_type: File type (e.g., "tearsheet.html", "trades.csv")

        Returns:
            Full file path as string, or None if logs directory doesn't exist
        """
        if not self.logs_dir.exists():
            return None

        return str(self.logs_dir / f"{run_id}_{file_type}")

    def _extract_metadata(self, run_id: str) -> Dict[str, Any]:
        """
        Extract metadata from run_id and files.

        Args:
            run_id: Run identifier

        Returns:
            Dictionary with extracted metadata
        """
        # Parse run_id components
        parts = run_id.split('_')

        metadata = {
            "strategy_class": parts[0] if parts else "Unknown",
            "run_id": run_id
        }

        if len(parts) >= 4:
            metadata["date"] = parts[-3]
            metadata["time"] = parts[-2].replace('-', ':')
            metadata["hash"] = parts[-1]

        return metadata


# Utility Functions

def parse_run_id(filename: str) -> str:
    """
    Extract run ID from backtest filename.

    Args:
        filename: Backtest filename or full path

    Returns:
        Run ID string (everything before file type)

    Example:
        >>> run_id = parse_run_id("EMACrossoverStrategy_2025-10-29_14-05_FoWcfI_settings.json")
        >>> print(run_id)
        'EMACrossoverStrategy_2025-10-29_14-05_FoWcfI'
    """
    # Get basename if full path
    basename = os.path.basename(filename)

    # Remove file extension and type
    # Pattern: {run_id}_{type}.{ext}
    # Remove everything after last underscore before extension
    name_parts = basename.rsplit('_', 1)
    if len(name_parts) == 2:
        # Remove extension from second part
        type_with_ext = name_parts[1]
        # If it's a known type, remove it
        if any(t in type_with_ext for t in ['settings', 'tearsheet', 'trades', 'stats']):
            return name_parts[0]

    # Fallback: just remove extension
    return os.path.splitext(basename)[0]


def format_metric(value: Any, metric_type: str = 'auto') -> str:
    """
    Format metric value for display.

    Args:
        value: Metric value to format
        metric_type: Format type ('percent', 'decimal', 'currency', 'auto')

    Returns:
        Formatted string for display

    Examples:
        >>> format_metric(0.1234, 'percent')
        '12.34%'
        >>> format_metric(1.5678, 'decimal')
        '1.57'
        >>> format_metric(10000, 'currency')
        '$10,000.00'
        >>> format_metric(None, 'auto')
        'N/A'
    """
    # Handle None, empty, or undefined
    if value is None or value == '' or value == '-':
        return 'N/A'

    # Handle already-formatted strings
    if isinstance(value, str):
        # If already has %, just return it
        if '%' in value:
            return value
        # If already has $, just return it
        if '$' in value:
            return value
        # Try to parse as number
        try:
            value = float(value.replace(',', ''))
        except (ValueError, AttributeError):
            return value

    # Auto-detect format based on magnitude
    if metric_type == 'auto':
        if abs(value) <= 1.0:
            metric_type = 'decimal'
        else:
            metric_type = 'decimal'

    # Format based on type
    if metric_type == 'percent':
        return f"{value:.2f}%"
    elif metric_type == 'decimal':
        return f"{value:.2f}"
    elif metric_type == 'currency':
        return f"${value:,.2f}"
    else:
        return str(value)


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Strategy Review Manager - Test")
    print("=" * 60)

    # Test StrategyLoader
    print("\n1. Testing StrategyLoader...")
    loader = StrategyLoader()
    strategies = loader.list_strategies()
    print(f"Found {len(strategies)} strategies:")
    for s in strategies:
        print(f"  - {s}")

    if strategies:
        print(f"\n2. Getting info for first strategy: {strategies[0]}")
        info = loader.get_strategy_info(strategies[0])
        if info:
            print(f"  Class: {info['class_name']}")
            print(f"  Parameters: {info['parameters']}")

    # Test BacktestManager
    print("\n3. Testing BacktestManager...")
    manager = BacktestManager()

    if strategies:
        # Get class name from first strategy
        info = loader.get_strategy_info(strategies[0])
        if info:
            class_name = info['class_name']
            print(f"\n4. Listing backtests for {class_name}...")
            backtests = manager.list_backtests(class_name)
            print(f"Found {len(backtests)} backtest runs:")
            for b in backtests[:3]:  # Show first 3
                print(f"  - {b['date']} {b['time']} | Symbol: {b['symbol']} | Return: {b['total_return']}")

            if backtests:
                print(f"\n5. Loading first backtest: {backtests[0]['run_id']}")
                results = manager.load_backtest_results(backtests[0]['run_id'])
                print(f"  Settings loaded: {results['settings'] is not None}")
                print(f"  Metrics loaded: {results['metrics_df'] is not None}")
                print(f"  Trades loaded: {results['trades_df'] is not None}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
