from dataclasses import dataclass


@dataclass
class AppState:
    connected: bool = False
    status_text: str = "Disconnected"
    message_count: int = 0
    username: str = ""

    def increment_message_count(self) -> None:
        self.message_count += 1

    def set_connected(self, connected: bool) -> None:
        self.connected = connected

    def set_status(self, status_text: str) -> None:
        self.status_text = status_text

    def set_username(self, username: str) -> None:
        self.username = username.strip()
