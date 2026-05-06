import queue
import tkinter as tk
from tkinter import ttk, messagebox

from .components import ChatDisplay, ConnectionPanel, MessageInput, StatusBar


class MainWindow:
    def __init__(self, ui_event_queue: queue.Queue, ui_update_queue: queue.Queue) -> None:
        self.ui_event_queue = ui_event_queue
        self.ui_update_queue = ui_update_queue
        self.root = tk.Tk()
        self.root.title("P2P Messenger Client")
        self.root.geometry("1100x700")
        self.root.minsize(900, 500)

        self.server_ip_var = tk.StringVar(value="127.0.0.1")
        self.server_port_var = tk.StringVar(value="8765")
        self.username_var = tk.StringVar(value="")

        self._setup_styles()
        self._build_ui()
        self._bind_events()
        self._setup_context_menu()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(100, self._process_ui_updates)

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Main.TFrame", background="#0f172a")
        style.configure("Header.TLabel", background="#0f172a", foreground="#e6edf3", font=("TkDefaultFont", 12, "bold"))
        style.configure("Status.TLabel", background="#0f172a", foreground="#e6edf3", font=("TkDefaultFont", 9))
        style.configure("Connected.TLabel", foreground="green", font=("TkDefaultFont", 9, "bold"))
        style.configure("Disconnected.TLabel", foreground="red", font=("TkDefaultFont", 9, "bold"))
        style.configure("Connecting.TLabel", foreground="orange", font=("TkDefaultFont", 9, "bold"))
        style.configure("Counter.TLabel", font=("TkDefaultFont", 8), foreground="#8b98a5", background="#0f172a")
        style.configure("Panel.TLabelframe", background="#1e293b", borderwidth=0, relief="flat")
        style.configure("Panel.TLabelframe.Label", background="#1e293b", foreground="#e6edf3")
        style.configure("Panel.TFrame", background="#0f172a")
        style.configure("ChatEntry.TEntry", fieldbackground="#1e293b", background="#1e293b", foreground="#e6edf3")
        style.configure("Accent.TButton", background="#2563eb", foreground="#e6edf3")

    def _build_ui(self) -> None:
        main_container = ttk.Frame(self.root, style="Main.TFrame")
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(main_container, style="Panel.TFrame", padding=10)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(header_frame, text="P2P Messenger", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.connection_status_label = ttk.Label(header_frame, text="Disconnected", style="Status.TLabel")
        self.connection_status_label.grid(row=0, column=1, sticky="e")

        self.connection_panel = ConnectionPanel(
            main_container,
            ip_var=self.server_ip_var,
            port_var=self.server_port_var,
            username_var=self.username_var,
            connect_command=self._on_connect,
        )
        self.connection_panel.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        content_frame = ttk.Frame(main_container, style="Panel.TFrame")
        content_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ChatDisplay(content_frame)
        self.chat_display.grid(row=0, column=0, sticky="nsew")

        self.message_input = MessageInput(main_container, send_command=self._on_send)
        self.message_input.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        self.status_bar = StatusBar(main_container)
        self.status_bar.grid(row=4, column=0, sticky="ew")

    def _bind_events(self) -> None:
        self.root.bind("<Return>", lambda event: self._on_send() if self.message_input.send_button["state"] == "normal" else None)
        self.root.bind("<Control-l>", lambda event: self._clear_chat())
        self.message_input.entry.bind("<Control-a>", self._select_all)
        self.message_input.entry.bind("<KeyRelease>", lambda event: self.message_input.update_char_count())

    def _setup_context_menu(self) -> None:
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy All", command=self._copy_chat)
        self.context_menu.add_command(label="Clear", command=self._clear_chat)
        self.chat_display.canvas.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event: tk.Event) -> None:
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _select_all(self, event: tk.Event) -> str:
        self.message_input.entry.selection_range(0, tk.END)
        return "break"

    def _on_connect(self) -> None:
        self.ui_event_queue.put(
            {
                "type": "connect",
                "host": self.server_ip_var.get(),
                "port": self.server_port_var.get(),
                "username": self.username_var.get(),
            }
        )

    def _on_send(self) -> None:
        self.ui_event_queue.put(
            {
                "type": "send_message",
                "text": self.message_input.text_var.get(),
                "username": self.username_var.get(),
            }
        )

    def _clear_chat(self) -> None:
        if messagebox.askyesno("Clear Chat", "Clear all messages?"):
            self.chat_display.clear()
            self.status_bar.set_message_count(0)
            self.ui_event_queue.put({"type": "clear_chat"})

    def _copy_chat(self) -> None:
        content = self.chat_display.copy_all()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self._set_status("Chat copied to clipboard")
        self.root.after(2000, lambda: self._set_status(self.status_bar.status_label.cget("text")))

    def _on_close(self) -> None:
        self.ui_event_queue.put({"type": "disconnect"})
        self.root.destroy()

    def _process_ui_updates(self) -> None:
        while True:
            try:
                update = self.ui_update_queue.get_nowait()
            except queue.Empty:
                break

            self._apply_update(update)

        self.root.after(100, self._process_ui_updates)

    def _apply_update(self, update: dict[str, object]) -> None:
        action = update.get("type")

        if action == "status":
            text = str(update.get("text", ""))
            self._set_status(text)
            self.connection_status_label.config(text=text)
        elif action == "enable_send":
            self.message_input.send_button.config(state="normal" if update.get("enabled") else "disabled")
        elif action == "enable_connect":
            self.connection_panel.connect_button.config(state="normal" if update.get("enabled") else "disabled")
        elif action == "append_message":
            message = str(update.get("message", ""))
            text, timestamp, is_own = self._parse_message(message)
            self.chat_display.add_message(text, is_own, timestamp)
        elif action == "append_system":
            system_text = str(update.get("message", ""))
            timestamp = str(update.get("timestamp", ""))
            self.chat_display.append_system(system_text, timestamp)
        elif action == "message_count":
            self.status_bar.set_message_count(int(update.get("count", 0)))
        elif action == "clear_input":
            self.message_input.clear()

    def _parse_message(self, message: str) -> tuple[str, str, bool]:
        timestamp = ""
        text = message
        if message.startswith("[") and "] " in message:
            closing_index = message.find("]")
            timestamp = message[1:closing_index]
            text = message[closing_index + 2 :]

        current_user = self.username_var.get().strip()
        is_own = False
        if current_user and text.startswith(f"{current_user}:"):
            is_own = True
            text = text[len(current_user) + 2 :].strip()

        return text, timestamp, is_own

    def _set_status(self, text: str) -> None:
        self.status_bar.set_status(text)

    def _auto_connect(self) -> None:
        """Automatically connect to the default server on startup"""
        self.ui_event_queue.put(
            {
                "type": "connect",
                "host": self.server_ip_var.get(),
                "port": self.server_port_var.get(),
            }
        )

    def run(self) -> None:
        self.root.mainloop()
