import asyncio
import json
import queue
import threading

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK


class WebSocketClient:
    def __init__(self, request_queue: queue.Queue, response_queue: queue.Queue) -> None:
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.loop = asyncio.new_event_loop()
        self.websocket = None
        self.username = ""
        self.receive_task = None
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self._request_loop())
        self.loop.run_forever()

    async def _request_loop(self) -> None:
        while True:
            request = await self.loop.run_in_executor(None, self.request_queue.get)
            request_type = request.get("type")

            if request_type == "connect":
                await self._connect(request.get("host"), request.get("port"), request.get("username"))
            elif request_type == "disconnect":
                await self._disconnect()
            elif request_type == "send_message":
                await self._send_text(request.get("message"))

    async def _connect(self, host: str | None, port: int | None, username: str | None = None) -> None:
        if not host or port is None:
            self.response_queue.put({"type": "error", "error": "Invalid connection parameters"})
            return

        self.username = str(username or "").strip()
        uri = f"ws://{host}:{port}"

        try:
            self.websocket = await websockets.connect(uri)
            self.response_queue.put({"type": "connected"})
            if self.username:
                auth_message = json.dumps({"type": "auth", "user": self.username})
                await self.websocket.send(auth_message)
            self.receive_task = self.loop.create_task(self._receive_messages())
        except Exception as error:
            self.response_queue.put({"type": "error", "error": str(error)})

    async def _receive_messages(self) -> None:
        try:
            async for message in self.websocket:
                self.response_queue.put({"type": "message", "message": message})
        except (ConnectionClosedError, ConnectionClosedOK):
            pass
        except Exception as error:
            self.response_queue.put({"type": "error", "error": str(error)})
        finally:
            self.websocket = None
            self.response_queue.put({"type": "disconnected"})

    async def _disconnect(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            if self.receive_task is not None:
                await self.receive_task
                self.receive_task = None

    async def _send_text(self, message: str | None) -> None:
        if not message or self.websocket is None:
            return

        await self.websocket.send(message)
