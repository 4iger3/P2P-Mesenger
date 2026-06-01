"""SQLite persistence manager for the P2P Messenger server."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .schema import CREATE_MESSAGES_TABLE, CREATE_USERS_TABLE


class DatabaseManager:
    """Manage SQLite persistence for users and messages."""

    def __init__(self, database_path: str | Path = Path("data/messenger.db")) -> None:
        self.database_path = Path(database_path)

    def initialize_database(self) -> None:
        """Create the database file and tables when the server starts."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path, timeout=30) as connection:
            self._configure_connection(connection)
            cursor = connection.cursor()
            cursor.execute(CREATE_USERS_TABLE)
            cursor.execute(CREATE_MESSAGES_TABLE)
            connection.commit()

    def _configure_connection(self, connection: sqlite3.Connection) -> None:
        """Configure SQLite connection settings for consistent behavior."""
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        self._configure_connection(connection)
        return connection

    def create_user(self, username: str) -> dict[str, Any] | None:
        """Create a new user record if it does not already exist."""
        username = username.strip()
        if not username:
            return None

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, created_at) VALUES (?, ?)",
                (username, datetime.utcnow().isoformat()),
            )
            connection.commit()

        return self.get_user(username)

    def get_user(self, username: str) -> dict[str, Any] | None:
        """Return a user record by username, or None if not found."""
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, username, created_at FROM users WHERE username = ?",
                (username.strip(),),
            )
            row = cursor.fetchone()

        return dict(row) if row else None

    def save_message(
        self,
        sender: str,
        receiver: str | None,
        content: str,
        timestamp: str | None = None,
    ) -> int:
        """Persist a chat message to the messages table."""
        timestamp = timestamp or datetime.utcnow().isoformat()
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, receiver, content, timestamp) VALUES (?, ?, ?, ?)",
                (sender.strip(), receiver.strip() if receiver else None, content, timestamp),
            )
            connection.commit()
            return cursor.lastrowid

    def get_message_history(
        self,
        sender: str | None = None,
        receiver: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return recent message history optionally filtered by sender or receiver."""
        query = "SELECT id, sender, receiver, content, timestamp FROM messages"
        conditions: list[str] = []
        parameters: list[Any] = []

        if sender:
            conditions.append("sender = ?")
            parameters.append(sender.strip())

        if receiver:
            conditions.append("receiver = ?")
            parameters.append(receiver.strip())

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ?"
        parameters.append(limit)

        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, tuple(parameters))
            rows = cursor.fetchall()

        return [dict(row) for row in rows]
