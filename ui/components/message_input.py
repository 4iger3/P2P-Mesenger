"""
Message input component for sending messages.
"""

import tkinter as tk
import customtkinter as ctk


class MessageInput(ctk.CTkFrame):
    """
    Bottom message input area with multiline text, send button, and character counter.
    """

    def __init__(self, parent: ctk.CTkFrame, send_command: callable, theme_manager=None) -> None:
        super().__init__(parent, fg_color="#1e1e2e", corner_radius=10)
        self.theme_manager = theme_manager
        self.grid_columnconfigure(0, weight=1)

        # Subscribe to theme changes
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(header_frame, text="Send Message", font=("", 12, "bold"),
                                   text_color="#ffffff")
        title_label.grid(row=0, column=0, sticky="w")

        # Input area
        input_frame = ctk.CTkFrame(self, fg_color="#2a2d3a", corner_radius=8)
        input_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        # Multiline text input
        self.textbox = ctk.CTkTextbox(input_frame, wrap="word", fg_color="#2a2d3a",
                                      border_color="#404040", corner_radius=6)
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Send button
        self.send_button = ctk.CTkButton(input_frame, text="Send", command=self._on_send,
                                         width=80, fg_color="#4CAF50", hover_color="#45a049")
        self.send_button.grid(row=0, column=1, sticky="ns", padx=(10, 10), pady=10)
        self.send_button.configure(state="disabled")

        # Character counter and controls
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        controls_frame.grid_columnconfigure(1, weight=1)

        self.char_count_label = ctk.CTkLabel(controls_frame, text="0 / 500",
                                             font=("", 9), text_color="#8b98a5")
        self.char_count_label.grid(row=0, column=0, sticky="w")

        # Enter to send checkbox
        self.enter_to_send_var = tk.BooleanVar(value=True)
        enter_checkbox = ctk.CTkCheckBox(controls_frame, text="Enter to send",
                                         variable=self.enter_to_send_var,
                                         font=("", 9), text_color="#c0c0c0")
        enter_checkbox.grid(row=0, column=2, sticky="e")

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
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") == "transparent":
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkLabel):
                        subchild.configure(text_color=theme.get_color("text_primary"))

        # Update input frame
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") != "transparent":
                child.configure(fg_color=theme.get_color("bg_tertiary"))

        # Update textbox
        self.textbox.configure(
            fg_color=theme.get_color("bg_tertiary"),
            border_color=theme.get_color("border_primary")
        )

        # Update send button
        self.send_button.configure(
            fg_color=theme.get_color("button_primary"),
            hover_color=theme.get_color("button_primary_hover")
        )

        # Update char count label
        self.char_count_label.configure(text_color=theme.get_color("text_muted"))

        # Update checkbox
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkCheckBox):
                        subchild.configure(text_color=theme.get_color("text_secondary"))

    def _on_send(self) -> None:
        """Handle send button click."""
        text = self.get_text().strip()
        if text:
            self.send_command()
            self.clear()

    def _on_enter_pressed(self, event) -> str:
        """Handle Enter key press."""
        if self.enter_to_send_var.get():
            self._on_send()
            return "break"  # Prevent default newline
        return None

    def _on_shift_enter(self, event) -> str:
        """Handle Shift+Enter for newline."""
        return None  # Allow default behavior

    def _update_char_count(self, event=None) -> None:
        """Update character count display."""
        text = self.get_text()
        count = len(text)
        self.char_count_label.configure(text=f"{count} / 500")

        # Limit text length
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