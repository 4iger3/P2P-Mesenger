#!/usr/bin/env python3
"""Test script to diagnose ConnectionDialog button visibility issue."""

import sys
import tkinter as tk
import customtkinter as ctk
from core.events.dispatcher import EventDispatcher
from ui.components.connection_dialog import ConnectionSettingsDialog
from ui.theme.theme_manager import ThemeManager

def test_connection_dialog():
    """Create and display the connection dialog to test button visibility."""
    print("[TEST] Starting ConnectionDialog test", flush=True)
    
    # Create minimal app structure
    root = ctk.CTk()
    root.title("Connection Dialog Test")
    root.geometry("800x600")
    
    # Create necessary objects
    dispatcher = EventDispatcher()
    theme_manager = ThemeManager(dispatcher)
    
    # Create StringVars
    ip_var = tk.StringVar(value="127.0.0.1")
    port_var = tk.StringVar(value="8765")
    username_var = tk.StringVar(value="TestUser")
    
    # Create the dialog
    print("[TEST] Creating ConnectionSettingsDialog...", flush=True)
    dialog = ConnectionSettingsDialog(
        parent=root,
        dispatcher=dispatcher,
        ip_var=ip_var,
        port_var=port_var,
        username_var=username_var,
        theme_manager=theme_manager,
    )
    
    print("[TEST] Dialog created successfully", flush=True)
    print("[TEST] Dialog geometry:", dialog.geometry(), flush=True)
    
    # Schedule test checks after a brief delay to allow rendering
    def check_buttons():
        print("\n[TEST] ===== FINAL BUTTON STATE (after event loop processing) =====", flush=True)
        print(f"[TEST] Dialog geometry: {dialog.geometry()}", flush=True)
        print(f"[TEST] Connect button exists: {dialog.connect_button.winfo_exists()}", flush=True)
        print(f"[TEST] Connect button ismapped: {dialog.connect_button.winfo_ismapped()}", flush=True)
        print(f"[TEST] Connect button width: {dialog.connect_button.winfo_width()}", flush=True)
        print(f"[TEST] Connect button height: {dialog.connect_button.winfo_height()}", flush=True)
        print(f"[TEST] Connect button class: {dialog.connect_button.__class__.__name__}", flush=True)
        print(f"[TEST] Disconnect button exists: {dialog.disconnect_button.winfo_exists()}", flush=True)
        print(f"[TEST] Disconnect button ismapped: {dialog.disconnect_button.winfo_ismapped()}", flush=True)
        print(f"[TEST] Disconnect button width: {dialog.disconnect_button.winfo_width()}", flush=True)
        print(f"[TEST] Disconnect button height: {dialog.disconnect_button.winfo_height()}", flush=True)
        print(f"[TEST] Disconnect button class: {dialog.disconnect_button.__class__.__name__}", flush=True)
        print("[TEST] ===== END FINAL STATE =====\n", flush=True)
        root.quit()
    
    # Schedule the check after the event loop has a chance to render
    root.after(500, check_buttons)
    
    # Run the event loop
    root.mainloop()
    
    print("[TEST] Test completed", flush=True)

if __name__ == "__main__":
    test_connection_dialog()
