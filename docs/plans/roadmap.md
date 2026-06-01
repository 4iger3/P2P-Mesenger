# P2P Messenger Roadmap

## MVP Scope
- Centralized WebSocket server that receives messages from clients and relays them to all connected peers
- CustomTkinter client application with server connection, message input field, send button, and chat history display
- No message history stored on the server; priority on simplicity and stability

## Development Stages / Sprints
1. Preparation sprint
   - project setup, `requirements.txt`, basic structure
   - develop `server.py` with WebSocket listener and a set of active connections
2. Client sprint
   - build CustomTkinter GUI with IP/port fields, Connect and Send buttons
   - implement a separate thread for receiving messages
3. Network stability and data delivery
   - handle client disconnects and close WebSocket connections cleanly
   - test message delivery among multiple clients
4. Testing and refactoring
   - unit tests and manual testing on Linux
   - simplify code, document, and ensure compliance with AGENTS.md
5. **Architecture improvements** ✅ **COMPLETE**
   - **Observer pattern implementation** ✅ **COMPLETE**
     - Replaced queue-based communication with event-driven Observer pattern
     - Created core/events module with EventDispatcher (Subject)
     - AppState, MainWindow, and WebSocketClient now implement Observer pattern
     - All components communicate through centered EventDispatcher
     - Thread-safe event dispatch with threading.Lock
     - Reduced coupling between UI, network, and core layers
6. **Active Users Panel** ✅ **COMPLETE**
   - **Real-time user tracking** ✅ **COMPLETE**
     - Server maintains list of connected usernames
     - Broadcasts user list updates on join/leave events
     - Client displays active users in dedicated right-side panel
     - Observer pattern integration for event-driven updates
     - Dark theme styling with online indicators
     - Scrollable user list for large groups

7. **Database persistence layer** ✅ **COMPLETE**
   - Uses SQLite and stores data in `data/messenger.db`
   - Server initializes the database and creates `users` and `messages` tables automatically on startup
   - Server-side only access ensures the UI remains decoupled from persistence

## Core Messaging Functionality
- Server receives text messages from any client
- Server relays incoming messages to all active connected clients
- Client displays received messages in a read-only history window
- Messages are sent only after a successful server connection

## GUI Improvements
- Save server address between sessions
- Friendly IP and port input with defaults: `127.0.0.1` and `8765`
- Allow chat history scrolling and prevent direct editing of history
- Handle network errors within the interface

## Networking and Server Stability Tasks
- Store active connections in a `set`
- Protect the server from crashing when a client disconnects
- Configure the server listener on `0.0.0.0` and port `8765` (with CLI override support)
- Avoid storing message history on the server; only relay messages

## Testing and Refactoring Stages
- Manual testing with two or more clients on a local machine
- Verify correct behavior during client disconnect/reconnect events
- Refactor based on test results: readability, exception handling, and comments in English


## Future Release Features
- Improved validation for user-entered IP and port values
- Local saving of server settings to a configuration file
- Option to set a username and display it in chat messages
- Minor UX improvements for message history and connection controls
- Better error reporting for network issues

## Private Direct Messages (DMs) ✅ **COMPLETE**
- **Private Chat Architecture** ✅ **COMPLETE**
  - **Window-based private conversations** ✅ **COMPLETE**
    - Dedicated PrivateChatWindow component for each peer
    - PrivateChatWindowManager prevents duplicate windows
    - Windows reuse existing ChatArea and MessageInput components
    - Auto-open windows when receiving private messages
  - **Structured message model** ✅ **COMPLETE**
    - MessageModel enum-like type field: public_message | private_message
    - Sender, recipient, and text fields for routing decisions
    - JSON serialization for network transmission
    - Backward compatibility with legacy text format
  - **Server-side private routing** ✅ **COMPLETE**
    - Server maintains username_to_websocket mapping
    - Private messages routed ONLY to recipient, not broadcast
    - Invalid recipients logged and ignored
    - Graceful handling of disconnected recipients
  - **Event-driven integration** ✅ **COMPLETE**
    - OPEN_PRIVATE_CHAT event when user clicks in UsersPanel
    - PRIVATE_MESSAGE_SENT event dispatched by PrivateChatWindow
    - PRIVATE_MESSAGE_RECEIVED event routed by WebSocketClient
    - UsersPanel single/double-click to open private chat
  - **Test coverage** ✅ **COMPLETE**
    - Message serialization/deserialization tests
    - Duplicate window prevention tests
    - Server routing to correct recipient only
    - Invalid recipient handling in server
    - Event dispatch verification
