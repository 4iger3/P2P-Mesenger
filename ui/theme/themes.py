"""
Theme definitions for the P2P Messenger application.

Contains predefined color palettes and theme configurations.
"""

from typing import Dict, Any


class Theme:
    """
    Base theme class defining the color palette structure.
    """

    def __init__(self, name: str, colors: Dict[str, str]) -> None:
        self.name = name
        self.colors = colors

    def get_color(self, key: str) -> str:
        """Get a color value by key."""
        return self.colors.get(key, "#000000")


# Predefined themes
DARK_BLUE_THEME = Theme("Dark Blue", {
    # Background colors
    "bg_primary": "#0f172a",      # Main background
    "bg_secondary": "#1e1e2e",    # Panel backgrounds
    "bg_tertiary": "#2a2d3a",     # Input fields, buttons
    "bg_accent": "#1e293b",       # Accent backgrounds

    # Text colors
    "text_primary": "#ffffff",    # Primary text
    "text_secondary": "#c0c0c0",  # Secondary text
    "text_muted": "#8b98a5",      # Muted text
    "text_accent": "#60a5fa",     # Accent text (usernames, links)

    # Border colors
    "border_primary": "#404040",  # Primary borders
    "border_secondary": "#555555", # Secondary borders

    # Status colors
    "status_connected": "#4CAF50",    # Connected status
    "status_disconnected": "#ff6b6b", # Disconnected status
    "status_online": "#4CAF50",       # Online indicator

    # Message bubble colors
    "bubble_own": "#2b5278",      # Own messages
    "bubble_other": "#182533",   # Other messages
    "bubble_system": "#2a2d3a",  # System messages

    # Button colors
    "button_primary": "#4CAF50",     # Primary buttons
    "button_primary_hover": "#45a049",
    "button_danger": "#f44336",      # Danger buttons
    "button_danger_hover": "#da190b",

    # Input/form colors
    "input_bg": "#2a2d3a",           # Input field background
    "input_text": "#ffffff",         # Input field text
    "input_border": "#404040",       # Input field border

    # Component-specific colors
    "chat_bg": "#0f172a",            # Chat area background
    "chat_text": "#ffffff",          # Chat text
    "sidebar_bg": "#1e1e2e",         # Sidebar background
    "sidebar_text": "#ffffff",       # Sidebar text
    "panel_bg": "#2a2d3a",           # Panel background
    "panel_secondary": "#1e1e2e",    # Secondary panel color
    
    # Scrollbar colors
    "scrollbar_fg": "#404040",       # Scrollbar foreground
    "scrollbar_button": "#555555",   # Scrollbar button

    # User list colors
    "userlist_bg": "#1e1e2e",        # User list background

    # Accent color (customizable)
    "accent": "#4CAF50"
})

DISCORD_THEME = Theme("Discord Style", {
    # Background colors
    "bg_primary": "#36393f",      # Discord dark background
    "bg_secondary": "#2f3136",    # Channel/sidebar background
    "bg_tertiary": "#40444b",     # Input fields
    "bg_accent": "#202225",       # Accent backgrounds

    # Text colors
    "text_primary": "#ffffff",    # Primary text
    "text_secondary": "#b9bbbe",  # Secondary text
    "text_muted": "#72767d",      # Muted text
    "text_accent": "#00aff4",     # Accent text

    # Border colors
    "border_primary": "#202225",  # Primary borders
    "border_secondary": "#40444b", # Secondary borders

    # Status colors
    "status_connected": "#43b581",    # Discord green
    "status_disconnected": "#f04747", # Discord red
    "status_online": "#43b581",       # Online indicator

    # Message bubble colors
    "bubble_own": "#4f545c",      # Own messages (Discord style)
    "bubble_other": "#36393f",    # Other messages
    "bubble_system": "#2f3136",   # System messages

    # Button colors
    "button_primary": "#5865f2",      # Discord blurple
    "button_primary_hover": "#4752c4",
    "button_danger": "#f04747",       # Discord red
    "button_danger_hover": "#d84040",

    # Input/form colors
    "input_bg": "#40444b",           # Input field background
    "input_text": "#ffffff",         # Input field text
    "input_border": "#202225",       # Input field border

    # Component-specific colors
    "chat_bg": "#36393f",            # Chat area background
    "chat_text": "#ffffff",          # Chat text
    "sidebar_bg": "#2f3136",         # Sidebar background
    "sidebar_text": "#ffffff",       # Sidebar text
    "panel_bg": "#40444b",           # Panel background
    "panel_secondary": "#2f3136",    # Secondary panel color
    
    # Scrollbar colors
    "scrollbar_fg": "#202225",       # Scrollbar foreground
    "scrollbar_button": "#40444b",   # Scrollbar button

    # User list colors
    "userlist_bg": "#2f3136",        # User list background

    # Accent color
    "accent": "#5865f2"
})

TELEGRAM_THEME = Theme("Telegram Style", {
    # Background colors
    "bg_primary": "#ffffff",      # Telegram light background
    "bg_secondary": "#f0f0f0",    # Panel backgrounds
    "bg_tertiary": "#ffffff",     # Input fields - WHITE in light theme
    "bg_accent": "#c4f1f1",       # Accent backgrounds

    # Text colors
    "text_primary": "#000000",    # Primary text - BLACK for light theme
    "text_secondary": "#666666",  # Secondary text
    "text_muted": "#999999",      # Muted text
    "text_accent": "#0088cc",     # Telegram blue

    # Border colors
    "border_primary": "#cccccc",  # Primary borders
    "border_secondary": "#dddddd", # Secondary borders

    # Status colors
    "status_connected": "#4CAF50",    # Green
    "status_disconnected": "#ff6b6b", # Red
    "status_online": "#4CAF50",       # Online indicator

    # Message bubble colors
    "bubble_own": "#0088cc",      # Telegram blue for own messages
    "bubble_other": "#e1f5fe",    # Light blue for others
    "bubble_system": "#f0f0f0",   # System messages

    # Button colors
    "button_primary": "#0088cc",      # Telegram blue
    "button_primary_hover": "#0077b3",
    "button_danger": "#ff6b6b",       # Red
    "button_danger_hover": "#ff5252",

    # Input/form colors - WHITE background with BLACK text
    "input_bg": "#ffffff",           # Input field background - WHITE
    "input_text": "#000000",         # Input field text - BLACK
    "input_border": "#cccccc",       # Input field border

    # Component-specific colors
    "chat_bg": "#ffffff",            # Chat area background
    "chat_text": "#000000",          # Chat text - BLACK
    "sidebar_bg": "#f0f0f0",         # Sidebar background
    "sidebar_text": "#000000",       # Sidebar text - BLACK
    "panel_bg": "#f0f0f0",           # Panel background
    "panel_secondary": "#ffffff",    # Secondary panel color
    
    # Scrollbar colors
    "scrollbar_fg": "#cccccc",       # Scrollbar foreground
    "scrollbar_button": "#dddddd",   # Scrollbar button

    # User list colors
    "userlist_bg": "#f0f0f0",        # User list background

    # Accent color
    "accent": "#0088cc"
})

# Available themes
AVAILABLE_THEMES = {
    "dark_blue": DARK_BLUE_THEME,
    "discord": DISCORD_THEME,
    "telegram": TELEGRAM_THEME,
}

# Light mode variants
LIGHT_MODE_THEMES = {
    "telegram": TELEGRAM_THEME,  # Telegram theme is already light
}