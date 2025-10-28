#!/usr/bin/env python3
"""
Example demonstrating emoji-safe printing functionality
This script shows how to use emojis in your Python code without runtime errors
"""

# Import the emoji-safe utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.emoji_safe import (
    safe_print, 
    configure_emoji_handling, 
    get_emoji_support,
    print_success,
    print_chart_up,
    print_chart_down,
    print_money,
    print_warning,
    print_error,
    print_info
)

def main():
    """Demonstrate emoji-safe printing functionality"""
    
    print("=" * 50)
    print("EMOJI-SAFE PRINTING DEMONSTRATION")
    print("=" * 50)
    
    # Check if emojis are supported in current environment
    emoji_support = get_emoji_support()
    print(f"Emoji support: {'✅ Yes' if emoji_support else '❌ No'}")
    print()
    
    # Example 1: Basic safe_print usage
    print("1. Basic safe_print usage:")
    safe_print("🚀 Trading strategy started!")
    safe_print("📈 Market is looking bullish today")
    safe_print("💰 Profit target: $1,000")
    print()
    
    # Example 2: Using convenience functions
    print("2. Convenience functions:")
    print_success("Strategy executed successfully!")
    print_chart_up("SPY is up 2.5% today")
    print_chart_down("QQQ dropped 1.2%")
    print_money("Portfolio value: $50,000")
    print_warning("High volatility detected")
    print_error("Connection to broker failed")
    print_info("Market opens in 30 minutes")
    print()
    
    # Example 3: Mixed content with emojis
    print("3. Mixed content:")
    safe_print("🎯 Target price: $450 | Current: $445 | Stop: $440")
    safe_print("⚡ Quick trade: Buy SPY calls at $2.50")
    safe_print("🔍 Analyzing market sentiment...")
    print()
    
    # Example 4: Trading simulation
    print("4. Trading simulation:")
    trades = [
        ("SPY", "CALL", 450, 2.50, "🚀"),
        ("QQQ", "PUT", 380, 1.80, "📉"),
        ("TSLA", "CALL", 250, 5.20, "⚡"),
    ]
    
    for symbol, option_type, strike, price, emoji in trades:
        safe_print(f"{emoji} {symbol} {option_type} ${strike} @ ${price}")
    
    print()
    print("=" * 50)
    print("Demo completed! 🎉")
    print("=" * 50)

if __name__ == "__main__":
    main()
