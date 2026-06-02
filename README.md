# P2P Messenger

A centralized messaging application with a WebSocket relay server and a modular Python client GUI.

## Project Overview

P2P Messenger is a centralized chat system that uses a server relay architecture. The server accepts WebSocket connections from clients, forwards messages to connected peers, and persists user and message metadata in a local database. The client is built with a modular event-driven UI and supports public and private messaging.

## Features

- WebSocket relay server with configurable host and port
- Event-driven client architecture using an observer pattern
- CustomTkinter-based GUI for connection management and chat input
- Public broadcast messaging and private message routing
- SQLite-backed database layer for user and message persistence
- Modular project layout with separate core, network, UI, config, database, and docs layers

## Architecture

P2P Messenger is organized as a layered application:

- `server.py` — central relay server using `websockets` and `asyncio`
- `app.py` — client entrypoint that composes core, network, and UI modules
- `core/` — application state, controller logic, and event dispatching
- `network/` — client-side WebSocket networking and event handling
- `ui/` — main window, components, and user interaction logic
- `database/` — SQLite database initialization and persistence
- `config/` — theming and configuration assets

The server accepts incoming client connections, processes authentication and message payloads, and relays messages to the proper recipients while keeping the relay stateless.

## Technologies

- Python 3.12
- asyncio for asynchronous networking and server operation
- websockets for WebSocket communication
- CustomTkinter / Tkinter for the desktop client GUI
- SQLite via Python standard library for lightweight persistence
- JSON for client-server payloads and configuration

## Running the Server

Start the relay server from the repository root:

```bash
python server.py --host 0.0.0.0 --port 8765
```

- `--host` defaults to `0.0.0.0`
- `--port` defaults to `8765`

The server initializes the database on startup and begins accepting WebSocket connections.

## Running the Client

Launch the client from the repository root:

```bash
python app.py
```

The client opens the main window and connects to a running server using the configured IP and port.

## Database Layer

The `database/` package contains the persistence layer used by `server.py`:

- `database/__init__.py`
- `database/database.py`
- `database/schema.py`

The database layer initializes the schema, stores user records, and saves messages. It is used for persistence and does not alter the real-time relay behavior of the server.

## Project Structure

```text
P2P-Messenger/
├── AGENTS.md
├── README.md
├── app.py
├── config/
│   └── theme_config.json
├── core/
│   ├── __init__.py
│   ├── controller.py
│   ├── events/
│   ├── message_model.py
│   └── state.py
├── database/
│   ├── __init__.py
│   ├── database.py
│   ├── schema.py
│   └── README.md
├── docs/
│   ├── architecture/
│   ├── plans/
│   └── requirements/
├── Experiment/
│   └── Experiment.md
├── network/
│   ├── __init__.py
│   ├── event_loop.py
│   └── websocket_client.py
├── requirements.txt
├── server.py
├── tests/
└── ui/
    ├── __init__.py
    ├── components/
    ├── components_old.py
    ├── main_window.py
    ├── private_chat_window.py
    └── theme/
```

> Note: Development artifacts such as `.venv`, `venv`, `.vscode`, and `__pycache__` are intentionally excluded from this structure listing.

## Documentation

The repository includes documentation and planning assets in the `docs/` folder:

- `docs/architecture/` — architecture diagrams and flow documentation
- `docs/plans/` — roadmap and future planning
- `docs/requirements/` — functional requirements and design notes

## Future Improvements

- Add user authentication and encrypted transport for stronger security
- Improve client UI with persistent chat history and message timestamps
- Add multi-room or channel support for group conversations
- Extend automated tests to cover database operations and UI workflows
- Add server health monitoring and better error reporting
