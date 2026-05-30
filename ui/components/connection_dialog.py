"""
Connection dialog component for the P2P Messenger application.

Encapsulates server connection settings and status controls in a modal dialog.
"""

import customtkinter as ctk
import tkinter as tk
from core.events.events import Event, CONNECT_REQUEST, DISCONNECT_REQUEST
from ..theme.theme_manager import ThemeManager


class ConnectionSettingsDialog(ctk.CTkToplevel):
    """
    Modal connection settings dialog.

    Responsible for server IP, port, username, connect/disconnect controls,
    and connection status display.
    """

    def __init__(
        self,
        parent: ctk.CTk,
        dispatcher,
        ip_var: tk.StringVar,
        port_var: tk.StringVar,
        username_var: tk.StringVar,
        theme_manager: ThemeManager,
    ) -> None:
        super().__init__(parent)

        self.parent = parent
        self.dispatcher = dispatcher
        self.ip_var = ip_var
        self.port_var = port_var
        self.username_var = username_var
        self.theme_manager = theme_manager
        self.connected = False

        self.title("Connection Settings")
        self.geometry("540x510")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()

        if self.theme_manager:
            self.theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        self._update_colors()

        self.update_idletasks()
        try:
            self.wait_visibility()
        except Exception as e:
            pass

        try:
            self.grab_set()
        except Exception as exc:
            pass

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        """Construct the connection dialog layout."""
        # Main container that fills the entire dialog
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_rowconfigure(3, weight=0)
        main_frame.grid_rowconfigure(4, weight=0)
        main_frame.grid_rowconfigure(5, weight=0)
        main_frame.grid_rowconfigure(6, weight=0)
        main_frame.grid_rowconfigure(7, weight=1)  # Spacer row
        main_frame.grid_rowconfigure(8, weight=0)  # Button row

        # Header
        header_label = ctk.CTkLabel(main_frame, text="Connection Settings", font=("", 16, "bold"))
        header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        self.header_label = header_label

        # IP field
        self.ip_label = ctk.CTkLabel(main_frame, text="Server IP:", font=("", 11))
        self.ip_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.ip_entry = ctk.CTkEntry(main_frame, textvariable=self.ip_var, width=360)
        self.ip_entry.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        # Port field
        self.port_label = ctk.CTkLabel(main_frame, text="Port:", font=("", 11))
        self.port_label.grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.port_entry = ctk.CTkEntry(main_frame, textvariable=self.port_var, width=360)
        self.port_entry.grid(row=4, column=0, sticky="ew", pady=(0, 15))

        # Username field
        self.username_label = ctk.CTkLabel(main_frame, text="Username:", font=("", 11))
        self.username_label.grid(row=5, column=0, sticky="w", pady=(0, 5))
        self.username_entry = ctk.CTkEntry(main_frame, textvariable=self.username_var, width=360)
        self.username_entry.grid(row=6, column=0, sticky="ew", pady=(0, 15))

        # Status field
        self.status_title = ctk.CTkLabel(main_frame, text="Status:", font=("", 11))
        self.status_title.grid(row=7, column=0, sticky="w", pady=(0, 5))
        self.status_label = ctk.CTkLabel(main_frame, text="Disconnected", font=("", 11))
        self.status_label.grid(row=8, column=0, sticky="w", pady=(0, 20))

        # Button frame with grid layout
        button_frame_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame_container.grid(row=9, column=0, sticky="ew", pady=(10, 0))
        button_frame_container.grid_columnconfigure(0, weight=1)
        button_frame_container.grid_columnconfigure(1, weight=1)

        self.connect_button = ctk.CTkButton(
            button_frame_container,
            text="Connect",
            command=self._dispatch_connect_request,
        )
        self.connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.disconnect_button = ctk.CTkButton(
            button_frame_container,
            text="Disconnect",
            command=self._dispatch_disconnect_request,
        )
        self.disconnect_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.disconnect_button.configure(state="disabled")

    def _dispatch_connect_request(self) -> None:
        """Validate inputs and dispatch the existing connect request event."""
        host = self.ip_var.get().strip()
        port_text = self.port_var.get().strip()
        username = self.username_var.get().strip()

        if not host or not port_text:
            self._set_status_text("Enter server IP and port", "#ff6b6b")
            return

        try:
            port = int(port_text)
        except ValueError:
            self._set_status_text("Port must be a number", "#ff6b6b")
            return

        event = Event(
            CONNECT_REQUEST,
            {
                "host": host,
                "port": port,
                "username": username,
            }
        )
        self.dispatcher.notify(event)

    def _dispatch_disconnect_request(self) -> None:
        """Dispatch the existing disconnect request event."""
        event = Event(DISCONNECT_REQUEST, {})
        self.dispatcher.notify(event)

    def _set_status_text(self, text: str, color: str) -> None:
        """Update the status text and color for validation feedback."""
        self.status_label.configure(text=text, text_color=color)

    def update_connection_status(self, connected: bool) -> None:
        """Update dialog widgets when the connection state changes."""
        self.connected = connected
        if connected:
            self.status_label.configure(text="Connected")
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
            self.ip_entry.configure(state="disabled")
            self.port_entry.configure(state="disabled")
            self.username_entry.configure(state="disabled")
        else:
            self.status_label.configure(text="Disconnected")
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
            self.ip_entry.configure(state="normal")
            self.port_entry.configure(state="normal")
            self.username_entry.configure(state="normal")

        if self.theme_manager:
            theme = self.theme_manager.get_current_theme()
            color = theme.get_color("status_connected") if connected else theme.get_color("status_disconnected")
            self.status_label.configure(text_color=color)

    def _on_theme_changed(self, theme) -> None:
        """Refresh dialog colors when theme changes."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Apply current theme colors to the dialog."""
        theme = self.theme_manager.get_current_theme()
        self.configure(fg_color=theme.get_color("bg_secondary"))

        labels = [
            self.header_label,
            self.ip_label,
            self.port_label,
            self.username_label,
            self.status_title,
            self.status_label,
        ]
        for label in labels:
            label.configure(text_color=theme.get_color("text_primary"))

        for entry in [self.ip_entry, self.port_entry, self.username_entry]:
            entry.configure(
                fg_color=theme.get_color("input_bg"),
                text_color=theme.get_color("input_text"),
                border_color=theme.get_color("input_border"),
            )

        for button in [self.connect_button, self.disconnect_button]:
            button.configure(
                fg_color=theme.get_color("button_primary"),
                hover_color=theme.get_color("button_primary_hover"),
                text_color=theme.get_color("text_primary"),
            )

    def _on_close(self) -> None:
        """Close the dialog and clean up theme subscriptions."""
        if self.theme_manager:
            self.theme_manager.unsubscribe_from_theme_changes(self._on_theme_changed)
        self.grab_release()
        self.destroy()
