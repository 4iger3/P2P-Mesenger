import json
import queue
from datetime import datetime
from typing import Any

from .message_model import MessageModel
from .state import AppState


class Controller:
    def __init__(
        self,
        ui_event_queue: queue.Queue,
        core_to_network_queue: queue.Queue,
        network_event_queue: queue.Queue,
        ui_update_queue: queue.Queue,
        state: AppState,
    ) -> None:
        self.ui_event_queue = ui_event_queue
        self.core_to_network_queue = core_to_network_queue
        self.network_event_queue = network_event_queue
        self.ui_update_queue = ui_update_queue
        self.state = state
        self.username = ""

    def process_queues(self) -> None:
        self._process_ui_events()
        self._process_network_events()

    def _process_ui_events(self) -> None:
        while True:
            try:
                event = self.ui_event_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_ui_event(event)

    def _process_network_events(self) -> None:
        while True:
            try:
                event = self.network_event_queue.get_nowait()
            except queue.Empty:
                break
            self._handle_network_event(event)

    def _handle_ui_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")

        if event_type == "connect":
            self._handle_connect(event)
        elif event_type == "send_message":
            self._handle_send_message(event)
        elif event_type == "disconnect":
            self._handle_disconnect()
        elif event_type == "clear_chat":
            self._handle_clear_chat()

    def _handle_connect(self, event: dict[str, Any]) -> None:
        host = str(event.get("host", "")).strip()
        port_text = str(event.get("port", "")).strip()

        if not host or not port_text:
            self._send_ui_update({"type": "status", "text": "Enter server IP and port"})
            return

        try:
            port = int(port_text)
        except ValueError:
            self._send_ui_update({"type": "status", "text": "Port must be a number"})
            return

        if self.state.connected:
            self._send_ui_update({"type": "status", "text": "Already connected"})
            return

        username = str(event.get("username", "")).strip()
        self.username = username
        self.state.set_username(username)
        self._send_ui_update({"type": "status", "text": "Connecting..."})
        self._send_ui_update({"type": "enable_connect", "enabled": False})
        self.core_to_network_queue.put(
            {"type": "connect", "host": host, "port": port, "username": username}
        )

    def _handle_send_message(self, event: dict[str, Any]) -> None:
        text = str(event.get("text", "")).strip()
        if not text:
            return

        username = str(event.get("username", "")).strip()
        message = f"{username}: {text}" if username else text

        if not self.state.connected:
            self._send_ui_update({"type": "status", "text": "Not connected"})
            return

        self.core_to_network_queue.put({"type": "send_message", "message": message})
        self._send_ui_update({"type": "clear_input"})

    def _handle_disconnect(self) -> None:
        if self.state.connected:
            self.core_to_network_queue.put({"type": "disconnect"})

    def _handle_clear_chat(self) -> None:
        self.state.message_count = 0
        self._send_ui_update({"type": "message_count", "count": 0})

    def _handle_network_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")

        if event_type == "connected":
            self.state.set_connected(True)
            self.state.set_status("Connected")
            self._send_ui_update({"type": "status", "text": "Connected"})
            self._send_ui_update({"type": "enable_send", "enabled": True})
            self._send_ui_update({"type": "enable_connect", "enabled": False})
        elif event_type == "disconnected":
            self.state.set_connected(False)
            self.state.set_status("Disconnected")
            self.state.set_username("")
            self._send_ui_update({"type": "status", "text": "Disconnected"})
            self._send_ui_update({"type": "enable_send", "enabled": False})
            self._send_ui_update({"type": "enable_connect", "enabled": True})
        elif event_type == "message":
            message_text = str(event.get("message", ""))
            if not message_text:
                return

            try:
                payload = json.loads(message_text)
            except json.JSONDecodeError:
                payload = None

            if isinstance(payload, dict):
                event_type_name = payload.get("type")
                user = str(payload.get("user", "")).strip()
                now = datetime.now().strftime("%H:%M:%S")

                if event_type_name == "join":
                    if user and user == self.state.username:
                        text = "You joined the chat"
                    else:
                        text = f"User {user} joined the chat"
                    self._send_ui_update({"type": "append_system", "message": text, "timestamp": now})
                elif event_type_name == "leave":
                    if user and user == self.state.username:
                        text = "You left the chat"
                    else:
                        text = f"User {user} left the chat"
                    self._send_ui_update({"type": "append_system", "message": text, "timestamp": now})
                else:
                    message = MessageModel(message_text)
                    formatted = message.formatted()
                    self.state.increment_message_count()
                    self._send_ui_update({"type": "append_message", "message": formatted})
                    self._send_ui_update({"type": "message_count", "count": self.state.message_count})
            else:
                message = MessageModel(message_text)
                formatted = message.formatted()
                self.state.increment_message_count()
                self._send_ui_update({"type": "append_message", "message": formatted})
                self._send_ui_update({"type": "message_count", "count": self.state.message_count})
        elif event_type == "error":
            error_text = str(event.get("error", "Connection error"))
            self._send_ui_update({"type": "status", "text": f"Connection error: {error_text}"})
            self._send_ui_update({"type": "enable_connect", "enabled": True})

    def _send_ui_update(self, update: dict[str, Any]) -> None:
        self.ui_update_queue.put(update)
