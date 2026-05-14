import tkinter as tk
import customtkinter as ctk


class ConnectionPanel(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, ip_var: tk.StringVar, port_var: tk.StringVar, username_var: tk.StringVar, connect_command: callable) -> None:
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)
        
        # Create a label for "Connection Settings"
        label_frame = ctk.CTkFrame(self)
        label_frame.grid(row=0, column=0, columnspan=8, sticky="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(label_frame, text="Connection Settings", font=("", 10, "bold")).pack(anchor="w")

        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, columnspan=8, sticky="ew", padx=10, pady=(5, 10))
        content_frame.grid_columnconfigure(1, weight=0)
        content_frame.grid_columnconfigure(3, weight=0)
        content_frame.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(content_frame, text="IP:", font=("", 10)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkEntry(content_frame, textvariable=ip_var, width=100).grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(content_frame, text="Port:", font=("", 10)).grid(row=0, column=2, sticky="w", padx=(0, 5))
        ctk.CTkEntry(content_frame, textvariable=port_var, width=60).grid(row=0, column=3, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(content_frame, text="User:", font=("", 10)).grid(row=0, column=4, sticky="w", padx=(0, 5))
        ctk.CTkEntry(content_frame, textvariable=username_var, width=100).grid(row=0, column=5, sticky="ew", padx=(0, 10))

        self.connect_button = ctk.CTkButton(content_frame, text="Connect", command=connect_command)
        self.connect_button.grid(row=0, column=6, sticky="e")


class MessageBubble(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, text: str, timestamp: str, is_own: bool) -> None:
        bg_color = "#2b5278" if is_own else "#182533"
        super().__init__(parent, fg_color="transparent")

        bubble = ctk.CTkFrame(self, fg_color=bg_color, corner_radius=8)
        bubble.grid(row=0, column=0, sticky="e" if is_own else "w")

        message_label = ctk.CTkLabel(
            bubble,
            text=text,
            text_color="#e6edf3",
            wraplength=420,
            justify="left",
            anchor="w",
            font=("", 10),
        )
        message_label.grid(row=0, column=0, sticky="w", padx=12, pady=8)

        timestamp_label = ctk.CTkLabel(
            bubble,
            text=timestamp,
            text_color="#8b98a5",
            font=("", 8),
            anchor="e",
        )
        timestamp_label.grid(row=1, column=0, sticky="e", padx=12, pady=(0, 8))

        bubble.grid(padx=(40, 10) if is_own else (10, 40), sticky="e" if is_own else "w")


class ChatDisplay(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create label for "Chat"
        label_frame = ctk.CTkFrame(self)
        label_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 5))
        ctk.CTkLabel(label_frame, text="Chat", font=("", 10, "bold")).pack(anchor="w")

        self.canvas = tk.Canvas(self, bg="#0f172a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        self.scrollable_frame = tk.Frame(self.canvas, bg="#0f172a")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_frame_configure(self, event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def add_message(self, text: str, is_own: bool, timestamp: str) -> None:
        MessageBubble(self.scrollable_frame, text, timestamp, is_own).pack(fill="x", pady=4)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def append_message(self, message: str) -> None:
        timestamp = ""
        text = message
        if message.startswith("[") and "] " in message:
            closing_index = message.find("]")
            timestamp = message[1:closing_index]
            text = message[closing_index + 2 :]
        self.add_message(text, is_own=False, timestamp=timestamp)

    def append_system(self, message: str, timestamp: str = "") -> None:
        system_frame = tk.Frame(self.scrollable_frame, bg="#0f172a")
        system_label = tk.Label(
            system_frame,
            text=message,
            bg="#0f172a",
            fg="#c084fc",
            wraplength=520,
            justify="center",
            font=("", 9, "italic"),
        )
        system_label.pack(padx=10, pady=4)
        if timestamp:
            timestamp_label = tk.Label(
                system_frame,
                text=timestamp,
                bg="#0f172a",
                fg="#8b98a5",
                font=("", 8),
            )
            timestamp_label.pack(anchor="e", padx=10)
        system_frame.pack(fill="x", pady=4)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def clear(self) -> None:
        for child in self.scrollable_frame.winfo_children():
            child.destroy()

    def copy_all(self) -> str:
        messages = []
        for child in self.scrollable_frame.winfo_children():
            for bubble in child.winfo_children():
                if isinstance(bubble, tk.Label):
                    messages.append(bubble.cget("text"))
        return "\n".join(messages)


class MessageInput(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, send_command: callable) -> None:
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        
        # Create label for "Message"
        label_frame = ctk.CTkFrame(self)
        label_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(label_frame, text="Message", font=("", 10, "bold")).pack(anchor="w")

        self.text_var = tk.StringVar(value="")

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, textvariable=self.text_var)
        self.entry.grid(row=0, column=0, sticky="ew", ipady=6)

        self.send_button = ctk.CTkButton(self.input_frame, text="Send", command=send_command)
        self.send_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.send_button.configure(state="disabled")

        self.char_count_label = ctk.CTkLabel(self, text="0 / 500", font=("", 8), text_color="#8b98a5")
        self.char_count_label.grid(row=2, column=0, sticky="w", padx=10, pady=(5, 10))

    def clear(self) -> None:
        self.text_var.set("")
        self.entry.focus()

    def update_char_count(self) -> None:
        text = self.text_var.get()
        count = len(text)
        self.char_count_label.configure(text=f"{count} / 500")
        if count > 500:
            self.text_var.set(text[:500])


class StatusBar(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame) -> None:
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)
        self.message_count = 0

        self.status_label = ctk.CTkLabel(self, text="Disconnected", font=("", 9))
        self.status_label.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.message_count_label = ctk.CTkLabel(self, text="Messages: 0", font=("", 9))
        self.message_count_label.grid(row=0, column=2, sticky="e", padx=8, pady=8)

    def set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def set_message_count(self, count: int) -> None:
        self.message_count = count
        self.message_count_label.configure(text=f"Messages: {count}")

    def increment_message_count(self) -> None:
        self.message_count += 1
        self.message_count_label.configure(text=f"Messages: {self.message_count}")

