"""
Credentials Configuration for Lumibot Strategies

This file manages API keys and configuration settings for live trading and backtesting.
Copy this to credentials.py and fill in your actual API keys.

IMPORTANT: Never commit credentials.py to version control!
Add credentials.py to .gitignore
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================================================================
# BACKTESTING MODE
# ================================================================
# Set to True to run backtests, False for live trading
IS_BACKTESTING = True

# ================================================================
# POLYGON.IO CONFIGURATION (For Backtesting & Live Data)
# ================================================================
POLYGON_CONFIG = {
    "API_KEY": os.getenv("POLYGON_API_KEY", "your_polygon_api_key_here"),

    # Set to True if you have a paid Polygon.io subscription
    # FREE tier does NOT include historical options data!
    # Required plans:
    #   - Starter ($29/month): Stock data only
    #   - Developer ($99/month): Includes options data
    #   - Advanced ($199/month): Real-time + historical options
    "HAS_PAID_SUBSCRIPTION": True,  # Set to False if using free tier
}

# ================================================================
# TRADIER CONFIGURATION (For Live Trading)
# ================================================================
# Tradier Brokerage: https://www.tradier.com/
TRADIER_CONFIG = {
    "ACCESS_TOKEN": os.getenv("TRADIER_ACCESS_TOKEN", "your_tradier_token_here"),
    "ACCOUNT_NUMBER": os.getenv("TRADIER_ACCOUNT_NUMBER", "your_account_number_here"),

    # Set to True for paper trading (recommended for testing)
    "PAPER": True,  # Change to False for real trading
}

# ================================================================
# ALPACA CONFIGURATION (Alternative Broker)
# ================================================================
# Alpaca: https://alpaca.markets/
ALPACA_CONFIG = {
    "API_KEY": os.getenv("ALPACA_API_KEY", "your_alpaca_key_here"),
    "API_SECRET": os.getenv("ALPACA_API_SECRET", "your_alpaca_secret_here"),

    # Paper trading endpoint vs live endpoint
    # Paper: https://paper-api.alpaca.markets
    # Live: https://api.alpaca.markets
    "PAPER": True,  # Change to False for real trading
}

# ================================================================
# INTERACTIVE BROKERS CONFIGURATION
# ================================================================
# Interactive Brokers TWS/Gateway connection
IB_CONFIG = {
    "SOCKET_PORT": 7497,  # TWS paper: 7497, TWS live: 7496
    "CLIENT_ID": 1,
    "IP": "127.0.0.1",
}

# ================================================================
# OTHER DATA SOURCES
# ================================================================

# Yahoo Finance (Free, but no options data)
# No configuration needed - works out of the box

# Barchart Configuration (Alternative data provider)
BARCHART_CONFIG = {
    "API_KEY": os.getenv("BARCHART_API_KEY", "your_barchart_key_here"),
}

# Databento Configuration (Professional market data)
DATABENTO_CONFIG = {
    "API_KEY": os.getenv("DATABENTO_API_KEY", "your_databento_key_here"),
}

# ================================================================
# DISCORD NOTIFICATIONS (Optional)
# ================================================================
# Discord webhook for trade notifications
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", None)

# ================================================================
# DATABASE CONFIGURATION (Optional - for storing trade history)
# ================================================================
# PostgreSQL connection string for account history
ACCOUNT_HISTORY_DB_CONNECTION_STR = os.getenv(
    "ACCOUNT_HISTORY_DB_CONNECTION_STR",
    None  # Example: "postgresql://user:password@localhost:5432/trading_history"
)

# ================================================================
# STRATEGY-SPECIFIC SETTINGS
# ================================================================

# General trading settings
GENERAL_SETTINGS = {
    "LOG_LEVEL": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "SAVE_TEARSHEET": True,  # Save backtest tearsheet HTML
    "ENABLE_NOTIFICATIONS": False,  # Send Discord notifications
}

# Risk management defaults
RISK_SETTINGS = {
    "MAX_POSITION_SIZE_PCT": 0.20,  # Max 20% of portfolio per position
    "MAX_PORTFOLIO_DRAWDOWN_PCT": 0.10,  # Stop trading if down 10%
    "MIN_CASH_RESERVE": 5000,  # Always keep $5k in cash
}

# ================================================================
# VALIDATION
# ================================================================

def validate_config():
    """Validate configuration before running strategies"""

    if IS_BACKTESTING:
        print("✅ Running in BACKTESTING mode")

        # Check Polygon.io configuration
        if POLYGON_CONFIG["API_KEY"] == "your_polygon_api_key_here":
            print("⚠️  WARNING: Polygon.io API key not set!")
            print("   Set POLYGON_API_KEY in .env file")
            return False

        if not POLYGON_CONFIG["HAS_PAID_SUBSCRIPTION"]:
            print("⚠️  WARNING: Free Polygon.io tier does NOT include options data")
            print("   Upgrade to Developer plan ($99/month) for options backtesting")
            print("   See: https://polygon.io/pricing")

        print(f"✅ Polygon.io configured (Paid: {POLYGON_CONFIG['HAS_PAID_SUBSCRIPTION']})")

    else:
        print("🔴 Running in LIVE TRADING mode")

        # Check broker configuration
        if TRADIER_CONFIG["ACCESS_TOKEN"] == "your_tradier_token_here":
            print("⚠️  WARNING: Tradier access token not set!")
            return False

        if TRADIER_CONFIG["PAPER"]:
            print("✅ Tradier configured (PAPER TRADING mode)")
        else:
            print("🔴 Tradier configured (LIVE TRADING mode)")
            print("⚠️  WARNING: Real money at risk!")

            response = input("Are you sure you want to trade LIVE? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Aborting for safety")
                return False

    return True

# ================================================================
# USAGE EXAMPLE
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Lumibot Credentials Configuration")
    print("=" * 60)

    if validate_config():
        print("\n✅ Configuration valid!")
        print("\nCurrent settings:")
        print(f"  - Backtesting: {IS_BACKTESTING}")
        print(f"  - Polygon.io: {POLYGON_CONFIG['HAS_PAID_SUBSCRIPTION']}")
        print(f"  - Paper trading: {TRADIER_CONFIG.get('PAPER', True)}")
    else:
        print("\n❌ Configuration invalid - please check settings")
