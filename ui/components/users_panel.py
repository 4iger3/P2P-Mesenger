"""
Users panel component for displaying active users.
"""

import customtkinter as ctk
from core.events.observer import Observer
from core.events.events import USER_LIST_UPDATED


class UsersPanel(ctk.CTkFrame, Observer):
    """
    Right-side panel displaying currently connected users.
    """

    def __init__(self, parent: ctk.CTkFrame, dispatcher, theme_manager=None) -> None:
        super().__init__(parent, fg_color="#1e1e2e", corner_radius=10)
        self.dispatcher = dispatcher
        self.theme_manager = theme_manager
        self.users = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Subscribe to theme changes
        if theme_manager:
            theme_manager.subscribe_to_theme_changes(self._on_theme_changed)

        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#2a2d3a", corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(header_frame, text="Active Users", font=("", 14, "bold"),
                                   text_color="#ffffff")
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.user_count_label = ctk.CTkLabel(header_frame, text="0 users",
                                             font=("", 10), text_color="#c0c0c0")
        self.user_count_label.grid(row=0, column=1, sticky="e", padx=15, pady=10)

        # Users list frame
        self.users_frame = ctk.CTkScrollableFrame(self, fg_color="#0f172a", corner_radius=8)
        self.users_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Attach to dispatcher to receive user list updates
        dispatcher.attach(self)

        # Update colors based on current theme
        self._update_colors()

    def _on_theme_changed(self, theme) -> None:
        """Handle theme change notifications."""
        self._update_colors()

    def _update_colors(self) -> None:
        """Update component colors based on current theme."""
        # This will be called when theme manager is available
        # For now, colors are set in the constructor
        pass

    def update(self, event) -> None:
        """
        Handle user list update events.

        Args:
            event: The event from the dispatcher.
        """
        if event.type == USER_LIST_UPDATED:
            self.update_users(event.data.get("users", []))

    def update_users(self, users: list) -> None:
        """
        Update the displayed user list.

        Args:
            users: List of active usernames.
        """
        self.users = users

        # Clear existing user widgets
        for widget in self.users_frame.winfo_children():
            widget.destroy()

        # Update count
        self.user_count_label.configure(text=f"{len(users)} users")

        # Add user widgets
        for username in users:
            user_frame = ctk.CTkFrame(self.users_frame, fg_color="#2a2d3a", corner_radius=6)
            user_frame.pack(fill="x", padx=5, pady=2)
            user_frame.grid_columnconfigure(1, weight=1)

            # Online indicator
            indicator = ctk.CTkFrame(user_frame, width=8, height=8,
                                     fg_color="#4CAF50", corner_radius=4)
            indicator.grid(row=0, column=0, sticky="w", padx=(10, 8), pady=8)

            # Username
            user_label = ctk.CTkLabel(user_frame, text=username,
                                      font=("", 11), text_color="#ffffff",
                                      anchor="w")
            user_label.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=8)