#!/usr/bin/env python3
"""
Test script to verify the client can send messages
"""
import asyncio
import websockets

async def test_client_send():
    """Connect and listen for messages to verify client sending works"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Test listener: Connected to server")
            
            # Wait for messages from the main client
            print("Waiting for messages from main client...")
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    print(f"Received message {i+1}: {message}")
                except asyncio.TimeoutError:
                    print(f"Timeout waiting for message {i+1}")
                    break

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting client send test...")
    print("Make sure to type messages in the main client GUI")
    asyncio.run(test_client_send())
    print("Test completed")