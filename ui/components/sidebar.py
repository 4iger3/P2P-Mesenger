"""
Sidebar component for the P2P Messenger.

Contains connection controls, server settings, and status information.
"""

import tkinter as tk
import customtkinter as ctk
from .theme_settings import ThemeSettings


class Sidebar(ctk.CTkFrame):
    """
    Left sidebar panel containing connection controls and status.
    """

    def __init__(self, parent: ctk.CTkFrame, ip_var: tk.StringVar, port_var: tk.StringVar,
                 username_var: tk.StringVar, connect_command: callable,
                 disconnect_command: callable, theme_manager=None) -> None:
        super().__init__(parent, fg_color="#1e1e2e", corner_radius=10)
        self.theme_manager = theme_manager
        self.grid_rowconfigure(10, weight=1)  # Increased for theme settings
        self.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(self, text="Connection", font=("", 14, "bold"),
                                   text_color="#ffffff")
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Server IP
        ip_label = ctk.CTkLabel(self, text="Server IP:", font=("", 10), text_color="#c0c0c0")
        ip_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 2))
        self.ip_entry = ctk.CTkEntry(self, textvariable=ip_var, width=180,
                                     fg_color="#2a2d3a", border_color="#404040")
        self.ip_entry.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Port
        port_label = ctk.CTkLabel(self, text="Port:", font=("", 10), text_color="#c0c0c0")
        port_label.grid(row=3, column=0, sticky="w", padx=15, pady=(5, 2))
        self.port_entry = ctk.CTkEntry(self, textvariable=port_var, width=180,
                                       fg_color="#2a2d3a", border_color="#404040")
        self.port_entry.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Username
        username_label = ctk.CTkLabel(self, text="Username:", font=("", 10), text_color="#c0c0c0")
        username_label.grid(row=5, column=0, sticky="w", padx=15, pady=(5, 2))
        self.username_entry = ctk.CTkEntry(self, textvariable=username_var, width=180,
                                           fg_color="#2a2d3a", border_color="#404040")
        self.username_entry.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 20))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, sticky="ew", padx=15, pady=(0, 15))
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self.connect_button = ctk.CTkButton(buttons_frame, text="Connect",
                                            command=connect_command, width=80,
                                            fg_color="#4CAF50", hover_color="#45a049")
        self.connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.disconnect_button = ctk.CTkButton(buttons_frame, text="Disconnect",
                                               command=disconnect_command, width=80,
                                               fg_color="#f44336", hover_color="#da190b")
        self.disconnect_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.disconnect_button.configure(state="disabled")

        # Status section
        status_frame = ctk.CTkFrame(self, fg_color="#2a2d3a", corner_radius=8)
        status_frame.grid(row=8, column=0, sticky="ew", padx=15, pady=(10, 15))
        status_frame.grid_columnconfigure(0, weight=1)

        status_title = ctk.CTkLabel(status_frame, text="Status", font=("", 12, "bold"),
                                    text_color="#ffffff")
        status_title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self.status_label = ctk.CTkLabel(status_frame, text="Disconnected",
                                         font=("", 10), text_color="#ff6b6b")
        self.status_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

        # Theme settings (if theme manager provided)
        if theme_manager:
            self.theme_settings = ThemeSettings(self, theme_manager)
            self.theme_settings.grid(row=9, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Subscribe to theme changes if theme manager exists
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()

        # Update main frame
        self.configure(fg_color=theme.get_color("bg_secondary"))

        # Update labels
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkLabel):
                child.configure(text_color=theme.get_color("text_primary"))
            elif isinstance(child, ctk.CTkFrame) and child != self.theme_settings:
                # Don't update theme_settings frame color as it handles its own
                if hasattr(child, 'fg_color') and child.fg_color != "transparent":
                    child.configure(fg_color=theme.get_color("bg_tertiary"))

        # Update entries
        for entry in [self.ip_entry, self.port_entry, self.username_entry]:
            entry.configure(
                fg_color=theme.get_color("bg_tertiary"),
                border_color=theme.get_color("border_primary")
            )

        # Update buttons
        self.connect_button.configure(
            fg_color=theme.get_color("button_primary"),
            hover_color=theme.get_color("button_primary_hover")
        )
        self.disconnect_button.configure(
            fg_color=theme.get_color("button_danger"),
            hover_color=theme.get_color("button_danger_hover")
        )

        # Update status
        status_frame = None
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame) and len(child.winfo_children()) > 0:
                first_child = child.winfo_children()[0]
                if isinstance(first_child, ctk.CTkLabel) and first_child.cget("text") == "Status":
                    status_frame = child
                    break

        if status_frame:
            status_frame.configure(fg_color=theme.get_color("bg_tertiary"))
            for child in status_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    if child.cget("text") == "Status":
                        child.configure(text_color=theme.get_color("text_primary"))
                    else:
                        # Status text
                        child.configure(text_color=theme.get_color("status_disconnected"))

    def update_connection_status(self, connected: bool) -> None:
        """Update the connection status display."""
        if connected:
            self.status_label.configure(text="Connected", text_color="#4CAF50")
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
            self.ip_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")
            self.username_entry.configure(state="disabled")
        else:
            self.status_label.configure(text="Disconnected", text_color="#ff6b6b")
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
            self.ip_entry.configure(state="normal")
            self.port_entry.configure(state="normal")
            self.username_entry.configure(state="normal")

        # Update status color based on theme
        if self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            color = theme.get_color("status_connected") if connected else theme.get_color("status_disconnected")
            self.status_label.configure(text_color=color)