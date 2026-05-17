"""
Status panel component for displaying connection and message statistics.
"""

import customtkinter as ctk


class StatusPanel(ctk.CTkFrame):
    """
    Status panel showing connection state and message count.
    """

    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent, fg_color="#2a2d3a", corner_radius=8)
        self.grid_columnconfigure(0, weight=1)
        self.message_count = 0

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Disconnected",
                                         font=("", 10), text_color="#ff6b6b")
        self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # Message count
        self.message_count_label = ctk.CTkLabel(self, text="Messages: 0",
                                                font=("", 9), text_color="#c0c0c0")
        self.message_count_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

    def set_status(self, text: str, is_connected: bool = False) -> None:
        """Update the status text and color."""
        color = "#4CAF50" if is_connected else "#ff6b6b"
        self.status_label.configure(text=text, text_color=color)

    def set_message_count(self, count: int) -> None:
        """Set the message count."""
        self.message_count = count
        self.message_count_label.configure(text=f"Messages: {count}")

    def increment_message_count(self) -> None:
        """Increment the message count."""
        self.message_count += 1
        self.message_count_label.configure(text=f"Messages: {self.message_count}")