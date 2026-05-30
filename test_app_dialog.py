#!/usr/bin/env python3
"""
Quick manual test to verify Connection Dialog displays buttons properly.
Run the app, wait for the window, and manually click the Connection Settings button.
"""

import tkinter as tk
import customtkinter as ctk
from ui.main_window import MainWindow
from core.events.dispatcher import EventDispatcher

# Create the event dispatcher
dispatcher = EventDispatcher()

# Create the main window
window = MainWindow(dispatcher)

# Automatically open the connection dialog after a brief delay
def auto_open_dialog():
    """Automatically open the connection dialog for testing."""
    window._open_connection_dialog()
    print("[AUTO TEST] Dialog should now be open", flush=True)
    print("[AUTO TEST] Check if buttons are visible!", flush=True)
    # Close after 3 seconds
    window.root.after(3000, window.root.quit)

window.root.after(500, auto_open_dialog)

print("[AUTO TEST] Starting P2P Messenger to test Connection Dialog", flush=True)
window.root.mainloop()
print("[AUTO TEST] Test complete", flush=True)
