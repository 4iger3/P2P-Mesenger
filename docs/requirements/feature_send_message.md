# Feature: Send a Chat Message

## User Story
As a client user, I want to send a text message to the server so that other connected users can see it in real time.

## Acceptance Criteria

### AC-1: Successful Message Sending
**Given** the client is connected to the server via WebSocket  
**When** the user enters the text "Hello" in the input field and clicks the "Send" button  
**Then** the text is transmitted to the server, the input field is cleared, and the chat history is NOT updated (the message will appear in the history only after being received back from the server)

### AC-2: Sending Without Connection
**Given** the client is NOT connected to the server  
**When** the user enters text and clicks "Send"  
**Then** the message is NOT sent, and the status bar displays "Not connected to server"

### AC-3: Empty Message
**Given** the client is connected to the server  
**When** the input field is empty and the user clicks "Send"  
**Then** nothing happens, and no message is sent to the server

### AC-4: Send Message by Pressing Enter
**Given** the client is connected to the server  
**When** the user enters text and presses the Enter key  
**Then** the message is sent in the same way as clicking the "Send" button