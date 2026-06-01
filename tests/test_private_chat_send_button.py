#!/usr/bin/env python3
"""
Test: Verify Private Chat Send Button Fix

Tests that:
1. Send button is enabled on window creation
2. Clicking Send button dispatches PRIVATE_MESSAGE_SENT event
3. Connection changes properly enable/disable the send button
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from core.events.dispatcher import EventDispatcher
from core.events.events import Event, PRIVATE_MESSAGE_SENT, CONNECTION_CHANGED
from ui.private_chat_window import PrivateChatWindow


class PrivateChatSendButtonTests(unittest.TestCase):
    """Test Send button in PrivateChatWindow."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.dispatcher = EventDispatcher()
        self.captured_events = []

        class EventCapture:
            def __init__(self, tests_instance):
                self.tests = tests_instance

            def update(self, event):
                self.tests.captured_events.append(event)

        self.capture_observer = EventCapture(self)
        self.dispatcher.attach(self.capture_observer)

    def tearDown(self):
        """Clean up."""
        self.root.destroy()

    def test_send_button_enabled_on_creation(self):
        """Verify send button is enabled when window is created."""
        print("\n[TEST] Send button enabled on creation")

        window = PrivateChatWindow(
            parent=self.root,
            dispatcher=self.dispatcher,
            local_username="Alice",
            peer_username="Bob",
            theme_manager=None,
        )

        # Check that send button exists and is enabled (state="normal")
        self.assertIsNotNone(window.input_area.send_button)
        button_state = window.input_area.send_button.cget("state")
        print(f"  Send button state: {button_state}")
        self.assertEqual(button_state, "normal", "Send button should be enabled (state='normal')")

        window._on_close()
        print("  ✅ PASS: Send button is enabled on creation\n")

    def test_send_button_click_dispatches_event(self):
        """Verify clicking Send button dispatches PRIVATE_MESSAGE_SENT event."""
        print("\n[TEST] Send button click dispatches event")

        window = PrivateChatWindow(
            parent=self.root,
            dispatcher=self.dispatcher,
            local_username="Alice",
            peer_username="Bob",
            theme_manager=None,
        )

        # Type a message
        window.input_area.textbox.insert("1.0", "Hello Bob!")
        print("  Message typed: 'Hello Bob!'")

        # Click send button
        window.input_area.send_button.invoke()
        print("  Send button clicked")

        # Verify event was dispatched
        self.assertGreater(len(self.captured_events), 0, "Event should be dispatched")

        # Find PRIVATE_MESSAGE_SENT event
        private_message_events = [e for e in self.captured_events if e.type == PRIVATE_MESSAGE_SENT]
        self.assertGreater(len(private_message_events), 0, "PRIVATE_MESSAGE_SENT event should be dispatched")

        event = private_message_events[0]
        print(f"  Event type: {event.type}")
        print(f"  Event data: sender={event.data.get('sender')}, recipient={event.data.get('recipient')}, text={event.data.get('text')}")

        self.assertEqual(event.data.get("sender"), "Alice")
        self.assertEqual(event.data.get("recipient"), "Bob")
        self.assertEqual(event.data.get("text"), "Hello Bob!")

        # Verify message was cleared
        remaining_text = window.input_area.textbox.get("1.0", "end-1c")
        print(f"  Remaining text after send: '{remaining_text}'")
        self.assertEqual(remaining_text, "", "Textbox should be cleared after send")

        window._on_close()
        print("  ✅ PASS: Send button click dispatches correct event\n")

    def test_connection_changed_disables_send_button(self):
        """Verify send button is disabled when connection is lost."""
        print("\n[TEST] Connection change disables send button")

        window = PrivateChatWindow(
            parent=self.root,
            dispatcher=self.dispatcher,
            local_username="Alice",
            peer_username="Bob",
            theme_manager=None,
        )

        # Verify button is enabled initially
        initial_state = window.input_area.send_button.cget("state")
        print(f"  Initial button state: {initial_state}")
        self.assertEqual(initial_state, "normal")

        # Simulate connection loss
        disconnect_event = Event(CONNECTION_CHANGED, {"connected": False})
        window.update(disconnect_event)

        disabled_state = window.input_area.send_button.cget("state")
        print(f"  Button state after disconnect: {disabled_state}")
        self.assertEqual(disabled_state, "disabled", "Send button should be disabled when connection is lost")

        # Simulate connection restored
        connect_event = Event(CONNECTION_CHANGED, {"connected": True})
        window.update(connect_event)

        reconnected_state = window.input_area.send_button.cget("state")
        print(f"  Button state after reconnect: {reconnected_state}")
        self.assertEqual(reconnected_state, "normal", "Send button should be enabled when connection is restored")

        window._on_close()
        print("  ✅ PASS: Connection changes properly control send button\n")

    def test_enter_key_still_works(self):
        """Verify Enter key still sends messages (regression test)."""
        print("\n[TEST] Enter key still works after fix")

        # Clear captured events
        self.captured_events.clear()

        window = PrivateChatWindow(
            parent=self.root,
            dispatcher=self.dispatcher,
            local_username="Alice",
            peer_username="Bob",
            theme_manager=None,
        )

        # Type a message
        window.input_area.textbox.insert("1.0", "Test message")
        print("  Message typed: 'Test message'")

        # Simulate Enter key press
        window.input_area._on_enter_pressed(None)
        print("  Enter key pressed")

        # Verify event was dispatched
        private_message_events = [e for e in self.captured_events if e.type == PRIVATE_MESSAGE_SENT]
        self.assertGreater(len(private_message_events), 0, "PRIVATE_MESSAGE_SENT event should be dispatched on Enter")

        window._on_close()
        print("  ✅ PASS: Enter key still dispatches events\n")


if __name__ == "__main__":
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(PrivateChatSendButtonTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - Send button fix verified!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*70)
