# Architecture: Message Sending Flow & Private Direct Messages

## System Architecture Diagram

```mermaid
graph TB
    User["🧑 User"]
    GUI["Tkinter GUI"]
    Dispatcher["EventDispatcher\n(Subject)"]
    UI["MainWindow\n(Observer)"]
    State["AppState\n(Observer)"]
    Controller["Controller\n(Observer)"]
    Network["WebSocketClient\n(Observer)"]
    Server["🖥️ WebSocket Server"]
    Database["DatabaseManager\n(SQLite)"]
    Users["UsersPanel\n(Observer)"]
    PrivateChat["PrivateChatWindow\n(Observer)"]
    WindowManager["PrivateChatWindowManager\n(Window Manager)"]

    User -->|Types & Sends| GUI
    GUI -->|SEND_MESSAGE\nCONNECT_REQUEST\nOPEN_PRIVATE_CHAT| Dispatcher
    Dispatcher -->|Notify| UI
    Dispatcher -->|Notify| State
    Dispatcher -->|Notify| Controller
    Dispatcher -->|Notify| Network
    Dispatcher -->|Notify| Users
    Dispatcher -->|Notify| PrivateChat
    Dispatcher -->|Notify| WindowManager
    Controller -->|send_message| Network
    Network -->|MESSAGE_RECEIVED\nPRIVATE_MESSAGE_RECEIVED\nCONNECTION_CHANGED\nUSER_LIST_UPDATED| Dispatcher
    Dispatcher -->|Update| UI
    Dispatcher -->|Update| State
    Dispatcher -->|Update| Users
    Dispatcher -->|Update| PrivateChat
    Network -->|WebSocket| Server
    Server -->|Broadcast public/private/user_list| Network
    Server -->|Persist public/private messages| Database
```

## Public Message Sending Sequence

```mermaid
sequenceDiagram
    participant User as User
    participant GUI as GUI (MainWindow)
    participant Disp as EventDispatcher
    participant Ctrl as Controller
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
    Disp->>Ctrl: update(Event(SEND_MESSAGE, {...}))
    Note over Ctrl: Controller validates input and formats payload
    Ctrl->>Net: send_message({type: public_message, sender: Alice, text: Hello})
    
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
    participant AliceCtrl as Controller
    participant AliceNet as Alice WebSocket
    participant Server as Server
    participant BobNet as Bob WebSocket
    participant BobDisp as Dispatcher
    participant BobUI as Bob UI
    participant PrivChat as PrivateChatWindow
    participant WindowMgr as PrivateChatWindowManager

    Note over Alice,Bob: Private Message Flow - Alice to Bob

    Alice->>AliceUI: Clicks on "Bob" in Users Panel
    AliceUI->>AliceDisp: notify(OPEN_PRIVATE_CHAT, {username: Bob})
    AliceDisp->>AliceUI: update(Event) -> MainWindow opens or focuses private chat window
    AliceUI->>WindowMgr: open_chat(Bob)
    WindowMgr->>PrivChat: create or focus existing window
    
    Alice->>AliceUI: Types "Secret" in private chat window
    AliceUI->>AliceDisp: notify(PRIVATE_MESSAGE_SENT, {sender: Alice, recipient: Bob, text: Secret})
    AliceDisp->>AliceCtrl: update(Event(PRIVATE_MESSAGE_SENT, {...}))
    Note over AliceCtrl: Controller validates and formats private payload
    AliceCtrl->>AliceNet: send_message({type: private_message, sender: Alice, recipient: Bob, text: Secret})
    
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
    participant NetB as WebSocketClient
    participant DispB as EventDispatcher
    participant Users as UsersPanel

    Note over ClientA,Users: User Connection/Disconnection Flow
    ClientA->>Server: WebSocket connect + auth message
    Server->>Server: Add username to client_usernames and username_to_websocket
    Server->>Server: Broadcast join message to all clients
    Server->>Server: Broadcast user_list message with updated users
    Server->>ClientA: user_list: ["Alice", "Bob"]
    Server->>ClientB: user_list: ["Alice", "Bob"]
    
    ClientB->>NetB: WebSocketClient receives user_list JSON
    NetB->>DispB: dispatcher.notify(Event(USER_LIST_UPDATED, {"users": ["Alice", "Bob"]}))
    DispB->>Users: update(Event(USER_LIST_UPDATED, {...}))
    Users->>Users: Update displayed user list with click handlers
    
    ClientA->>Server: WebSocket disconnect
    Server->>Server: Remove from client_usernames and username_to_websocket
    Server->>Server: Broadcast leave message to all clients
    Server->>Server: Broadcast updated user_list
    Server->>ClientB: user_list: ["Bob"]
    ClientB->>NetB: WebSocketClient receives user_list JSON
    NetB->>DispB: dispatcher.notify(Event(USER_LIST_UPDATED, {"users": ["Bob"]}))
    DispB->>Users: update(Event(USER_LIST_UPDATED, {...}))
    Users->>Users: Update displayed user list
```

## Event Flow Description

### Public Message (Existing)
1. **User Input**: User types and clicks Send in MainWindow
2. **UI Validation**: GUI validates input and connection state
3. **Event Creation**: GUI creates `Event(SEND_MESSAGE, {text, username})`
4. **Dispatcher Notification**: `dispatcher.notify(event)` called
5. **Routing**: All observers notified (Controller, Network, State, UI)
6. **Controller Processing**: Controller validates the event and formats the outgoing payload
7. **Network Transport**: WebSocketClient sends the formatted JSON string to the server
8. **Server Broadcast**: Server persists the public message and relays it to all connected clients
9. **Message Received**: WebSocketClient receives the broadcast and dispatches `Event(MESSAGE_RECEIVED, {...})`
10. **UI Display**: MainWindow receives the event and updates chat history

### Private Message (New)
1. **User Selection**: User clicks on username in UsersPanel
2. **Dispatcher Event**: UsersPanel emits `Event(OPEN_PRIVATE_CHAT, {username})`
3. **Window Mgmt**: MainWindow.private_chat_manager.open_chat() creates or focuses a private chat window
4. **Private Window**: PrivateChatWindow opens independently with the peer username
5. **User Sends**: User types a message and clicks Send in PrivateChatWindow
6. **Dispatcher Event**: PrivateChatWindow emits `Event(PRIVATE_MESSAGE_SENT, {sender, recipient, text})`
7. **Controller Processing**: Controller validates and formats the structured private payload
8. **Network Transport**: WebSocketClient sends the payload to the server
9. **Server Routing**: Server looks up `username_to_websocket[recipient]` and forwards only to that recipient
10. **Recipient Receive**: Recipient WebSocketClient dispatches `Event(PRIVATE_MESSAGE_RECEIVED, {...})`
11. **Auto-Window Open**: MainWindow opens or focuses the sender's private chat window if needed
12. **Display**: PrivateChatWindow receives the event and appends the incoming message

## AppState Responsibilities

`AppState` only handles:
- `CONNECTION_CHANGED`
- `CLEAR_CHAT`
- `ERROR_OCCURRED`

It does not process message payloads or user list updates.

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

PrivateChatWindowManager prevents duplicate private chat windows by reusing existing windows for the same recipient.

## Event Types Reference

See [core/events/README.md](../../core/events/README.md) for complete event type documentation.

New events added:
- `OPEN_PRIVATE_CHAT`: User selected from UsersPanel
- `PRIVATE_CHAT_OPENED`: Window manager opened private chat
- `PRIVATE_MESSAGE_SENT`: User sent private message
- `PRIVATE_MESSAGE_RECEIVED`: Server routed private message to client
