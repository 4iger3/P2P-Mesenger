# Architecture: Message Sending Flow & Private Direct Messages

## System Architecture Diagram

```mermaid
graph TB
    User["🧑 User"]
    GUI["Tkinter GUI"]
    Dispatcher["EventDispatcher\n(Subject)"]
    UI["MainWindow\n(Observer)"]
    State["AppState\n(Observer)"]
    Network["WebSocketClient\n(Observer)"]
    Server["🖥️ WebSocket Server"]
    Database["SQLite Database\n(data/messenger.db)"]
    Users["UsersPanel\n(Observer)"]
    PrivateChat["PrivateChatWindow\n(Observer)"]

    User -->|Types & Sends| GUI
    GUI -->|SEND_MESSAGE\nCONNECT_REQUEST\nOPEN_PRIVATE_CHAT| Dispatcher
    Dispatcher -->|Notify| UI
    Dispatcher -->|Notify| State
    Dispatcher -->|Notify| Network
    Dispatcher -->|Notify| Users
    Dispatcher -->|Notify| PrivateChat
    Network -->|MESSAGE_RECEIVED\nPRIVATE_MESSAGE_RECEIVED\nCONNECTION_CHANGED\nUSER_LIST_UPDATED| Dispatcher
    Dispatcher -->|Update| UI
    Dispatcher -->|Update| State
    Dispatcher -->|Update| Users
    Dispatcher -->|Update| PrivateChat
    Network -->|WebSocket| Server
    Server -->|Relay Public\nRoute Private\nUser List| Network
    Server -->|Persist users/messages| Database
```

## Public Message Sending Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant GUI as GUI (MainWindow)
    participant Disp as EventDispatcher
    participant Net as WebSocketClient
    participant Server as Server
    participant Others as Other Clients

    Note over User,GUI: Public Message Flow
    User->>GUI: Types "Hello" and clicks "Send"
    GUI->>GUI: Validate: is input field empty?
    GUI->>GUI: Validate: is WebSocket connected?
    GUI->>GUI: Clear input field
    
    GUI->>Disp: dispatcher.notify(Event(SEND_MESSAGE, {...}))
    
    Note over Disp: EventDispatcher notifies all observers
    Disp->>Net: update(Event(SEND_MESSAGE, {...}))
    
    Net->>Net: asyncio: run_coroutine_threadsafe()
    Net->>Server: WebSocket.send({type: public_message, sender: Alice, text: Hello})
    Server->>Server: Receive message
    Server->>Database: save public message
    Server->>Others: Relay to all connected clients
    Server->>Net: Relay to this client too
    
    Net->>Disp: dispatcher.notify(Event(MESSAGE_RECEIVED, {...}))
    Disp->>GUI: update(Event(...))
    GUI->>GUI: Display "Hello" in chat history
```

## Private Message Sending & Receiving Sequence

```mermaid
sequenceDiagram
    participant Alice as Alice Client
    participant AliceUI as Alice UI
    participant AliceDisp as Dispatcher
    participant AliceNet as Alice WebSocket
    participant Server as Server
    participant BobNet as Bob WebSocket
    participant BobDisp as Dispatcher
    participant BobUI as Bob UI
    participant PrivChat as PrivateChatWindow

    Note over Alice,Bob: Private Message Flow - Alice to Bob

    Alice->>AliceUI: Clicks on "Bob" in Users Panel
    AliceUI->>AliceDisp: notify(OPEN_PRIVATE_CHAT, {username: Bob})
    AliceDisp->>PrivChat: update(Event) -> opens window
    
    Alice->>AliceUI: Types "Secret" in private chat window
    AliceUI->>AliceDisp: notify(PRIVATE_MESSAGE_SENT, {sender: Alice, recipient: Bob, text: Secret})
    AliceDisp->>AliceNet: update(Event) -> sends via network
    
    AliceNet->>Server: WebSocket.send({type: private_message, sender: Alice, recipient: Bob, text: Secret})
    Server->>Server: Lookup username_to_websocket["Bob"]
    Server->>Database: save private message
    Server->>BobNet: Send message ONLY to Bob
    Note over Server,BobNet: Message NOT relayed to other clients
    
    BobNet->>BobDisp: receive + notify(PRIVATE_MESSAGE_RECEIVED, {payload: {...}})
    BobDisp->>BobUI: update(Event) -> opens PrivateChatWindow(Alice)
    BobDisp->>PrivChat: update(Event) -> displays message in existing window
    
    PrivChat->>PrivChat: _append_message(Alice, Secret, timestamp, is_own=False)
