"""
Main window UI for the P2P Messenger application.

Implements the Observer pattern to respond to network and core events,
providing real-time updates to the user interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox

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
from .components import ChatDisplay, ConnectionPanel, MessageInput, StatusBar


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
        self.root = tk.Tk()
        self.root.title("P2P Messenger Client")
        self.root.geometry("1100x700")
        self.root.minsize(900, 500)

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.server_port_var = tk.StringVar(value="8765")
        self.username_var = tk.StringVar(value="")

        self._setup_styles()
        self._build_ui()
        self._bind_events()
        self._setup_context_menu()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Attach to dispatcher to receive events
        dispatcher.attach(self)

    def _setup_styles(self) -> None:
        """Setup Tkinter styles for UI components."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Header.TLabel", background="#0f172a", foreground="#e6edf3", font=("TkDefaultFont", 12, "bold"))
        style.configure("Status.TLabel", background="#0f172a", foreground="#e6edf3", font=("TkDefaultFont", 9))
        style.configure("Connected.TLabel", foreground="green", font=("TkDefaultFont", 9, "bold"))
        style.configure("Disconnected.TLabel", foreground="red", font=("TkDefaultFont", 9, "bold"))
        style.configure("Connecting.TLabel", foreground="orange", font=("TkDefaultFont", 9, "bold"))
        style.configure("Counter.TLabel", font=("TkDefaultFont", 8), foreground="#8b98a5", background="#0f172a")
        style.configure("Panel.TLabelframe", background="#1e293b", borderwidth=0, relief="flat")
        style.configure("Panel.TLabelframe.Label", background="#1e293b", foreground="#e6edf3")
        style.configure("Panel.TFrame", background="#0f172a")
        style.configure("ChatEntry.TEntry", fieldbackground="#1e293b", background="#1e293b", foreground="#e6edf3")
        style.configure("Accent.TButton", background="#2563eb", foreground="#e6edf3")

    def _build_ui(self) -> None:
        """Build the UI layout."""
        main_container = ttk.Frame(self.root, style="Main.TFrame")
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(main_container, style="Panel.TFrame", padding=10)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="P2P Messenger", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.connection_status_label = ttk.Label(header_frame, text="Disconnected", style="Status.TLabel")
        self.connection_status_label.grid(row=0, column=1, sticky="e")

        self.connection_panel = ConnectionPanel(
            main_container,
            ip_var=self.server_ip_var,
            port_var=self.server_port_var,
            username_var=self.username_var,
            connect_command=self._on_connect,
        )
        self.connection_panel.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        content_frame = ttk.Frame(main_container, style="Panel.TFrame")
        content_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ChatDisplay(content_frame)
        self.chat_display.grid(row=0, column=0, sticky="nsew")

        self.message_input = MessageInput(main_container, send_command=self._on_send)
        self.message_input.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        self.status_bar = StatusBar(main_container)
        self.status_bar.grid(row=4, column=0, sticky="ew")

    def _bind_events(self) -> None:
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-l>", lambda event: self._clear_chat())
        self.message_input.entry.bind("<Control-a>", self._select_all)
        self.message_input.entry.bind("<KeyRelease>", lambda event: self.message_input.update_char_count())
        self.message_input.entry.bind("<Return>", lambda event: self._on_send() if self.message_input.send_button["state"] == "normal" else None)

    def _setup_context_menu(self) -> None:
        """Setup right-click context menu."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy All", command=self._copy_chat)
        self.context_menu.add_command(label="Clear", command=self._clear_chat)
        self.chat_display.canvas.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event: tk.Event) -> None:
        """Show context menu at mouse position."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _select_all(self, event: tk.Event) -> str:
        """Select all text in message input."""
        self.message_input.entry.selection_range(0, tk.END)
        return "break"

    def _on_connect(self) -> None:
        """Handle connect button click."""
        event = Event(
            CONNECT_REQUEST,
            {
                "host": self.server_ip_var.get(),
                "port": self.server_port_var.get(),
                "username": self.username_var.get(),
            }
        )
        self.dispatcher.notify(event)

    def _on_send(self) -> None:
        """Handle send button click."""
        event = Event(
            SEND_MESSAGE,
            {
                "text": self.message_input.text_var.get(),
                "username": self.username_var.get(),
            }
        )
        self.dispatcher.notify(event)
        self.message_input.clear()

    def _clear_chat(self) -> None:
        """Clear chat history."""
        if messagebox.askyesno("Clear Chat", "Clear all messages?"):
            self.chat_display.clear()
            self.status_bar.set_message_count(0)
            event = Event(CLEAR_CHAT, {})
            self.dispatcher.notify(event)

    def _copy_chat(self) -> None:
        """Copy chat content to clipboard."""
        content = self.chat_display.copy_all()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._set_status("Chat copied to clipboard")
        self.root.after(2000, lambda: self._set_status(self.status_bar.status_label.cget("text")))

    def _on_close(self) -> None:
        """Handle window close."""
        event = Event(DISCONNECT_REQUEST, {})
        self.dispatcher.notify(event)
        self.root.destroy()

    def _set_status(self, text: str) -> None:
        """Set status bar text."""
        self.status_bar.set_status(text)

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
                self.chat_display.append_system(text, now)
            elif event_type == "leave":
                current_user = self.username_var.get().strip()
                if user and user == current_user:
                    text = "You left the chat"
                else:
                    text = f"User {user} left the chat"
                self.chat_display.append_system(text, now)
            else:
                message = MessageModel(message_text)
                formatted = message.formatted()
                text, timestamp, is_own = self._parse_message(formatted)
                self.chat_display.add_message(text, is_own, timestamp)
                self.status_bar.increment_message_count()
        else:
            message = MessageModel(message_text)
            formatted = message.formatted()
            text, timestamp, is_own = self._parse_message(formatted)
            self.chat_display.add_message(text, is_own, timestamp)
            self.status_bar.increment_message_count()

    def _handle_connection_changed(self, event: Event) -> None:
        """Handle connection state change event."""
        connected = event.data.get("connected", False)
        
        if connected:
            self._set_status("Connected")
            self.connection_status_label.config(text="Connected")
            self.message_input.send_button.config(state="normal")
            self.connection_panel.connect_button.config(state="disabled")
        else:
            self._set_status("Disconnected")
            self.connection_status_label.config(text="Disconnected")
            self.message_input.send_button.config(state="disabled")
            self.connection_panel.connect_button.config(state="normal")

    def _handle_error(self, event: Event) -> None:
        """Handle error event."""
        error_text = str(event.data.get("error", "Connection error"))
        self._set_status(f"Connection error: {error_text}")
        self.connection_panel.connect_button.config(state="normal")

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

