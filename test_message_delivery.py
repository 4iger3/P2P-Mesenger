#!/usr/bin/env python3
"""
Test script to verify message delivery between two clients
"""
import asyncio
import websockets
import threading
import time

async def client_a():
    """Client A that connects and sends a message"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Client A: Connected to server")
            test_message = "Hello from Client A!"
            await websocket.send(test_message)
            print(f"Client A: Sent: {test_message}")

            # Wait for responses
            try:
                response1 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Client A: Received: {response1}")
                
                response2 = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Client A: Received: {response2}")
            except asyncio.TimeoutError:
                print("Client A: Timeout waiting for messages")

    except Exception as e:
        print(f"Client A: Error: {e}")

async def client_b():
    """Client B that connects and waits for messages"""
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("Client B: Connected to server")
            
            # Wait for messages from Client A
            try:
                message1 = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"Client B: Received: {message1}")
                
                # Send a response
                response = "Hello back from Client B!"
                await websocket.send(response)
                print(f"Client B: Sent: {response}")
                
            except asyncio.TimeoutError:
                print("Client B: Timeout waiting for messages")

    except Exception as e:
        print(f"Client B: Error: {e}")

async def run_test():
    """Run both clients concurrently"""
    print("Starting dual-client message delivery test...")
    
    # Start Client B first (listening)
    task_b = asyncio.create_task(client_b())
    
    # Wait a moment, then start Client A (sending)
    await asyncio.sleep(1)
    task_a = asyncio.create_task(client_a())
    
    # Wait for both to complete
    await asyncio.gather(task_a, task_b)
    print("Test completed")

if __name__ == "__main__":
    asyncio.run(run_test())