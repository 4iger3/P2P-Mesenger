# Feature: Send a Chat Message

## User Story
As a client user, I want to send a chat message from the GUI so that the server relays it to other connected clients in real time.

## Functional Requirements
- The UI must provide a text input field and a "Send" button.
- When a user enters non-empty text and clicks "Send":
  - the client validates that a WebSocket connection is active,
  - the client formats the message as structured JSON using `MessageModel`,
  - the message is sent through the network layer to the server.
- The client must not update the local chat history until the server broadcasts the message back.
- If the client is not connected, sending is blocked and an error event is emitted.
- Empty message input must be ignored and must not be transmitted.
- The UI must not perform network operations directly; network messaging must go through the controller and `WebSocketClient`.

## Non-functional Requirements
- The UI thread must remain responsive during send and receive activity.
- WebSocket send operations must execute on a background thread with an `asyncio` event loop.
- The application must not block the main UI while waiting for network responses.
- Message delivery latency should be minimized by sending immediately after validation and relying on the server relay.
- Error conditions such as invalid connection state or send failure must be reported through event-driven error handling.

## Message Flow
1. User types text in the GUI input field.
2. User clicks the "Send" button.
3. The UI emits a send request event to the dispatcher.
4. The controller validates the message and connection state.
5. The controller builds a structured `MessageModel` payload and forwards it to the WebSocket client.
6. The WebSocket client sends the payload to the server over the WebSocket connection.
7. The server relays the message to all connected clients.
8. The client receives the broadcasted message and updates the chat history display.

## Architecture Constraints
- The UI layer must not access the database directly.
- The send path must remain decoupled: UI → controller → network layer → server → UI.
- The network layer must operate asynchronously and independently from the main UI thread.