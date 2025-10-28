"""
Emoji-safe printing utilities for AI Trading Platform
Handles Unicode emoji encoding issues gracefully
"""

import sys
import os
from typing import Any, Optional


class EmojiSafePrinter:
    """
    A printer that handles emoji encoding issues gracefully
    """
    
    def __init__(self, fallback_mode: bool = True, encoding: str = 'utf-8'):
        self.fallback_mode = fallback_mode
        self.encoding = encoding
        self._emoji_support = self._check_emoji_support()
    
    def _check_emoji_support(self) -> bool:
        """Check if the current environment supports emojis"""
        try:
            # Test emoji output
            test_emoji = "🚀"
            print(test_emoji, end='', flush=True)
            # If we get here without error, emojis are supported
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
        except Exception:
            return False
    
    def safe_print(self, *args, **kwargs) -> None:
        """
        Print with emoji safety - automatically handles encoding issues
        """
        try:
            print(*args, **kwargs)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if self.fallback_mode:
                # Convert emojis to text equivalents
                safe_args = []
                for arg in args:
                    if isinstance(arg, str):
                        safe_args.append(self._emoji_to_text(arg))
                    else:
                        safe_args.append(str(arg))
                print(*safe_args, **kwargs)
            else:
                # Re-raise the error
                raise e
    
    def _emoji_to_text(self, text: str) -> str:
        """Convert common emojis to text equivalents"""
        emoji_map = {
            '🚀': '[ROCKET]',
            '📈': '[CHART_UP]',
            '📉': '[CHART_DOWN]',
            '💰': '[MONEY]',
            '⚡': '[LIGHTNING]',
            '🎯': '[TARGET]',
            '✅': '[CHECK]',
            '❌': '[X]',
            '⚠️': '[WARNING]',
            '🔍': '[SEARCH]',
            '📊': '[CHART]',
            '🎉': '[PARTY]',
            '🔥': '[FIRE]',
            '💡': '[BULB]',
            '🔄': '[REFRESH]',
            '🎪': '[CIRCUS]',
            '🏆': '[TROPHY]',
            '⭐': '[STAR]',
            '🎨': '[ART]',
            '🚨': '[ALERT]',
            '💎': '[DIAMOND]',
            '🎲': '[DICE]',
            '🎭': '[MASK]',
            '🎪': '[TENT]',
            '🎯': '[DART]',
            '🛸': '[UFO]',
            '📝': '[MEMO]',
            '⏰': '[CLOCK]',
        }
        
        result = text
        for emoji, replacement in emoji_map.items():
            result = result.replace(emoji, replacement)
        
        return result


# Global instance
_emoji_printer = EmojiSafePrinter()


def safe_print(*args, **kwargs) -> None:
    """
    Global safe print function that handles emojis gracefully
    Usage: safe_print("🚀 Trading started!")
    """
    _emoji_printer.safe_print(*args, **kwargs)


def configure_emoji_handling(fallback_mode: bool = True, encoding: str = 'utf-8') -> None:
    """
    Configure global emoji handling behavior
    
    Args:
        fallback_mode: If True, convert emojis to text on encoding errors
        encoding: Text encoding to use
    """
    global _emoji_printer
    _emoji_printer = EmojiSafePrinter(fallback_mode=fallback_mode, encoding=encoding)


def get_emoji_support() -> bool:
    """Check if current environment supports emojis"""
    return _emoji_printer._emoji_support


# Convenience functions for common trading emojis
def print_success(message: str) -> None:
    """Print success message with rocket emoji"""
    safe_print(f"🚀 {message}")


def print_chart_up(message: str) -> None:
    """Print chart up message"""
    safe_print(f"📈 {message}")


def print_chart_down(message: str) -> None:
    """Print chart down message"""
    safe_print(f"📉 {message}")


def print_money(message: str) -> None:
    """Print money-related message"""
    safe_print(f"💰 {message}")


def print_warning(message: str) -> None:
    """Print warning message"""
    safe_print(f"⚠️ {message}")


def print_error(message: str) -> None:
    """Print error message"""
    safe_print(f"❌ {message}")


def print_info(message: str) -> None:
    """Print info message"""
    safe_print(f"💡 {message}")
