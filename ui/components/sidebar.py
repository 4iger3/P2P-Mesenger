"""
Sidebar component for the P2P Messenger.

Contains connection controls, server settings, and status information.
Fully theme-aware with support for light and dark modes.
"""

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """
    Left sidebar panel containing auxiliary actions.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        connection_settings_command: callable = None,
        settings_command: callable = None,
        theme_manager=None,
    ) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=10)
        self.theme_manager = theme_manager
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        title_label = ctk.CTkLabel(self, text="Actions", font=("", 14, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        self.title_label = title_label

        self.connection_settings_button = ctk.CTkButton(
            self,
            text="Connection Settings",
            command=connection_settings_command,
            width=180,
        )
        self.connection_settings_button.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        self.settings_button = ctk.CTkButton(
            self,
            text="Settings",
            command=settings_command,
            width=180,
        )
        self.settings_button.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))

        self._update_colors()

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()
        self.configure(fg_color=theme.get_color("sidebar_bg"))
        self.title_label.configure(text_color=theme.get_color("text_primary"))

        for button in [self.connection_settings_button, self.settings_button]:
            button.configure(
                fg_color=theme.get_color("button_primary"),
                hover_color=theme.get_color("button_primary_hover"),
                text_color=theme.get_color("text_primary"),
            )

