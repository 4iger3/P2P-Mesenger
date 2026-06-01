import asyncio
import json
import unittest

import websockets

from core.events.dispatcher import EventDispatcher
from core.events.events import Event, OPEN_PRIVATE_CHAT
from core.message_model import MessageModel
from ui.private_chat_window import PrivateChatWindowManager


class DummyPrivateChatWindow:
    """Dummy window used to test private chat manager behavior."""

    def __init__(self, parent, dispatcher, local_username, peer_username, theme_manager, on_close=None):
        self.parent = parent
        self.dispatcher = dispatcher
        self.local_username = local_username
        self.peer_username = peer_username
        self.on_close = on_close
        self.focused = False
        self.closed = False

    def winfo_exists(self):
        return not self.closed

    def focus_window(self):
        self.focused = True

    def destroy(self):
        self.closed = True


class PrivateMessageFeatureTests(unittest.TestCase):
    def test_message_model_serialization_public(self):
        model = MessageModel(type="public_message", sender="Alice", text="Hello")
        payload = json.loads(model.to_json())

        self.assertEqual(payload["type"], "public_message")
        self.assertEqual(payload["sender"], "Alice")
        self.assertEqual(payload["text"], "Hello")

        parsed = MessageModel.from_payload(payload)
        self.assertEqual(parsed.type, "public_message")
        self.assertEqual(parsed.sender, "Alice")
        self.assertEqual(parsed.text, "Hello")

    def test_message_model_serialization_private(self):
        model = MessageModel(
            type="private_message",
            sender="Alice",
            recipient="Bob",
            text="Secret",
        )
        payload = json.loads(model.to_json())

        self.assertEqual(payload["type"], "private_message")
        self.assertEqual(payload["sender"], "Alice")
        self.assertEqual(payload["recipient"], "Bob")
        self.assertEqual(payload["text"], "Secret")

        parsed = MessageModel.from_payload(payload)
        self.assertEqual(parsed.type, "private_message")
        self.assertEqual(parsed.sender, "Alice")
        self.assertEqual(parsed.recipient, "Bob")
        self.assertEqual(parsed.text, "Secret")

    def test_private_chat_manager_prevents_duplicate_windows(self):
        dispatcher = EventDispatcher()
        manager = PrivateChatWindowManager(
            parent=None,
            dispatcher=dispatcher,
            local_username_getter=lambda: "Alice",
            theme_manager=None,
            window_class=DummyPrivateChatWindow,
        )

        window_one = manager.open_chat("Bob")
        window_two = manager.open_chat("Bob")

        self.assertIs(window_one, window_two)
        self.assertTrue(window_one.focused)

        manager.open_chat("Bob")
        self.assertTrue(window_one.focused)

    def test_open_private_chat_event_constant(self):
        self.assertEqual(OPEN_PRIVATE_CHAT, "open_private_chat")
        dispatcher = EventDispatcher()
        captured = []

        class Recorder:
            def update(self, event):
                captured.append(event)

        recorder = Recorder()
        dispatcher.attach(recorder)
        event = Event(OPEN_PRIVATE_CHAT, {"username": "Bob"})
        dispatcher.notify(event)

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0].type, OPEN_PRIVATE_CHAT)
        self.assertEqual(captured[0].data["username"], "Bob")


class ServerRoutingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from server import handle_client, active_connections, client_usernames, username_to_websocket

        active_connections.clear()
        client_usernames.clear()
        username_to_websocket.clear()

        self.server = await websockets.serve(handle_client, "127.0.0.1", 8766)
        await asyncio.sleep(0.1)

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def _drain_messages(self, websocket):
        messages = []
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.05)
                messages.append(message)
            except asyncio.TimeoutError:
                break
        return messages

    async def test_private_messages_delivered_only_to_recipient(self):
        alice = await websockets.connect("ws://127.0.0.1:8766")
        bob = await websockets.connect("ws://127.0.0.1:8766")

        await alice.send(json.dumps({"type": "auth", "user": "Alice"}))
        await bob.send(json.dumps({"type": "auth", "user": "Bob"}))
        await asyncio.sleep(0.1)

        await self._drain_messages(alice)
        await self._drain_messages(bob)

        private_message = {
            "type": "private_message",
            "sender": "Alice",
            "recipient": "Bob",
            "text": "Secret Hello",
        }
        await alice.send(json.dumps(private_message))

        received_by_bob = await asyncio.wait_for(bob.recv(), timeout=1.0)
        payload = json.loads(received_by_bob)
        self.assertEqual(payload["type"], "private_message")
        self.assertEqual(payload["sender"], "Alice")
        self.assertEqual(payload["recipient"], "Bob")
        self.assertEqual(payload["text"], "Secret Hello")

        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(alice.recv(), timeout=0.2)

        await alice.close()
        await bob.close()

    async def test_invalid_recipient_is_ignored(self):
        alice = await websockets.connect("ws://127.0.0.1:8766")
        await alice.send(json.dumps({"type": "auth", "user": "Alice"}))
        await asyncio.sleep(0.1)
        await self._drain_messages(alice)

        invalid_message = {
            "type": "private_message",
            "sender": "Alice",
            "recipient": "Nobody",
            "text": "Should not route",
        }
        await alice.send(json.dumps(invalid_message))

        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(alice.recv(), timeout=0.2)

        await alice.close()


if __name__ == "__main__":
    unittest.main()
