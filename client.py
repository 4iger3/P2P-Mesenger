#!/usr/bin/env python3
"""Minimal Tkinter client for the centralized P2P Messenger relay server."""

import asyncio
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


class ClientApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("P2P Messenger Client")

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.server_port_var = tk.StringVar(value="8765")
        self.username_var = tk.StringVar(value="")
        self.message_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Not connected")

        self.incoming_queue: queue.Queue[str] = queue.Queue()
        self.websocket = None
        self.websocket_lock = threading.Lock()
        self.loop = asyncio.new_event_loop()
        self.network_thread = threading.Thread(target=self.start_network_loop, daemon=True)
        self.network_thread.start()

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_incoming_messages)
        self.root.mainloop()

    def build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.grid(sticky="nsew")

        tk.Label(frame, text="Server IP:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.server_ip_var, width=15).grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Port:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        tk.Entry(frame, textvariable=self.server_port_var, width=7).grid(row=0, column=3, sticky="w")

        tk.Label(frame, text="Username:").grid(row=0, column=4, sticky="w", padx=(10, 0))
        tk.Entry(frame, textvariable=self.username_var, width=15).grid(row=0, column=5, sticky="w")

        self.connect_button = tk.Button(frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=6, padx=(10, 0))

        self.chat_display = scrolledtext.ScrolledText(frame, width=70, height=20, state="disabled", wrap="word")
        self.chat_display.grid(row=1, column=0, columnspan=7, pady=(10, 0))

        tk.Entry(frame, textvariable=self.message_var, width=55).grid(row=2, column=0, columnspan=5, pady=(10, 0), sticky="w")
        self.send_button = tk.Button(frame, text="Send", command=self.send_message, state="disabled")
        self.send_button.grid(row=2, column=5, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="w")

        tk.Label(frame, textvariable=self.status_var, anchor="w").grid(row=3, column=0, columnspan=7, pady=(10, 0), sticky="we")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def start_network_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def connect(self) -> None:
        if self.websocket is not None:
            return

        host = self.server_ip_var.get().strip()
        port_text = self.server_port_var.get().strip()

        if not host or not port_text:
            self.set_status("Enter server IP and port")
            return

        try:
            port = int(port_text)
        except ValueError:
            self.set_status("Port must be a number")
            return

        self.set_status("Connecting...")
        self.connect_button.config(state="disabled")
        asyncio.run_coroutine_threadsafe(self.connect_to_server(host, port), self.loop)

    async def connect_to_server(self, host: str, port: int) -> None:
        uri = f"ws://{host}:{port}"

        try:
            websocket = await websockets.connect(uri)
            with self.websocket_lock:
                self.websocket = websocket

            self.root.after(0, self.on_connected)
            print("Connected to server")

            async for message in websocket:
                print("Message received")
                self.incoming_queue.put(message)

        except (ConnectionClosedError, ConnectionClosedOK):
            pass
        except Exception as error:
            print(f"Connection error: {error}")
            self.root.after(0, lambda: self.set_status(f"Connection error: {error}"))
        finally:
            with self.websocket_lock:
                self.websocket = None
            self.root.after(0, self.on_disconnected)
            print("Disconnected")

    def send_message(self) -> None:
        text = self.message_var.get().strip()
        if not text:
            return

        username = self.username_var.get().strip()
        message = f"{username}: {text}" if username else text

        with self.websocket_lock:
            websocket = self.websocket

        if websocket is None:
            self.set_status("Not connected")
            return

        self.message_var.set("")
        future = asyncio.run_coroutine_threadsafe(self._send_text(message), self.loop)
        future.add_done_callback(self.send_callback)

    async def _send_text(self, message: str) -> None:
        with self.websocket_lock:
            websocket = self.websocket

        if websocket is None:
            raise RuntimeError("WebSocket is not available")

        await websocket.send(message)
        print("Message sent")

    def send_callback(self, future: asyncio.Future[None]) -> None:
        try:
            future.result()
        except Exception as error:
            print(f"Send error: {error}")
            self.root.after(0, lambda: self.set_status(f"Send error: {error}"))

    def process_incoming_messages(self) -> None:
        try:
            while True:
                message = self.incoming_queue.get_nowait()
                self.append_message(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_incoming_messages)

    def append_message(self, message: str) -> None:
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def on_connected(self) -> None:
        self.set_status("Connected")
        self.send_button.config(state="normal")
        self.connect_button.config(state="disabled")

    def on_disconnected(self) -> None:
        self.set_status("Disconnected")
        self.send_button.config(state="disabled")
        self.connect_button.config(state="normal")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def on_close(self) -> None:
        with self.websocket_lock:
            websocket = self.websocket

        if websocket is not None:
            asyncio.run_coroutine_threadsafe(websocket.close(), self.loop)

        self.loop.call_soon_threadsafe(self.loop.stop)
        self.root.destroy()


if __name__ == "__main__":
    ClientApp()
