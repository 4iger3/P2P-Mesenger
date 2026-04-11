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
├── server.py
├── client.py
├── requirements.txt
├── README.md
└── COPILOT_RULES.md

## Usage

### Server
```
python server.py --host 0.0.0.0 --port 8765
```

### Client
```
python client.py
```