```

## User List Update Flow

```mermaid
sequenceDiagram
    participant ClientA as Client A
    participant Server as Server
    participant ClientB as Client B
    participant Users as UsersPanel

    Note over ClientA,Users: User Connection/Disconnection Flow
    ClientA->>Server: WebSocket connect + auth message
    Server->>Server: Add username to client_usernames and username_to_websocket
    Server->>Server: Broadcast join message to all clients
    Server->>Server: Broadcast user_list message with updated users
    Server->>ClientA: user_list: ["Alice", "Bob"]
    Server->>ClientB: user_list: ["Alice", "Bob"]
    
    ClientB->>Users: WebSocketClient receives user_list
    ClientB->>Users: Event(USER_LIST_UPDATED, {"users": ["Alice", "Bob"]})
    Users->>Users: Update displayed user list with click handlers
    
    ClientA->>Server: WebSocket disconnect
    Server->>Server: Remove from client_usernames and username_to_websocket
    Server->>Server: Broadcast leave message to all clients
    Server->>Server: Broadcast updated user_list
    Server->>ClientB: user_list: ["Bob"]
    ClientB->>Users: Update displayed user list
```

## Event Flow Description

### Public Message (Existing)
1. **User Input**: User types and clicks Send in MainWindow
2. **UI Validation**: GUI validates input and connection state
3. **Event Creation**: GUI creates `Event(SEND_MESSAGE, {text, username})`
4. **Dispatcher Notification**: `dispatcher.notify(event)` called
5. **Routing**: All observers notified (Network, State, UI)
6. **Network Processing**: WebSocketClient formats and sends structured `{type: public_message, sender, text}`
7. **Server Broadcast**: Message relayed to all connected clients
8. **Message Received**: WebSocketClient fires `Event(MESSAGE_RECEIVED, {message})`
9. **UI Display**: MainWindow receives message event and updates chat history

### Private Message (New)
1. **User Selection**: User clicks on username in UsersPanel
2. **Dispatcher Event**: UsersPanel emits `Event(OPEN_PRIVATE_CHAT, {username})`
3. **Window Mgmt**: MainWindow.private_chat_manager.open_chat() creates/focuses window
4. **Private Window**: PrivateChatWindow opens independently with peer username
5. **User Sends**: User types message and clicks Send in PrivateChatWindow
6. **Dispatcher Event**: PrivateChatWindow emits `Event(PRIVATE_MESSAGE_SENT, {sender, recipient, text})`
7. **Controller Processing**: Controller validates and formats structured payload
8. **Network Send**: WebSocketClient sends `{type: private_message, sender, recipient, text}` to server
9. **Server Routing**: Server looks up recipient in `username_to_websocket` and sends ONLY to that connection
10. **Recipient Receive**: WebSocketClient fires `Event(PRIVATE_MESSAGE_RECEIVED, {payload})`
11. **Auto-Window Open**: MainWindow opens PrivateChatWindow if not already open
12. **Display**: PrivateChatWindow receives event and displays message with sender name

## Key Improvements Over Queue-Based System

| Aspect | Old (Queues) | New (Observer Pattern) |
|--------|-------------|----------------------|
| Coupling | High (direct queue refs) | Low (event-based) |
| Scalability | Limited (4 fixed queues) | High (add observers dynamically) |
| Private Messaging | Not supported | Fully supported with window mgmt |
| Thread Safety | Manual queue thread-safety | Built-in dispatcher locks |
| Debugging | Multiple queues to trace | Single dispatcher logs events |
| Extensibility | Requires new queues | Just add new Observer |
| Code Clarity | Queue management scattered | Clear event types and handlers |

## Message Model: Structured vs Raw Text

**Old Format** (Legacy):
```
"[13:45:21] Alice: Hello World"
```

**New Format** (Structured JSON):
```json
{
  "type": "public_message|private_message",
  "sender": "Alice",
  "recipient": "Bob",  // empty for public messages
  "text": "Hello World",
  "timestamp": "2026-05-31T13:45:21.123456"
}
```

Advantages:
- **Type distinction**: Server can route private messages to single recipient
- **Metadata extraction**: Recipient name parsed reliably from payload
- **Forward compatibility**: New fields can be added without breaking parsing
- **Server-side routing**: Server decision logic based on message type, not heuristics

## Server Username Mapping

```python
client_usernames: dict[WebSocket, str]
    # Maps: WebSocket object -> Username string
    # Use: Track username for disconnection cleanup

username_to_websocket: dict[str, WebSocket]
    # Maps: Username string -> WebSocket object
    # Use: Lookup socket when routing private messages
```

Both kept in sync on authentication and disconnection.

## Private Chat Window Manager

```python
class PrivateChatWindowManager:
    windows: dict[str, PrivateChatWindow]
        # Key: peer username
        # Value: PrivateChatWindow instance
    
    def open_chat(username) -> PrivateChatWindow:
        # If window exists: focus existing window (no duplicate)
        # If window doesn't exist: create new window and store
```

## Event Types Reference

See [core/events/README.md](../../core/events/README.md) for complete event type documentation.

New events added:
- `OPEN_PRIVATE_CHAT`: User selected from UsersPanel
- `PRIVATE_CHAT_OPENED`: Window manager opened private chat
- `PRIVATE_MESSAGE_SENT`: User sent private message
- `PRIVATE_MESSAGE_RECEIVED`: Server routed private message to client
