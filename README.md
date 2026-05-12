# P2P Messenger

*Centralized relay architecture for instant messaging*

## Architecture

This project implements a messaging system where:

1. A server runs on a designated PC and accepts WebSocket connections
2. Clients connect to the server using a known IP address and port
3. The server relays each incoming message to all connected clients

## Technologies

- Python 3.10+ with asyncio
- WebSockets for bidirectional communication
- Tkinter for graphical user interface

## Project Structure

P2P-Messenger/
├── app.py
├── server.py
├── README.md
├── AGENTS.md
│
├── core/
│   ├── __init__.py
│   ├── state.py
│   └── message_model.py
│   │
│   └── events/
│       ├── __init__.py
│       ├── dispatcher.py
│       ├── observer.py
│       ├── events.py
│       └── README.md
│
├── network/
│   ├── __init__.py
│   ├── event_loop.py
│   └── websocket_client.py
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   └── components.py
│
├── docs/
│   ├── architecture/
│   │   └── flow_[Mermaid].md
│   │
│   ├── plans/
│   │   └── roadmap.md
│   │
│   └── requirements/
│       ├── feature_send_message.md
│       └── pm_approach.md
│
├── Experiment/
│   └── Experiment.md
│
├── tests/
│   ├── test_client_send.py
│   └── test_message_delivery.py
│
└── __pycache__/

## Architecture Overview

The application follows a layered architecture:

- core/ — domain state and models
- network/ — async communication layer (WebSocket)
- ui/ — presentation layer (Tkinter)
- app.py — composition root (wires all layers together)

## Design Patterns

The project uses the Observer Design Pattern to implement
an event-driven communication system between the UI,
network, and controller layers.

The event dispatcher reduces direct coupling between modules
and improves scalability and maintainability.

## Usage


### Server
```
python server.py --host 0.0.0.0 --port 8765
```

### Client
```
python app.py
```
