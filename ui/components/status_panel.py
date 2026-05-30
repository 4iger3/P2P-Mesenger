"""
Status panel component for displaying connection and message statistics.
Fully theme-aware panel for displaying application status.
"""

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """
    Status panel showing connection state and message count.
    All colors are theme-driven.
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager=None) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=8)
        self.theme_manager = theme_manager
        self.grid_columnconfigure(0, weight=1)
        self.message_count = 0

        # Subscribe to theme changes
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Disconnected", font=("", 10))
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Message count
        self.message_count_label = ctk.CTkLabel(self, text="Messages: 0", font=("", 9))
        self.message_count_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

        # Update colors
        self._update_colors()

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()

        # Update frame
        self.configure(fg_color=theme.get_color("panel_bg"))

        # Update labels
        self.status_label.configure(text_color=theme.get_color("status_disconnected"))
        self.message_count_label.configure(text_color=theme.get_color("text_secondary"))

    def set_status(self, text: str, is_connected: bool = False) -> None:
        """Update the status text and color."""
        if self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            color = theme.get_color("status_connected") if is_connected else theme.get_color("status_disconnected")
        else:
            color = "#4CAF50" if is_connected else "#ff6b6b"
        self.status_label.configure(text=text, text_color=color)

    def set_message_count(self, count: int) -> None:
        """Set the message count."""
        self.message_count = count
        self.message_count_label.configure(text=f"Messages: {count}")

    def increment_message_count(self) -> None:
        """Increment the message count."""
        self.message_count += 1
        self.message_count_label.configure(text=f"Messages: {self.message_count}")
