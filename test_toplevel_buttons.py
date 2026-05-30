#!/usr/bin/env python3
"""Test to compare CTk vs CTkToplevel button rendering."""

import customtkinter as ctk

def test_toplevel_buttons():
    """Create a CTkToplevel window with buttons."""
    root = ctk.CTk()
    root.title("CTk Root")
    root.geometry("600x400")
    
    print("[Test] CTk root window created", flush=True)
    
    # Create a toplevel dialog
    dialog = ctk.CTkToplevel(root)
    dialog.title("CTkToplevel Dialog")
    dialog.geometry("400x300")
    
    print("[Test] CTkToplevel dialog created", flush=True)
    
    # Create a frame to hold buttons in the toplevel
    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    print("[Test] Button frame packed in toplevel", flush=True)
    
    # Create button 1
    btn1 = ctk.CTkButton(button_frame, text="Button 1", fg_color="green")
    btn1.pack(side="left", fill="both", expand=True, padx=(0, 8))
    
    print(f"[Test] Button 1 in toplevel: ismapped={btn1.winfo_ismapped()}, width={btn1.winfo_width()}, height={btn1.winfo_height()}", flush=True)
    
    # Create button 2
    btn2 = ctk.CTkButton(button_frame, text="Button 2", fg_color="red")
    btn2.pack(side="left", fill="both", expand=True, padx=(8, 0))
    
    print(f"[Test] Button 2 in toplevel: ismapped={btn2.winfo_ismapped()}, width={btn2.winfo_width()}, height={btn2.winfo_height()}", flush=True)
    
    def check_after():
        print(f"\n[Test] After event loop from root:", flush=True)
        print(f"[Test] Button 1 in toplevel: ismapped={btn1.winfo_ismapped()}, width={btn1.winfo_width()}, height={btn1.winfo_height()}", flush=True)
        print(f"[Test] Button 2 in toplevel: ismapped={btn2.winfo_ismapped()}, width={btn2.winfo_width()}, height={btn2.winfo_height()}", flush=True)
        root.quit()
    
    root.after(500, check_after)
    root.mainloop()
    
    print("[Test] Completed", flush=True)

if __name__ == "__main__":
    test_toplevel_buttons()
