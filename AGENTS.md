# Copilot Agent Rules — P2P Messenger

> ATTENTION AGENT: This file contains mandatory rules. Read before every session with this project.

## Project Identity

| Parameter | Value |
|-----------|-------|
| Project Name | P2P Messenger |
| Actual Architecture | Client-Server with centralized relay |
| Language | Python 3.10 |
| GUI Framework | Tkinter (built-in) |
| Protocol | WebSockets |

## PROHIBITED ACTIONS

- Do NOT implement WiFi Direct, Bluetooth P2P, mDNS, Zeroconf, or any automatic peer discovery
- Do NOT change the project name from "P2P Messenger"
- Do NOT generate code for decentralized P2P features such as NAT traversal, UDP hole punching, DHT, or STUN/TURN
- Do NOT delete or rename the COPILOT_RULES.md file
- Do NOT add external libraries without explicit permission beyond websockets and standard library
- Do NOT overcomplicate the architecture unnecessarily

## REQUIRED ACTIONS

- ALWAYS read this file before starting work on the project
- ALWAYS write comments and docstrings in Russian
- ALWAYS use asyncio for asynchronous server operations
- ALWAYS adhere to the architecture: one server, multiple clients, server relays all messages
- ALWAYS verify that generated code runs without errors before proposing changes
- ALWAYS use clear variable names and avoid abbreviations

-ALWAYS generate not more than 5000 lines of code per Persenal Request.

## Architectural Constraints

### Server (server.py)
- Must listen on host 0.0.0.0 and port 8765 (configurable via command line arguments)
- Must store active WebSocket connections in a set data structure
- Upon receiving a message from any client, relay it to all connected clients
- Must not store message history (stateless relay)
- Must handle client disconnections gracefully without crashing

### Client (client.py)
- Must provide a Tkinter GUI with the following elements:
  - Server IP address input field with option to save
  - Server port input field (default 8765)
  - Message input field
  - Chat history display (read-only)
  - Connect button
  - Send button
- Must run message receiving logic in a separate thread to avoid blocking the GUI
- Upon receiving a message from the server, append it to the chat history display

### Code Requirements
- Total lines of code should not exceed approximately 400 lines across server and client
- Minimal dependencies: websockets library only
- Code must be self-documenting with docstrings

## Project Structure

P2P-Messenger/
├── server.py
├── client.py
├── requirements.txt
├── README.md
└── COPILOT_RULES.md

## Agent Reminder

"I am building a centralized chat application using WebSockets. The project is named P2P Messenger but it is not true peer-to-peer. Clients communicate only through a central server. No WiFi Direct. No decentralized P2P."

## Agent Commands Reference

When the user writes:
- "fix client" — modify only client.py
- "add feature X" — verify the feature does not violate the rules above before implementing
- "review" — check the codebase for compliance with this rules file

---
Last updated: 11 апреля 2026 г.
This file serves as the instruction set for GitHub Copilot Agent.