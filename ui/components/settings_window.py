"""
Settings window component for the P2P Messenger application.

Provides a separate popup window for theme customization.
"""

import customtkinter as ctk
from .theme_settings import ThemeSettings
from ..theme.theme_manager import ThemeManager


class SettingsWindow(ctk.CTkToplevel):
    """
    A non-modal settings window for theme selection and accent color.
    """

    def __init__(self, parent: ctk.CTk, theme_manager: ThemeManager) -> None:
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = theme_manager

        self.title("Settings")
        self.geometry("400x500")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.theme_settings = ThemeSettings(self.container, self.theme_manager)
        self.theme_settings.grid(row=0, column=0, sticky="nsew")

        if self.theme_manager:
            self.theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        self._update_colors()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_theme_changed(self, theme) -> None:
        """Update window colors when the theme changes."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Apply theme colors to the settings window."""
        theme = self.theme_manager.get_current_theme()
        self.configure(fg_color=theme.get_color("bg_secondary"))
        self.container.configure(fg_color=theme.get_color("bg_secondary"))

    def _on_close(self) -> None:
        """Cleanly close the settings window and unsubscribe from theme updates."""
        if self.theme_manager:
            self.theme_manager.unsubscribe_from_theme_changes(self._on_theme_changed)
        self.destroy()
