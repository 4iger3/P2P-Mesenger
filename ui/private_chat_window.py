"""
Private chat window module for P2P Messenger.

Provides a dedicated private chat window component and a manager to
prevent duplicate windows while preserving event-driven decoupling.
"""

from __future__ import annotations

import customtkinter as ctk
from core.events.observer import Observer
from core.events.events import Event, PRIVATE_MESSAGE_SENT, PRIVATE_MESSAGE_RECEIVED, PRIVATE_CHAT_OPENED, CONNECTION_CHANGED
from ui.components.chat_area import ChatArea
from ui.components.message_input import MessageInput


class PrivateChatWindow(ctk.CTkToplevel, Observer):
    """A dedicated private conversation window for a single peer."""

    def __init__(
        self,
        parent: ctk.CTk,
        dispatcher,
        local_username: str,
        peer_username: str,
        theme_manager=None,
        on_close: callable | None = None,
    ) -> None:
        super().__init__(parent)
        self.dispatcher = dispatcher
        self.local_username = local_username
        self.peer_username = peer_username
        self.theme_manager = theme_manager
        self.on_close_callback = on_close

        self.title(f"Chat with {peer_username}")
        self.geometry("520x520")
        self.minsize(420, 380)

        self._build_ui()
        self.dispatcher.attach(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        open_event = Event(PRIVATE_CHAT_OPENED, {"username": peer_username})
        self.dispatcher.notify(open_event)

    def _build_ui(self) -> None:
        """Build the private chat window user interface."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self, text=f"Chat with {self.peer_username}", font=("", 16, "bold"))
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))

        self.chat_area = ChatArea(self, self.theme_manager)
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.chat_area.title_label.configure(text=f"Chat with {self.peer_username}")

        self.input_area = MessageInput(self, send_command=self._on_send, theme_manager=self.theme_manager)
        self.input_area.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))

        # Enable send button since we're only opened when already connected
        self.input_area.set_send_enabled(True)
        print(f"[DEBUG] PrivateChatWindow created for {self.peer_username}")
        print(f"[DEBUG] Send button enabled")

    def _on_send(self) -> None:
        """Dispatch private message send events for this chat window."""
        text = self.input_area.get_text().strip()
        if not text:
            return

        print(f"[DEBUG] Send button clicked in PrivateChatWindow")
        print(f"[DEBUG] Sending private message to {self.peer_username}: {text[:50]}...")

        event = Event(
            PRIVATE_MESSAGE_SENT,
            {
                "sender": self.local_username,
                "recipient": self.peer_username,
                "text": text,
            },
        )
        self.dispatcher.notify(event)
        self.input_area.clear()

    def update(self, event: Event) -> None:
        """Update the chat window for private message events and connection changes."""
        if event.type == CONNECTION_CHANGED:
            connected = event.data.get("connected", False)
            self.input_area.set_send_enabled(connected)
            print(f"[DEBUG] PrivateChatWindow: CONNECTION_CHANGED -> {'enabled' if connected else 'disabled'} send button")

        if event.type == PRIVATE_MESSAGE_RECEIVED:
            payload = event.data.get("payload", {})
            sender = str(payload.get("sender", "")).strip()
            recipient = str(payload.get("recipient", "")).strip()
            text = str(payload.get("text", ""))
            timestamp = str(payload.get("timestamp", ""))

            if sender == self.peer_username and recipient == self.local_username:
                print(f"[DEBUG] PrivateChatWindow received message from {sender}")
                self._append_message(sender, text, timestamp, is_own=False)

        if event.type == PRIVATE_MESSAGE_SENT:
            sender = str(event.data.get("sender", "")).strip()
            recipient = str(event.data.get("recipient", "")).strip()
            text = str(event.data.get("text", ""))
            if sender == self.local_username and recipient == self.peer_username:
                print(f"[DEBUG] PrivateChatWindow: Local message sent to {recipient}")
                self._append_message("Me", text, "", is_own=True)

    def _append_message(self, sender: str, text: str, timestamp: str, is_own: bool) -> None:
        """Append a message to the private chat history."""
        self.chat_area.add_message(text, is_own, timestamp, sender if not is_own else "")

    def focus_window(self) -> None:
        """Bring the private chat window to the front."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_close(self) -> None:
        """Handle window close and detach from dispatcher."""
        self.dispatcher.detach(self)
        if self.on_close_callback:
            self.on_close_callback(self.peer_username)
        self.destroy()


class PrivateChatWindowManager:
    """Manages private chat windows and prevents duplicates."""

    def __init__(
        self,
        parent,
        dispatcher,
        local_username_getter: callable,
        theme_manager=None,
        window_class=PrivateChatWindow,
    ) -> None:
        self.parent = parent
        self.dispatcher = dispatcher
        self.get_local_username = local_username_getter
        self.theme_manager = theme_manager
        self.window_class = window_class
        self.windows: dict[str, PrivateChatWindow] = {}

    def open_chat(self, username: str):
        """Open or focus an existing private chat window for a user."""
        username = str(username or "").strip()
        if not username or username == self.get_local_username():
            return None

        if username in self.windows:
            window = self.windows[username]
            if window.winfo_exists():
                window.focus_window()
                return window
            self.windows.pop(username, None)

        window = self.window_class(
            self.parent,
            self.dispatcher,
            self.get_local_username(),
            username,
            self.theme_manager,
            on_close=self._handle_window_close,
        )
        self.windows[username] = window
        return window

    def _handle_window_close(self, username: str) -> None:
        """Remove closed window from the manager."""
        if username in self.windows:
            self.windows.pop(username, None)
