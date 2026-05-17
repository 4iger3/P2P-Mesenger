"""
Theme settings component for the P2P Messenger.

Allows users to customize themes, colors, and appearance settings.
"""

import tkinter as tk
import customtkinter as ctk
from ..theme.theme_manager import ThemeManager
from core.events.observer import Observer
from core.events.events import THEME_CHANGED, ACCENT_COLOR_CHANGED


class ThemeSettings(ctk.CTkFrame, Observer):
    """
    Theme settings panel with theme selection and customization options.
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager: ThemeManager) -> None:
        super().__init__(parent, fg_color="transparent")
        self.theme_manager = theme_manager
        self.grid_columnconfigure(0, weight=1)

        # Subscribe to theme changes
        theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Title
        title_label = ctk.CTkLabel(self, text="Theme Settings", font=("", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(10, 5))

        # Theme selection
        theme_frame = ctk.CTkFrame(self)
        theme_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(1, weight=1)

        theme_label = ctk.CTkLabel(theme_frame, text="Theme:", font=("", 10))
        theme_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.theme_var = tk.StringVar(value=theme_manager.config.get_theme_name())
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=list(theme_manager.get_available_themes().keys()),
            variable=self.theme_var,
            command=self._on_theme_selected
        )
        self.theme_menu.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Mode selection
        mode_frame = ctk.CTkFrame(self)
        mode_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        mode_frame.grid_columnconfigure(1, weight=1)

        mode_label = ctk.CTkLabel(mode_frame, text="Mode:", font=("", 10))
        mode_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.mode_var = tk.StringVar(value=theme_manager.config.get_mode())
        self.mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=["dark", "light"],
            variable=self.mode_var,
            command=self._on_mode_selected
        )
        self.mode_menu.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Accent color
        accent_frame = ctk.CTkFrame(self)
        accent_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        accent_frame.grid_columnconfigure(1, weight=1)

        accent_label = ctk.CTkLabel(accent_frame, text="Accent Color:", font=("", 10))
        accent_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.accent_var = tk.StringVar(value=theme_manager.config.get_accent_color())
        self.accent_entry = ctk.CTkEntry(
            accent_frame,
            textvariable=self.accent_var,
            placeholder_text="#4CAF50"
        )
        self.accent_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)

        # Apply button
        apply_button = ctk.CTkButton(
            self,
            text="Apply Accent Color",
            command=self._on_apply_accent
        )
        apply_button.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        # Update colors based on current theme
        self._update_colors()

    def _on_theme_selected(self, theme_name: str) -> None:
        """Handle theme selection."""
        self.theme_manager.set_theme(theme_name)

    def _on_mode_selected(self, mode: str) -> None:
        """Handle mode selection."""
        self.theme_manager.set_mode(mode)

    def _on_apply_accent(self) -> None:
        """Handle accent color application."""
        color = self.accent_var.get().strip()
        if color:
            self.theme_manager.set_accent_color(color)

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        theme = self.theme_manager.get_current_theme()

        # Update frame colors
        self.configure(fg_color=theme.get_color("bg_secondary"))

        # Update labels
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=theme.get_color("text_primary"))
            elif isinstance(child, ctk.CTkFrame):
                child.configure(fg_color=theme.get_color("bg_tertiary"))

        # Update entry
        if hasattr(self, 'accent_entry'):
            self.accent_entry.configure(
                fg_color=theme.get_color("bg_tertiary"),
                border_color=theme.get_color("border_primary")
            )

    def update(self, event) -> None:
        """Handle events from dispatcher."""
        # Theme events are handled through the theme manager subscription
        pass