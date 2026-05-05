#!/usr/bin/env python3
"""Centralized WebSocket relay server for forwarding messages between clients."""

import argparse
import asyncio
import sys

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

active_connections = set()
connection_lock = asyncio.Lock()


async def broadcast_message(message: str) -> None:
    """Send a text message to all active clients."""
    disconnected = []

    for websocket in list(active_connections):
        try:
            await websocket.send(message)
        except (ConnectionClosedError, ConnectionClosedOK, OSError):
            disconnected.append(websocket)
        except Exception as error:
            print(f"Broadcast error: {error}", file=sys.stderr)
            disconnected.append(websocket)

    if disconnected:
        async with connection_lock:
            for websocket in disconnected:
                active_connections.discard(websocket)


async def handle_client(websocket: websockets.WebSocketServerProtocol) -> None:
    """Handle a client connection and relay its messages."""
    async with connection_lock:
        active_connections.add(websocket)
    print("Client connected")

    try:
        async for message in websocket:
            print("Message received")
            await broadcast_message(message)
    except (ConnectionClosedError, ConnectionClosedOK):
        pass
    except Exception as error:
        print(f"Connection handler error: {error}", file=sys.stderr)
    finally:
        async with connection_lock:
            active_connections.discard(websocket)
        print("Client disconnected")


async def main() -> None:
    """Start the WebSocket server with command-line arguments."""
    parser = argparse.ArgumentParser(description="P2P Messenger relay server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind the server")
    args = parser.parse_args()

    async with websockets.serve(handle_client, args.host, args.port):
        print(f"Server started on {args.host}:{args.port}")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
