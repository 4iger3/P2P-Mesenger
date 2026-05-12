"""
WebSocket client for network communication.

Handles WebSocket connections and integration with the event dispatcher
for asynchronous, thread-safe network operations.
"""

import asyncio
import json
import queue
import threading
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from core.events.observer import Observer
from core.events.dispatcher import EventDispatcher
from core.events.events import (
    Event,
    CONNECTION_CHANGED,
    MESSAGE_RECEIVED,
    ERROR_OCCURRED,
    CONNECT_REQUEST,
    DISCONNECT_REQUEST,
    SEND_MESSAGE,
)


class WebSocketClient(Observer):
    """
    Manages WebSocket connections and dispatches network events.
    
    Runs asyncio event loop in a separate thread and communicates with
    the main application through the EventDispatcher.
    """

    def __init__(self, dispatcher: EventDispatcher) -> None:
        """
        Initialize WebSocket client with event dispatcher.
        
        Args:
            dispatcher (EventDispatcher): Event dispatcher for sending/receiving events.
        """
        self.dispatcher = dispatcher
        self.loop = asyncio.new_event_loop()
        self.websocket: Optional[object] = None
        self.username: str = ""
        self.receive_task: Optional[object] = None
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        
        # Attach to dispatcher to receive network requests
        dispatcher.attach(self)

    def start(self) -> None:
        """Start the network thread."""
        self.thread.start()

    def send_message(self, message: str) -> None:
        """
        Send a message directly (called by Controller).
        
        Args:
            message (str): The formatted message to send.
        """
        if message:
            asyncio.run_coroutine_threadsafe(self._send_text(message), self.loop)

    def disconnect(self) -> None:
        """
        Disconnect directly (called by Controller).
        """
        asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)

    def _run_loop(self) -> None:
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._event_loop())
        self.loop.run_forever()

    async def _event_loop(self) -> None:
        """
        Main event loop that continuously checks for events from dispatcher.
        
        Since the dispatcher doesn't have async support, we poll for events
        at regular intervals.
        """
        while True:
            await asyncio.sleep(0.1)

    def update(self, event: Event) -> None:
        """
        Handle incoming events from the dispatcher.
        
        Routes network requests (connect, disconnect, send) to appropriate handlers.
        
        Args:
            event (Event): The event from the dispatcher.
        """
        if event.type == CONNECT_REQUEST:
            host = event.data.get("host")
            port = event.data.get("port")
            username = event.data.get("username")
            asyncio.run_coroutine_threadsafe(
                self._connect(host, port, username),
                self.loop
            )
        elif event.type == DISCONNECT_REQUEST:
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
        elif event.type == SEND_MESSAGE:
            message = event.data.get("message")
            # Only process events that have the formatted message (from Controller)
            if message is not None:
                asyncio.run_coroutine_threadsafe(self._send_text(message), self.loop)

    async def _connect(self, host: Optional[str], port: Optional[int], username: Optional[str] = None) -> None:
        """
        Establish WebSocket connection and begin receiving messages.
        
        Args:
            host (str): Server hostname or IP.
            port (int): Server port.
            username (str): Username to authenticate with.
        """
        if not host or port is None:
            event = Event(ERROR_OCCURRED, {"error": "Invalid connection parameters"})
            self.dispatcher.notify(event)
            return

        self.username = str(username or "").strip()
        uri = f"ws://{host}:{port}"

        try:
            self.websocket = await websockets.connect(uri)
            
            # Notify connection successful
            event = Event(CONNECTION_CHANGED, {"connected": True})
            self.dispatcher.notify(event)
            
            # Send auth message if username provided
            if self.username:
                auth_message = json.dumps({"type": "auth", "user": self.username})
                await self.websocket.send(auth_message)
            
            # Start receiving messages
            self.receive_task = self.loop.create_task(self._receive_messages())
        except Exception as error:
            event = Event(ERROR_OCCURRED, {"error": str(error)})
            self.dispatcher.notify(event)

    async def _receive_messages(self) -> None:
        """
        Receive messages from WebSocket and dispatch them as events.
        
        Runs indefinitely until connection is closed.
        """
        try:
            async for message in self.websocket:
                # Dispatch message received event
                event = Event(MESSAGE_RECEIVED, {"message": message})
                self.dispatcher.notify(event)
        except (ConnectionClosedError, ConnectionClosedOK):
            pass
        except Exception as error:
            event = Event(ERROR_OCCURRED, {"error": str(error)})
            self.dispatcher.notify(event)
        finally:
            self.websocket = None
            # Notify disconnection
            event = Event(CONNECTION_CHANGED, {"connected": False})
            self.dispatcher.notify(event)

    async def _disconnect(self) -> None:
        """Close WebSocket connection gracefully."""
        if self.websocket is not None:
            await self.websocket.close()
            if self.receive_task is not None:
                await self.receive_task
                self.receive_task = None

    async def _send_text(self, message: Optional[str]) -> None:
        """
        Send a text message via WebSocket.
        
        Args:
            message (str): The message to send.
        """
        if not message or self.websocket is None:
            return

        await self.websocket.send(message)

