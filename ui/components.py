import tkinter as tk
from tkinter import ttk


class ConnectionPanel(ttk.LabelFrame):
    def __init__(self, parent: ttk.Widget, ip_var: tk.StringVar, port_var: tk.StringVar, username_var: tk.StringVar, connect_command: callable) -> None:
        super().__init__(parent, text="Connection Settings", padding=10, style="Panel.TLabelframe")
        self.grid_columnconfigure(7, weight=1)

        ttk.Label(self, text="IP:", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(self, textvariable=ip_var, width=14).grid(row=0, column=1, sticky="ew", padx=(3, 8))

        ttk.Label(self, text="Port:", style="Header.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Entry(self, textvariable=port_var, width=8).grid(row=0, column=3, sticky="ew", padx=(3, 8))

        ttk.Label(self, text="User:", style="Header.TLabel").grid(row=0, column=4, sticky="w")
        ttk.Entry(self, textvariable=username_var, width=14).grid(row=0, column=5, sticky="ew", padx=(3, 8))

        ttk.Frame(self).grid(row=0, column=6, padx=5)

        self.connect_button = ttk.Button(self, text="Connect", command=connect_command, state="normal")
        self.connect_button.grid(row=0, column=7, sticky="e")


class MessageBubble(tk.Frame):
    def __init__(self, parent: ttk.Widget, text: str, timestamp: str, is_own: bool) -> None:
        bg_color = "#2b5278" if is_own else "#182533"
        super().__init__(parent, bg=parent["bg"])

        bubble = tk.Frame(self, bg=bg_color, padx=12, pady=8)
        bubble.grid(row=0, column=0, sticky="e" if is_own else "w")

        message_label = tk.Label(
            bubble,
            text=text,
            bg=bg_color,
            fg="#e6edf3",
            wraplength=420,
            justify="left",
            anchor="w",
            font=("TkDefaultFont", 10),
        )
        message_label.grid(row=0, column=0, sticky="w")

        timestamp_label = tk.Label(
            bubble,
            text=timestamp,
            bg=bg_color,
            fg="#8b98a5",
            font=("TkDefaultFont", 8),
            anchor="e",
        )
        timestamp_label.grid(row=1, column=0, sticky="e", pady=(6, 0))

        self.grid_columnconfigure(0, weight=1)
        bubble.grid(padx=(40, 10) if is_own else (10, 40), sticky="e" if is_own else "w")


class ChatDisplay(ttk.LabelFrame):
    def __init__(self, parent: ttk.Widget) -> None:
        super().__init__(parent, text="Chat", padding=8, style="Panel.TLabelframe")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="#0f172a", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

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
            font=("TkDefaultFont", 9, "italic"),
        )
        system_label.pack(padx=10, pady=4)
        if timestamp:
            timestamp_label = tk.Label(
                system_frame,
                text=timestamp,
                bg="#0f172a",
                fg="#8b98a5",
                font=("TkDefaultFont", 8),
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


class MessageInput(ttk.LabelFrame):
    def __init__(self, parent: ttk.Widget, send_command: callable) -> None:
        super().__init__(parent, text="Message", padding=10, style="Panel.TLabelframe")
        self.grid_columnconfigure(0, weight=1)

        self.text_var = tk.StringVar(value="")

        self.input_frame = ttk.Frame(self, style="Panel.TFrame")
        self.input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ttk.Entry(self.input_frame, textvariable=self.text_var, style="ChatEntry.TEntry")
        self.entry.grid(row=0, column=0, sticky="ew", ipady=6)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=send_command, state="disabled", style="Accent.TButton")
        self.send_button.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        self.char_count_label = ttk.Label(self, text="0 / 500", style="Counter.TLabel")
        self.char_count_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

    def clear(self) -> None:
        self.text_var.set("")
        self.entry.focus()

    def update_char_count(self) -> None:
        text = self.text_var.get()
        count = len(text)
        self.char_count_label.config(text=f"{count} / 500")
        if count > 500:
            self.text_var.set(text[:500])


class StatusBar(ttk.Frame):
    def __init__(self, parent: ttk.Widget) -> None:
        super().__init__(parent, relief="sunken", padding=8, style="StatusBar.TFrame")
        self.grid_columnconfigure(1, weight=1)

        self.status_label = ttk.Label(self, text="Disconnected", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.message_count_label = ttk.Label(self, text="Messages: 0", style="Status.TLabel")
        self.message_count_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

    def set_status(self, text: str) -> None:
        self.status_label.config(text=text)

    def set_message_count(self, count: int) -> None:
        self.message_count_label.config(text=f"Messages: {count}")
