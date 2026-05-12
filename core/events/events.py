"""
Event definitions for the P2P Messenger application.

This module defines the events that are dispatched through the event system
and provides a unified Event dataclass for event data.
"""

from dataclasses import dataclass
from time import time as current_time
from typing import Any

# Event type constants
MESSAGE_RECEIVED = "message_received"
CONNECTION_CHANGED = "connection_changed"
USER_JOINED = "user_joined"
USER_LEFT = "user_left"
ERROR_OCCURRED = "error_occurred"
CLEAR_CHAT = "clear_chat"
SEND_MESSAGE = "send_message"
CONNECT_REQUEST = "connect_request"
DISCONNECT_REQUEST = "disconnect_request"
UI_UPDATE = "ui_update"
STATUS_CHANGED = "status_changed"


@dataclass
class Event:
    """
    Unified event structure for all dispatcher events.
    
    Attributes:
        type (str): The event type (one of the constants above).
        data (dict): Event-specific data payload.
        timestamp (float): Unix timestamp when the event was created.
    """
    type: str
    data: dict[str, Any]
    timestamp: float = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = current_time()
