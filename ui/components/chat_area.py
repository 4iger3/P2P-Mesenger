"""
Chat area component for displaying the message history.
"""

import tkinter as tk
import customtkinter as ctk
from .chat_bubble import ChatBubble, SystemMessage


class ChatArea(ctk.CTkFrame):
    """
    Central chat area with scrollable message history.
    """

    def __init__(self, parent: ctk.CTkFrame, theme_manager=None) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=10)
        self.theme_manager = theme_manager
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Subscribe to theme changes
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame = header_frame

        title_label = ctk.CTkLabel(header_frame, text="Chat", font=("", 14, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.title_label = title_label

        # Chat display area
        self.canvas = tk.Canvas(self, bg="#0f172a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=(0, 10))

        self.scrollable_frame = tk.Frame(self.canvas, bg="#0f172a")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Auto-scroll to bottom
        self._auto_scroll = True

        # Update colors based on current theme
        self._update_colors()

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        if not self.theme_manager:
            return

        theme = self.theme_manager.get_current_theme()

        # Update main frame
        self.configure(fg_color=theme.get_color("chat_bg"))

        # Update header
        self.header_frame.configure(fg_color=theme.get_color("bg_secondary"))
        self.title_label.configure(text_color=theme.get_color("text_primary"))

        # Update canvas background
        self.canvas.configure(bg=theme.get_color("chat_bg"))
        self.scrollable_frame.configure(bg=theme.get_color("chat_bg"))

    def _on_frame_configure(self, event: tk.Event) -> None:
        """Update scroll region when frame content changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        if self._auto_scroll:
            self.canvas.yview_moveto(1.0)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Update canvas window width when canvas resizes."""
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def add_message(self, text: str, is_own: bool, timestamp: str, username: str = "") -> None:
        """Add a new message to the chat."""
        ChatBubble(self.scrollable_frame, text, timestamp, is_own, username, self.theme_manager).pack(fill="x", pady=2)
        self.canvas.update_idletasks()
        if self._auto_scroll:
            self.canvas.yview_moveto(1.0)

    def add_system_message(self, text: str, timestamp: str = "") -> None:
        """Add a system message (join/leave notifications)."""
        SystemMessage(self.scrollable_frame, text, timestamp, self.theme_manager).pack(fill="x", pady=2)
        self.canvas.update_idletasks()
        if self._auto_scroll:
            self.canvas.yview_moveto(1.0)

    def clear(self) -> None:
        """Clear all messages from the chat."""
        for child in self.scrollable_frame.winfo_children():
            child.destroy()

    def copy_all(self) -> str:
        """Copy all chat content to clipboard."""
        messages = []
        for child in self.scrollable_frame.winfo_children():
            # This is a simplified version - in practice, you'd need to traverse deeper
            for bubble in child.winfo_children():
                if isinstance(bubble, tk.Label):
                    messages.append(bubble.cget("text"))
        return "\n".join(messages)

    def set_auto_scroll(self, enabled: bool) -> None:
        """Enable or disable auto-scrolling to bottom."""
        self._auto_scroll = enabled
        if enabled:
            self.canvas.yview_moveto(1.0)