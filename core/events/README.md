# Event System Documentation

## Overview

The `core/events/` module implements the **Observer pattern** for event-driven communication in the P2P Messenger application. This pattern replaces the previous queue-based communication system, providing better decoupling between UI, network, and core business logic layers.

## Why Observer Pattern?

### Benefits

1. **Loose Coupling**: Components don't need direct references to each other. They simply observe events they care about.
2. **Scalability**: New observers can be added without modifying the dispatcher or other observers.
3. **Thread-Safety**: The EventDispatcher uses locks to ensure safe multi-threaded event dispatch.
4. **Clarity**: Event flow is explicit and easy to follow compared to multiple inter-component queues.
5. **Testability**: Components can be tested in isolation by mocking events.

### Architecture Before

```
UI ←→ Controller ←→ Network
     (via 4 queues)
```

Multiple queue management created coupling and complexity.

### Architecture After

```
         EventDispatcher
        /      |      \
       UI      Core    Network
   (Observer) (Observer) (Observer)
```

All components attach to a central dispatcher and respond to events.

## Event Types

Events are defined in `events.py` as constants and use a unified `Event` dataclass:

```python
@dataclass
class Event:
    type: str                  # Event type constant
    data: dict[str, Any]       # Event payload
    timestamp: float           # Unix timestamp
```

### Event Constants

| Event Type | Source | Consumers | Description |
|-----------|--------|-----------|-------------|
| `MESSAGE_RECEIVED` | Network | UI, Core | A message arrived from WebSocket |
| `CONNECTION_CHANGED` | Network | UI, Core | Connection state changed (connected/disconnected) |
| `USER_JOINED` | Network | UI | A user joined the chat |
| `USER_LEFT` | Network | UI | A user left the chat |
| `ERROR_OCCURRED` | Network, Core | UI | An error occurred |
| `SEND_MESSAGE` | UI | Network | User sent a message via UI |
| `CONNECT_REQUEST` | UI | Network | User requested connection |
| `DISCONNECT_REQUEST` | UI | Network | User requested disconnection |
| `STATUS_CHANGED` | Core | UI | Application status changed |
| `CLEAR_CHAT` | UI | Core | User cleared chat history |
| `UI_UPDATE` | Core | UI | General UI update request |

## Module Structure

- **`events.py`**: Defines `Event` dataclass and event type constants
- **`observer.py`**: Abstract `Observer` base class with `update()` method
- **`dispatcher.py`**: Thread-safe `EventDispatcher` (Subject) for managing observers

## Usage Example

```python
from core.events import EventDispatcher, Event, Observer, MESSAGE_RECEIVED

# Define an observer
class MyComponent(Observer):
    def update(self, event: Event) -> None:
        if event.type == MESSAGE_RECEIVED:
            message = event.data.get("message")
            print(f"Received: {message}")

# Create dispatcher and attach observer
dispatcher = EventDispatcher()
component = MyComponent()
dispatcher.attach(component)

# Fire an event
event = Event(
    type=MESSAGE_RECEIVED,
    data={"message": "Hello, World!"}
)
dispatcher.notify(event)
```

## Thread-Safety

The `EventDispatcher` uses `threading.Lock` to ensure:
- Safe observer registration/deregistration from multiple threads
- Safe event dispatch without race conditions
- Observers list is copied before iteration to prevent issues if observers are modified during dispatch

## Integration

The event system integrates with:
1. **core/state.py**: `AppState` observes events and updates application state
2. **network/websocket_client.py**: Fires network-related events
3. **ui/main_window.py**: `MainWindow` observes events and updates GUI
4. **core/controller.py**: Routes events between network and UI (transitional)
5. **app.py**: Creates and wires the dispatcher to all components

## Future Evolution

The event system provides a foundation for:
- Event filtering and priority handling
- Event replay for debugging
- Persistent event logging
- Advanced error handling and recovery
