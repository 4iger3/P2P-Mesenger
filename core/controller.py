"""
Application controller for routing events between UI and network.

The controller acts as an intermediary that processes UI requests,
validates them, updates the application state, and coordinates with
the network layer through event dispatching.
"""

import asyncio
from core.events.observer import Observer
from core.events.dispatcher import EventDispatcher
from core.events.events import (
    Event,
    CONNECTION_CHANGED,
    CONNECT_REQUEST,
    DISCONNECT_REQUEST,
    SEND_MESSAGE,
    ERROR_OCCURRED,
)
from .state import AppState


class Controller(Observer):
    """
    Application controller with Observer pattern integration.
    
    Validates user actions, manages application state, and coordinates
    between the UI layer (user actions) and network layer (WebSocket).
    """

    def __init__(self, dispatcher: EventDispatcher, state: AppState, network_client) -> None:
        """
        Initialize the controller.
        
        Args:
            dispatcher (EventDispatcher): Event dispatcher for sending/receiving events.
            state (AppState): Application state object.
            network_client: The network client for direct communication.
        """
        self.dispatcher = dispatcher
        self.state = state
        self.network_client = network_client
        
        # Attach to dispatcher to receive user events
        dispatcher.attach(self)

    def update(self, event: Event) -> None:
        """
        Handle events from the dispatcher.
        
        Routes user actions (connect, send) to appropriate handlers with validation.
        
        Args:
            event (Event): The event to process.
        """
        if event.type == CONNECT_REQUEST:
            self._handle_connect_request(event)
        elif event.type == SEND_MESSAGE:
            self._handle_send_message_request(event)
        elif event.type == DISCONNECT_REQUEST:
            self._handle_disconnect_request(event)
        elif event.type == CONNECTION_CHANGED:
            # Update state when connection changes
            connected = event.data.get("connected", False)
            self.state.set_connected(connected)
            if not connected:
                self.state.set_username("")

    def _handle_connect_request(self, event: Event) -> None:
        """
        Handle connection request with validation.
        
        Validates connection parameters. Does NOT re-emit the event to prevent
        infinite loops. The WebSocketClient is also attached to the dispatcher
        and will handle the connection directly from the original event.
        Errors are emitted as separate ERROR_OCCURRED events.
        
        Args:
            event (Event): The connect request event.
        """
        host = str(event.data.get("host", "")).strip()
        port_text = str(event.data.get("port", "")).strip()
        username = str(event.data.get("username", "")).strip()

        if not host or not port_text:
            error_event = Event(ERROR_OCCURRED, {"error": "Enter server IP and port"})
            self.dispatcher.notify(error_event)
            return

        try:
            port = int(port_text)
        except ValueError:
            error_event = Event(ERROR_OCCURRED, {"error": "Port must be a number"})
            self.dispatcher.notify(error_event)
            return

        if self.state.connected:
            error_event = Event(ERROR_OCCURRED, {"error": "Already connected"})
            self.dispatcher.notify(error_event)
            return

        # Save username for later use
        self.state.set_username(username)

    def _handle_send_message_request(self, event: Event) -> None:
        """
        Handle send message request with validation.
        
        Validates the message and connection state, then forwards to network layer.
        Formats the message properly for the WebSocketClient.
        
        Args:
            event (Event): The send message request event.
        """
        text = str(event.data.get("text", "")).strip()
        if not text:
            return

        if not self.state.connected:
            error_event = Event(ERROR_OCCURRED, {"error": "Not connected to server"})
            self.dispatcher.notify(error_event)
            return

        username = str(event.data.get("username", "")).strip()
        message = f"{username}: {text}" if username else text

        # Send directly to network client (avoid re-entrant event dispatching)
        self.network_client.send_message(message)

    def _handle_disconnect_request(self, event: Event) -> None:
        """
        Handle disconnection request.
        
        Calls network client directly to disconnect.
        
        Args:
            event (Event): The disconnect request event.
        """
        # Call network client directly (avoid re-entrant event dispatching)
        self.network_client.disconnect()

