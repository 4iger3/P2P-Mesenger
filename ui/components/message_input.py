"""
Message input component for sending messages.
"""

import tkinter as tk
import customtkinter as ctk


class MessageInput(ctk.CTkFrame):
    """
    Bottom message input area with multiline text, send button, and character counter.
    Fully theme-aware with support for light and dark modes.
    """

    def __init__(self, parent: ctk.CTkFrame, send_command: callable, theme_manager=None) -> None:
        super().__init__(parent, fg_color="transparent", corner_radius=10)
        self.theme_manager = theme_manager
        self.send_command = send_command
        self.grid_columnconfigure(0, weight=1)

        # Subscribe to theme changes
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(header_frame, text="Send Message", font=("", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        self.title_label = title_label

        # Input area
        input_frame = ctk.CTkFrame(self, corner_radius=8)
        input_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame = input_frame

        # Multiline text input
        self.textbox = ctk.CTkTextbox(input_frame, wrap="word", corner_radius=6)
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Send button
        self.send_button = ctk.CTkButton(input_frame, text="Send", command=self._on_send, width=80)
        self.send_button.grid(row=0, column=1, sticky="ns", padx=(10, 10), pady=10)
        self.send_button.configure(state="disabled")

        # Character counter and controls
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        controls_frame.grid_columnconfigure(1, weight=1)

        self.char_count_label = ctk.CTkLabel(controls_frame, text="0 / 500", font=("", 9))
        self.char_count_label.grid(row=0, column=0, sticky="w")

        # Enter to send checkbox
        self.enter_to_send_var = tk.BooleanVar(value=True)
        enter_checkbox = ctk.CTkCheckBox(
            controls_frame, 
            text="Enter to send",
            variable=self.enter_to_send_var,
            font=("", 9)
        )
        enter_checkbox.grid(row=0, column=2, sticky="e")
        self.enter_checkbox = enter_checkbox

        # Bind events
        self.textbox.bind("<KeyRelease>", self._update_char_count)
        self.textbox.bind("<Return>", self._on_enter_pressed)
        self.textbox.bind("<Shift-Return>", self._on_shift_enter)

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
        self.configure(fg_color=theme.get_color("bg_secondary"))

        # Update header label
        self.title_label.configure(text_color=theme.get_color("text_primary"))

        # Update input frame
        self.input_frame.configure(fg_color=theme.get_color("bg_tertiary"))

        # Update textbox with theme-aware colors
        self.textbox.configure(
            fg_color=theme.get_color("input_bg"),
            text_color=theme.get_color("input_text"),
            border_color=theme.get_color("input_border"),
            scrollbar_button_color=theme.get_color("scrollbar_button"),
        )

        # Update send button
        self.send_button.configure(
            fg_color=theme.get_color("button_primary"),
            hover_color=theme.get_color("button_primary_hover"),
            text_color=theme.get_color("text_primary")
        )

        # Update char count label
        self.char_count_label.configure(text_color=theme.get_color("text_muted"))

        # Update checkbox
        self.enter_checkbox.configure(text_color=theme.get_color("text_secondary"))

    def _on_send(self) -> None:
        """Handle send button click."""
        text = self.get_text().strip()
        if not text:
            return

        if self.send_command is None:
            print("Warning: send_command not configured for MessageInput")
            return

        self.send_command()
        self.clear()

    def _on_enter_pressed(self, event) -> str:
        """Handle Enter key press."""
        if self.enter_to_send_var.get():
            self._on_send()
            return "break"
        return None

    def _on_shift_enter(self, event) -> str:
        """Handle Shift+Enter for newline."""
        return None

    def _update_char_count(self, event=None) -> None:
        """Update character count display."""
        text = self.get_text()
        count = len(text)
        self.char_count_label.configure(text=f"{count} / 500")

        if count > 500:
            self.textbox.delete("1.0 + 500 chars", "end")

    def get_text(self) -> str:
        """Get the current text content."""
        return self.textbox.get("1.0", "end-1c")

    def set_text(self, text: str) -> None:
        """Set the text content."""
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self._update_char_count()

    def clear(self) -> None:
        """Clear the input field."""
        self.textbox.delete("1.0", "end")
        self._update_char_count()
        self.textbox.focus()

    def set_send_enabled(self, enabled: bool) -> None:
        """Enable or disable the send button."""
        state = "normal" if enabled else "disabled"
        self.send_button.configure(state=state)
