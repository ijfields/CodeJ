"""
Global emoji configuration for the AI Trading Platform
Set your preferences here to control emoji behavior across the entire project
"""

# Emoji Configuration Settings
EMOJI_CONFIG = {
    # Set to True to enable emoji fallback mode (converts emojis to text on encoding errors)
    # Set to False to raise errors when emojis can't be displayed
    'fallback_mode': True,
    
    # Text encoding to use for emoji output
    'encoding': 'utf-8',
    
    # Set to True to automatically configure emoji handling on import
    'auto_configure': True,
    
    # Custom emoji mappings (emoji -> text replacement)
    'custom_mappings': {
        # Add your custom emoji mappings here
        # '🎯': '[CUSTOM_TARGET]',
    }
}

# Auto-configure emoji handling if enabled
if EMOJI_CONFIG['auto_configure']:
    try:
        from src.utils.emoji_safe import configure_emoji_handling
        configure_emoji_handling(
            fallback_mode=EMOJI_CONFIG['fallback_mode'],
            encoding=EMOJI_CONFIG['encoding']
        )
    except ImportError:
        # Handle case where src.utils is not available
        pass