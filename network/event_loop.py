"""
Factory for creating and configuring the WebSocket network client.
"""

from core.events.dispatcher import EventDispatcher
from .websocket_client import WebSocketClient


def create_network_client(dispatcher: EventDispatcher) -> WebSocketClient:
    """
    Create and start a WebSocket client with the dispatcher.
    
    Args:
        dispatcher (EventDispatcher): The event dispatcher for network communication.
    
    Returns:
        WebSocketClient: The initialized and started WebSocket client.
    """
    client = WebSocketClient(dispatcher)
    client.start()
    return client

