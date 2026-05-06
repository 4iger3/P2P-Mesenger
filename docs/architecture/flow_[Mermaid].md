# Architecture: Message Sending Flow

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant GUI as Tkinter GUI
    participant NetThread as Network Thread (asyncio)
    participant Server as WebSocket Server
    participant Other as Other Clients

    Note over User,GUI: AC-1: Successful Message Sending
    User->>GUI: Types "Hello" and clicks "Send"
    GUI->>GUI: Validate: is input field empty?
    GUI->>GUI: Validate: is WebSocket connected?
    GUI->>GUI: Clear input field
    GUI->>NetThread: Pass "Hello" to asyncio queue
    NetThread->>Server: WebSocket.send("Hello")
    Server->>Server: Receive message
    Server->>Other: Relay to all connected clients
    Server->>NetThread: Relay to all connected clients
    NetThread->>GUI: Put message into incoming queue
    GUI->>GUI: Display "Hello" in chat history

    Note over User,GUI: AC-2: Sending Without Connection
    User->>GUI: Types text and clicks "Send"
    GUI->>GUI: Validate: is WebSocket connected?
    GUI-->>User: Status bar: "Not connected to server"

    Note over User,GUI: AC-3: Empty Message
    User->>GUI: Clicks "Send" with empty input field
    GUI->>GUI: Validate: is input field empty?
    GUI-->>User: Nothing happens
```

## Description
The diagram visualizes three acceptance criteria from `feature_send_message.md`:
1. **AC-1 (Success):** The full message path — user input → GUI validation → asyncio network thread → WebSocket → server relay → back to all clients' chat history.
2. **AC-2 (No Connection):** GUI checks WebSocket state and displays an error in the status bar if not connected.
3. **AC-3 (Empty Input):** GUI rejects an empty message before any network call occurs.