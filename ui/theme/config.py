"""
Theme configuration management for the P2P Messenger application.

Handles loading, saving, and managing theme settings.
"""

import json
import os
from typing import Dict, Any, Optional
from .themes import AVAILABLE_THEMES, Theme


class ThemeConfig:
    """
    Manages theme configuration persistence and loading.
    """

    def __init__(self, config_file: str = "config/theme_config.json") -> None:
        self.config_file = config_file
        self.config_dir = os.path.dirname(config_file)
        self._ensure_config_dir()

        # Default configuration
        self.default_config = {
            "theme": "dark_blue",
            "mode": "dark",  # "dark" or "light"
            "accent_color": "#4CAF50",
            "custom_colors": {}
        }

        self.config = self._load_config()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load theme config: {e}")
                return self.default_config.copy()
        return self.default_config.copy()

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save theme config: {e}")

    def get_theme_name(self) -> str:
        """Get the current theme name."""
        return self.config.get("theme", "dark_blue")

    def set_theme_name(self, theme_name: str) -> None:
        """Set the current theme name."""
        if theme_name in AVAILABLE_THEMES:
            self.config["theme"] = theme_name
            self.save_config()

    def get_mode(self) -> str:
        """Get the current mode (dark/light)."""
        return self.config.get("mode", "dark")

    def set_mode(self, mode: str) -> None:
        """Set the current mode."""
        if mode in ["dark", "light"]:
            self.config["mode"] = mode
            self.save_config()

    def get_accent_color(self) -> str:
        """Get the current accent color."""
        return self.config.get("accent_color", "#4CAF50")

    def set_accent_color(self, color: str) -> None:
        """Set the accent color."""
        self.config["accent_color"] = color
        self.save_config()

    def get_custom_colors(self) -> Dict[str, str]:
        """Get custom color overrides."""
        return self.config.get("custom_colors", {})

    def set_custom_color(self, key: str, color: str) -> None:
        """Set a custom color override."""
        if "custom_colors" not in self.config:
            self.config["custom_colors"] = {}
        self.config["custom_colors"][key] = color
        self.save_config()

    def get_current_theme(self) -> Theme:
        """Get the current theme object."""
        theme_name = self.get_theme_name()
        theme = AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES["dark_blue"])

        # Apply custom colors
        custom_colors = self.get_custom_colors()
        if custom_colors:
            theme_colors = theme.colors.copy()
            theme_colors.update(custom_colors)
            theme = Theme(theme.name, theme_colors)

        return theme