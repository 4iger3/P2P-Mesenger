# P2P Messenger Roadmap

## MVP Scope
- Centralized WebSocket server that receives messages from clients and relays them to all connected peers
- Tkinter client application with server connection, message input field, send button, and chat history display
- No message history stored on the server; priority on simplicity and stability

## Development Stages / Sprints
1. Preparation sprint
   - project setup, `requirements.txt`, basic structure
   - develop `server.py` with WebSocket listener and a set of active connections
2. Client sprint
   - build Tkinter GUI with IP/port fields, Connect and Send buttons
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

