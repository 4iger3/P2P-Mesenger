import queue

from .websocket_client import WebSocketClient


def create_network_client(request_queue: queue.Queue, response_queue: queue.Queue) -> WebSocketClient:
    client = WebSocketClient(request_queue, response_queue)
    client.start()
    return client
