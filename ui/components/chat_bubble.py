"""
Chat bubble component for displaying messages in the chat area.
"""

import tkinter as tk
import customtkinter as ctk


class ChatBubble(ctk.CTkFrame):
    """
    Message bubble component with alignment, timestamp, and styling.
    """

    def __init__(self, parent: ctk.CTkFrame, text: str, timestamp: str, is_own: bool,
                 username: str = "", theme_manager=None) -> None:
        super().__init__(parent, fg_color="transparent")
        self.theme_manager = theme_manager

        # Get colors from theme or use defaults
        if theme_manager:
            theme = theme_manager.get_current_theme()
            bubble_bg = theme.get_color("bubble_own") if is_own else theme.get_color("bubble_other")
            text_color = theme.get_color("text_primary")
            timestamp_color = theme.get_color("text_muted")
            username_color = theme.get_color("text_accent")
        else:
            # Fallback colors
            bubble_bg = "#2b5278" if is_own else "#182533"
            text_color = "#e6edf3"
            timestamp_color = "#8b98a5"
            username_color = "#60a5fa"

        # Create bubble frame
        bubble = ctk.CTkFrame(self, fg_color=bubble_bg, corner_radius=12)

        # Username for received messages
        if not is_own and username:
            username_label = ctk.CTkLabel(
                bubble,
                text=username,
                text_color=username_color,
                font=("", 9, "bold"),
                anchor="w"
            )
            username_label.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        # Message text
        message_label = ctk.CTkLabel(
            bubble,
            text=text,
            text_color=text_color,
            wraplength=400,
            justify="left",
            anchor="w",
            font=("", 10),
        )
        message_label.grid(row=1, column=0, sticky="w", padx=12, pady=(2 if not is_own and username else 8, 4))

        # Timestamp
        timestamp_label = ctk.CTkLabel(
            bubble,
            text=timestamp,
            text_color=timestamp_color,
            font=("", 8),
            anchor="e",
        )
        timestamp_label.grid(row=2, column=0, sticky="e", padx=12, pady=(0, 8))

        # Position bubble based on ownership
        if is_own:
            bubble.grid(row=0, column=0, sticky="e", padx=(60, 15))
        else:
            bubble.grid(row=0, column=0, sticky="w", padx=(15, 60))


class SystemMessage(ctk.CTkFrame):
    """
    System message component for join/leave notifications.
    """

    def __init__(self, parent: ctk.CTkFrame, text: str, timestamp: str = "", theme_manager=None) -> None:
        super().__init__(parent, fg_color="transparent")
        self.theme_manager = theme_manager

        # Get colors from theme or use defaults
        if theme_manager:
            theme = theme_manager.get_current_theme()
            bubble_bg = theme.get_color("bubble_system")
            text_color = theme.get_color("text_primary")
            timestamp_color = theme.get_color("text_muted")
        else:
            # Fallback colors
            bubble_bg = "#2a2d3a"
            text_color = "#c084fc"
            timestamp_color = "#8b98a5"

        # System message frame
        system_frame = ctk.CTkFrame(self, fg_color=bubble_bg, corner_radius=8)

        message_label = ctk.CTkLabel(
            system_frame,
            text=text,
            text_color=text_color,
            font=("", 9, "italic"),
            justify="center",
            anchor="center"
        )
        message_label.grid(row=0, column=0, sticky="ew", padx=15, pady=6)

        if timestamp:
            timestamp_label = ctk.CTkLabel(
                system_frame,
                text=timestamp,
                text_color=timestamp_color,
                font=("", 8),
                anchor="center"
            )
            timestamp_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 6))

        system_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=4)
        system_frame.grid_columnconfigure(0, weight=1)