# Emoji Usage Rules for AI Trading Platform

## 🚨 IMPORTANT: Always Use Emoji-Safe Printing

### Rule: Never use regular `print()` with emojis

❌ **WRONG:**
```python
print("🚀 Trading started!")  # This can cause encoding errors
```

✅ **CORRECT:**
```python
from src.utils.emoji_safe import safe_print
safe_print("🚀 Trading started!")  # This handles encoding gracefully
```

### Rule: Use convenience functions for common scenarios

✅ **BEST PRACTICE:**
```python
from src.utils.emoji_safe import print_success, print_warning, print_error

print_success("Trade executed!")  # 🚀 Trade executed!
print_warning("High volatility!")  # ⚠️ High volatility!
print_error("Connection failed")   # ❌ Connection failed
```

### Rule: Configure emoji handling globally

Edit `config/emoji_config.py` to set your preferences:
- `fallback_mode: True` - Converts emojis to text on encoding errors
- `auto_configure: True` - Automatically configures emoji handling

### Rule: Test emoji support in your environment

Run the example to verify emoji support:
```bash
python examples/emoji_safe_example.py
```

## Quick Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `safe_print()` | General emoji-safe printing | `safe_print("🚀 Message")` |
| `print_success()` | Success messages | `print_success("Done!")` |
| `print_chart_up()` | Bullish/upward trends | `print_chart_up("SPY +2%")` |
| `print_chart_down()` | Bearish/downward trends | `print_chart_down("QQQ -1%")` |
| `print_money()` | Financial information | `print_money("$50,000")` |
| `print_warning()` | Warnings | `print_warning("High risk!")` |
| `print_error()` | Errors | `print_error("Failed!")` |
| `print_info()` | Information | `print_info("Market opens soon")` |

## Why This Matters

- **Prevents runtime errors** when terminals don't support Unicode emojis
- **Maintains code readability** with emoji fallbacks like `[ROCKET]` instead of crashes
- **Consistent behavior** across different environments (Windows, Linux, macOS)
- **Professional output** that works in all deployment scenarios

## Remember

🎯 **Always import and use emoji-safe functions when using emojis in your Python code!**
