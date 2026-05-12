"""
Application state management with Observer pattern integration.

AppState maintains the core application state and responds to events
through the Observer pattern, reducing coupling with UI and network layers.
"""

from core.events.observer import Observer
from core.events.events import Event, CONNECTION_CHANGED, ERROR_OCCURRED, CLEAR_CHAT


class AppState(Observer):
    """
    Maintains centralized application state and responds to events.
    
    Implements the Observer pattern to automatically sync state based on
    events from the network, UI, and other components.
    """

    def __init__(self) -> None:
        """Initialize application state with default values."""
        self.connected: bool = False
        self.status_text: str = "Disconnected"
        self.message_count: int = 0
        self.username: str = ""

    def increment_message_count(self) -> None:
        """Increment the message count."""
        self.message_count += 1

    def set_connected(self, connected: bool) -> None:
        """Set the connection state."""
        self.connected = connected

    def set_status(self, status_text: str) -> None:
        """Set the status text."""
        self.status_text = status_text

    def set_username(self, username: str) -> None:
        """Set the username."""
        self.username = username.strip()

    def update(self, event: Event) -> None:
        """
        Handle events and update application state accordingly.
        
        Args:
            event (Event): The event to process.
        """
        if event.type == CONNECTION_CHANGED:
            connected = event.data.get("connected", False)
            self.set_connected(connected)
            if connected:
                self.set_status("Connected")
            else:
                self.set_status("Disconnected")
                self.set_username("")
        elif event.type == CLEAR_CHAT:
            self.message_count = 0
        elif event.type == ERROR_OCCURRED:
            # Optionally handle error state
            pass
