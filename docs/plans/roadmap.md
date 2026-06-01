# P2P Messenger Roadmap

## Current implementation status
This roadmap reflects the actual repository structure and current behavior in the codebase.

### DONE
- core/
  - Event-driven architecture with `EventDispatcher`, `Observer`, and `Controller`.
  - Application state tracking in `AppState` and structured messages via `MessageModel`.
  - Controller validates send/connect requests and routes them to network logic.
- network/
  - `WebSocketClient` runs an `asyncio` event loop in a separate background thread.
  - WebSocket connect/disconnect, receive loop, and send operations are implemented.
  - Received server payloads are converted into dispatcher events, including `MESSAGE_RECEIVED`, `PRIVATE_MESSAGE_RECEIVED`, and `USER_LIST_UPDATED`.
- ui/
  - CustomTkinter GUI with server IP, port, connect, send, and chat history display.
  - UI remains decoupled from persistence; it communicates through the event dispatcher.
  - Active users list and private messaging components are present in the UI layer.
- database/
  - SQLite persistence layer initialized on server startup.
  - `data/messenger.db` is created automatically.
  - `users` and `messages` tables are created by the server-side `DatabaseManager`.
- docs/
  - Architecture and feature documentation exist under `docs/` and reflect the current modular layout.

### IN PROGRESS
- database persistence stabilization
  - The server-side database layer is active, but storage behavior and history retrieval require validation and potential extension.
  - Message history support exists at the database layer but is not yet reflected in the UI experience.
- documentation sync
  - Keep architecture, roadmap, and feature requirement documents aligned with live code and repository layout.

### PLANNED
- UI validation and error handling improvements.
- stronger server-side persistence behavior and message lifecycle clarity.
- better integration of stored message history into the client experience.
- expanded documentation for private messaging and database behavior.
- automated verification of network and persistence interactions.
