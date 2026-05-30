#!/usr/bin/env python3
"""Minimal test for CustomTkinter button rendering."""

import customtkinter as ctk

def test_minimal():
    """Create a minimal window with buttons using pack()."""
    root = ctk.CTk()
    root.title("Minimal Button Test")
    root.geometry("400x300")
    
    print("[Test] Root window created", flush=True)
    
    # Create a frame to hold buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    print("[Test] Button frame packed", flush=True)
    
    # Create button 1
    btn1 = ctk.CTkButton(button_frame, text="Button 1", fg_color="green")
    btn1.pack(side="left", fill="both", expand=True, padx=(0, 8))
    
    print(f"[Test] Button 1: ismapped={btn1.winfo_ismapped()}, width={btn1.winfo_width()}, height={btn1.winfo_height()}", flush=True)
    
    # Create button 2
    btn2 = ctk.CTkButton(button_frame, text="Button 2", fg_color="red")
    btn2.pack(side="left", fill="both", expand=True, padx=(8, 0))
    
    print(f"[Test] Button 2: ismapped={btn2.winfo_ismapped()}, width={btn2.winfo_width()}, height={btn2.winfo_height()}", flush=True)
    
    def check_after():
        print(f"\n[Test] After event loop:", flush=True)
        print(f"[Test] Button 1: ismapped={btn1.winfo_ismapped()}, width={btn1.winfo_width()}, height={btn1.winfo_height()}", flush=True)
        print(f"[Test] Button 2: ismapped={btn2.winfo_ismapped()}, width={btn2.winfo_width()}, height={btn2.winfo_height()}", flush=True)
        root.quit()
    
    root.after(500, check_after)
    root.mainloop()
    
    print("[Test] Completed", flush=True)

if __name__ == "__main__":
    test_minimal()
