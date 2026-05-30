"""
Main window UI for the P2P Messenger application.

Implements the Observer pattern to respond to network and core events,
providing real-time updates to the user interface.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from core.events.observer import Observer
from core.events.events import (
    Event,
    CONNECTION_CHANGED,
    MESSAGE_RECEIVED,
    ERROR_OCCURRED,
    CONNECT_REQUEST,
    DISCONNECT_REQUEST,
    SEND_MESSAGE,
    CLEAR_CHAT,
)
from core.events.dispatcher import EventDispatcher
from .components import Sidebar, ChatArea, MessageInput, StatusPanel, UsersPanel
from .components.connection_dialog import ConnectionSettingsDialog
from .components.settings_window import SettingsWindow
from .theme.theme_manager import ThemeManager


class MainWindow(Observer):
    """
    Main UI window for the P2P Messenger application.
    
    Observes events from the network and core layers, updating the UI
    in response to connection changes, incoming messages, and errors.
    """

    def __init__(self, dispatcher: EventDispatcher) -> None:
        """
        Initialize the main window.
        
        Args:
            dispatcher (EventDispatcher): The event dispatcher for sending/receiving events.
        """
        self.dispatcher = dispatcher
        self.root = ctk.CTk()
        self.root.title("P2P Messenger Client")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Set CustomTkinter theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.server_port_var = tk.StringVar(value="8765")
        self.username_var = tk.StringVar(value="")

        # Initialize theme manager
        self.theme_manager = ThemeManager(dispatcher)
        self.settings_window = None
        self.connection_dialog = None
        self.connected = False

        self._build_ui()
        self._bind_events()
        self._setup_context_menu()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Attach to dispatcher to receive events
        dispatcher.attach(self)

    def _build_ui(self) -> None:
        """Build the UI layout with sidebar, chat area, and message input."""
        # Configure root window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Main content frame (sidebar + chat area + users panel)
        main_frame = ctk.CTkFrame(self.root, fg_color="#0f172a")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=0)  # Sidebar
        main_frame.grid_columnconfigure(1, weight=1)  # Chat area
        main_frame.grid_columnconfigure(2, weight=0)  # Users panel

        # Sidebar
        self.sidebar = Sidebar(
            main_frame,
            connection_settings_command=self._open_connection_dialog,
            settings_command=self._open_settings_window,
            theme_manager=self.theme_manager
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)

        # Chat area
        self.chat_area = ChatArea(main_frame, self.theme_manager)
        self.chat_area.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=0)

        # Users panel
        self.users_panel = UsersPanel(main_frame, self.dispatcher, self.theme_manager)
        self.users_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=0)

        # Message input (bottom, spans full width)
        self.message_input = MessageInput(self.root, send_command=self._on_send, theme_manager=self.theme_manager)
        self.message_input.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-l>", lambda event: self._clear_chat())
        # Note: MessageInput handles its own key bindings internally

    def _open_settings_window(self) -> None:
        """Open the settings popup window or bring it to the front."""
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return

        self.settings_window = SettingsWindow(self.root, self.theme_manager)
        self.settings_window.bind("<Destroy>", self._on_settings_window_destroy)

    def _open_connection_dialog(self) -> None:
        """Open the connection dialog or bring it to the front."""
        if self.connection_dialog and self.connection_dialog.winfo_exists():
            self.connection_dialog.lift()
            self.connection_dialog.focus_force()
            return

        self.connection_dialog = ConnectionSettingsDialog(
            self.root,
            dispatcher=self.dispatcher,
            ip_var=self.server_ip_var,
            port_var=self.server_port_var,
            username_var=self.username_var,
            theme_manager=self.theme_manager,
        )
        self.connection_dialog.update_connection_status(self.connected)
        self.connection_dialog.bind("<Destroy>", self._on_connection_dialog_destroy)

    def _on_connection_dialog_destroy(self, event: tk.Event) -> None:
        """Clear the stored connection dialog reference when it closes."""
        if event.widget is self.connection_dialog:
            self.connection_dialog = None

    def _on_settings_window_destroy(self, event: tk.Event) -> None:
        """Clear the stored settings window reference when it closes."""
        if event.widget is self.settings_window:
            self.settings_window = None

    def _setup_context_menu(self) -> None:
        """Setup right-click context menu."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy All", command=self._copy_chat)
        self.context_menu.add_command(label="Clear", command=self._clear_chat)
        self.chat_area.canvas.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event: tk.Event) -> None:
        """Show context menu at mouse position."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _on_send(self) -> None:
        """Handle send button click."""
        text = self.message_input.get_text().strip()
        if text:
            event = Event(
                SEND_MESSAGE,
                {
                    "text": text,
                    "username": self.username_var.get(),
                }
            )
            self.dispatcher.notify(event)
            self.message_input.clear()

    def _clear_chat(self) -> None:
        """Clear chat history."""
        if messagebox.askyesno("Clear Chat", "Clear all messages?"):
            self.chat_area.clear()
            # Note: No message count tracking in new design

    def _copy_chat(self) -> None:
        """Copy chat content to clipboard."""
        content = self.chat_area.copy_all()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        # Note: Status message not shown in new design

    def _on_close(self) -> None:
        """Handle window close."""
        event = Event(DISCONNECT_REQUEST, {})
        self.dispatcher.notify(event)
        self.root.destroy()

    def update(self, event: Event) -> None:
        """
        Handle events from the dispatcher.
        
        Updates the UI in response to network and core events.
        
        Args:
            event (Event): The event to process.
        """
        if event.type == MESSAGE_RECEIVED:
            self._handle_message_received(event)
        elif event.type == CONNECTION_CHANGED:
            self._handle_connection_changed(event)
        elif event.type == ERROR_OCCURRED:
            self._handle_error(event)

    def _handle_message_received(self, event: Event) -> None:
        """Handle incoming message event."""
        import json
        from core.message_model import MessageModel
        from datetime import datetime

        message_text = str(event.data.get("message", ""))
        if not message_text:
            return

        try:
            payload = json.loads(message_text)
        except json.JSONDecodeError:
            payload = None

        if isinstance(payload, dict):
            event_type = payload.get("type")
            user = str(payload.get("user", "")).strip()
            now = datetime.now().strftime("%H:%M:%S")

            if event_type == "join":
                current_user = self.username_var.get().strip()
                if user and user == current_user:
                    text = "You joined the chat"
                else:
                    text = f"User {user} joined the chat"
                self.chat_area.add_system_message(text, now)
            elif event_type == "leave":
                current_user = self.username_var.get().strip()
                if user and user == current_user:
                    text = "You left the chat"
                else:
                    text = f"User {user} left the chat"
                self.chat_area.add_system_message(text, now)
            else:
                message = MessageModel(message_text)
                formatted = message.formatted()
                text, timestamp, is_own = self._parse_message(formatted)
                username = user if not is_own else ""
                self.chat_area.add_message(text, is_own, timestamp, username)
        else:
            message = MessageModel(message_text)
            formatted = message.formatted()
            text, timestamp, is_own = self._parse_message(formatted)
            self.chat_area.add_message(text, is_own, timestamp)

    def _handle_connection_changed(self, event: Event) -> None:
        """Handle connection state change event."""
        connected = event.data.get("connected", False)
        
        self.connected = connected
        if connected:
            if self.connection_dialog and self.connection_dialog.winfo_exists():
                self.connection_dialog.update_connection_status(True)
            self.message_input.set_send_enabled(True)
        else:
            if self.connection_dialog and self.connection_dialog.winfo_exists():
                self.connection_dialog.update_connection_status(False)
            self.message_input.set_send_enabled(False)

    def _handle_error(self, event: Event) -> None:
        """Handle error event."""
        error_text = str(event.data.get("error", "Connection error"))
        self.connected = False
        if self.connection_dialog and self.connection_dialog.winfo_exists():
            self.connection_dialog.update_connection_status(False)
        self.message_input.set_send_enabled(False)
        # Could show error in a popup or status area

    def _parse_message(self, message: str) -> tuple[str, str, bool]:
        """Parse a formatted message into text, timestamp, and ownership flag."""
        timestamp = ""
        text = message
        if message.startswith("[") and "] " in message:
            closing_index = message.find("]")
            timestamp = message[1:closing_index]
            text = message[closing_index + 2 :]

        current_user = self.username_var.get().strip()
        is_own = False
        if current_user and text.startswith(f"{current_user}:"):
            is_own = True
            text = text[len(current_user) + 2 :].strip()

        return text, timestamp, is_own

    def run(self) -> None:
        """Start the GUI event loop."""
        self.root.mainloop()

