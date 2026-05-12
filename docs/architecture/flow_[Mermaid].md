# Architecture: Message Sending Flow

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

    User -->|Types & Sends| GUI
    GUI -->|SEND_MESSAGE\nCONNECT_REQUEST| Dispatcher
    Dispatcher -->|Notify| UI
    Dispatcher -->|Notify| State
    Dispatcher -->|Notify| Network
    Network -->|MESSAGE_RECEIVED\nCONNECTION_CHANGED| Dispatcher
    Dispatcher -->|Update| UI
    Dispatcher -->|Update| State
    Network -->|WebSocket| Server
    Server -->|Relay| Network
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User as User
    participant GUI as GUI (MainWindow)
    participant Disp as EventDispatcher
    participant Net as WebSocketClient
    participant Server as Server
    participant Others as Other Clients

    Note over User,GUI: AC-1: Successful Message Sending (Observer Pattern)
    User->>GUI: Types "Hello" and clicks "Send"
    GUI->>GUI: Validate: is input field empty?
    GUI->>GUI: Validate: is WebSocket connected?
    GUI->>GUI: Clear input field
    
    GUI->>Disp: dispatcher.notify(Event(SEND_MESSAGE, {...}))
    
    Note over Disp: EventDispatcher notifies all observers
    Disp->>Net: update(Event(SEND_MESSAGE, {...}))
    Disp->>User: UI remains responsive
    
    Net->>Net: asyncio: run_coroutine_threadsafe()
    Net->>Server: WebSocket.send("Hello")
    Server->>Server: Receive message
    Server->>Others: Relay to all connected clients
    Server->>Net: Relay to this client too
    
    Net->>Disp: dispatcher.notify(Event(MESSAGE_RECEIVED, {...}))
    Disp->>GUI: update(Event(...))
    GUI->>GUI: Display "Hello" in chat history

    Note over User,GUI: AC-2: Sending Without Connection
    User->>GUI: Types text and clicks "Send"
    GUI->>GUI: Validate: is WebSocket connected?
    GUI->>Disp: dispatcher.notify(Event(SEND_MESSAGE, {...}))
    Note over Net,Disp: Update method checks connection state
    Net->>GUI: (ignored if not connected)
    GUI-->>User: Status bar: "Not connected to server"

    Note over User,GUI: AC-3: Empty Message
    User->>GUI: Clicks "Send" with empty input field
    GUI->>GUI: Validate: is input field empty?
    GUI-->>User: Nothing happens (event not dispatched)
```

## Event Flow Description

The diagram visualizes the Observer pattern implementation with three acceptance criteria:

### AC-1 (Success): Full Message Path with Event Dispatcher
1. **User Input**: User types "Hello" and clicks Send
2. **UI Validation**: GUI validates input and connection state
3. **Event Creation**: GUI creates `Event(SEND_MESSAGE, {...})`
4. **Dispatcher Notification**: `dispatcher.notify(event)` called
5. **Observer Updates**: All attached observers (Network, State, UI) receive `update(event)` calls
6. **Network Processing**: WebSocketClient processes SEND_MESSAGE event asynchronously
7. **Server Relay**: Message sent via WebSocket to server
8. **Server Broadcast**: Server relays to all connected clients
9. **Message Received**: WebSocketClient fires `Event(MESSAGE_RECEIVED, {...})`
10. **UI Display**: GUI receives message event and updates chat history

### AC-2 (No Connection): Event Dispatch Without Active Connection
- GUI validates connection before sending event
- Alternatively, Network observer ignores SEND_MESSAGE if not connected
- Error event dispatched via dispatcher to inform user

### AC-3 (Empty Input): Event Not Dispatched for Invalid Input
- GUI validates input (non-empty) before creating event
- No event is dispatched if validation fails
- No processing overhead on network or state layers

## Key Improvements Over Queue-Based System

| Aspect | Old (Queues) | New (Observer Pattern) |
|--------|-------------|----------------------|
| Coupling | High (direct queue refs) | Low (event-based) |
| Scalability | Limited (4 fixed queues) | High (add observers dynamically) |
| Thread Safety | Manual queue thread-safety | Built-in dispatcher locks |
| Debugging | Multiple queues to trace | Single dispatcher logs events |
| Extensibility | Requires new queues | Just add new Observer |
| Code Clarity | Queue management scattered | Clear event types and handlers |

## Event Types Reference

See [core/events/README.md](../../core/events/README.md) for complete event type documentation.
