#!/usr/bin/env python3
"""Centralized WebSocket relay server for forwarding messages between clients."""

import argparse
import asyncio
import json
import sys

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

active_connections = set()
client_usernames: dict[websockets.WebSocketServerProtocol, str] = {}
connection_lock = asyncio.Lock()


async def broadcast_user_list() -> None:
    """Broadcast the current user list to all connected clients."""
    usernames = list(client_usernames.values())
    user_list_message = json.dumps({"type": "user_list", "users": usernames})
    await broadcast_message(user_list_message)


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
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                payload = None

            if isinstance(payload, dict) and payload.get("type") == "auth":
                username = str(payload.get("user", "")).strip()
                client_usernames[websocket] = username
                join_message = json.dumps({"type": "join", "user": username})
                await broadcast_message(join_message)
                await broadcast_user_list()  # Broadcast updated user list
                continue

            await broadcast_message(message)
    except (ConnectionClosedError, ConnectionClosedOK):
        pass
    except Exception as error:
        print(f"Connection handler error: {error}", file=sys.stderr)
    finally:
        username = client_usernames.pop(websocket, "")
        async with connection_lock:
            active_connections.discard(websocket)
        if username:
            leave_message = json.dumps({"type": "leave", "user": username})
            await broadcast_message(leave_message)
            await broadcast_user_list()  # Broadcast updated user list
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
