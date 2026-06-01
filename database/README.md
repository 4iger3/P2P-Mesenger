# Database Layer for P2P Messenger

## Why SQLite

SQLite was chosen because it is a lightweight, file-based database engine included with Python's standard library. It does not require a separate server process or external dependencies, which keeps the P2P Messenger architecture simple and easy to deploy.

## Database Responsibilities

The database layer is responsible for:
- creating the database file at `data/messenger.db`
- initializing the `users` and `messages` tables automatically when the server starts
- persisting user registration information
- persisting chat messages
- querying message history for future server-side operations

## Interaction with Server and Messaging Modules

Only server-side code accesses `DatabaseManager`. The `server.py` module initializes the database on startup and records chat events as messages are received. The UI layer is not connected directly to the database, preserving the separation between presentation and persistence.

This keeps the database layer aligned with the server's role as the central relay and storage component for message data.
