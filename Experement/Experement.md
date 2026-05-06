````markdown
# Experiment: Pure Function for Message Sending

**Date:** 2026-05-06
**Project:** P2P Messenger
**Feature:** Send a Chat Message

## 1. Prompt Provided to AI

AI Prompt — Pure Function Validation (Strict Version)

You are given a feature specification and a system interaction diagram.

Your task is to implement the core decision-making logic of this feature as a strict pure function.

Input: Feature Specification (BDD)

(Use the following requirements exactly as written)

[Вставляешь свой BDD без изменений]

Input: Architecture Diagram

(Use the following Mermaid diagram as behavioral reference)

[Вставляешь свой diagram]

Task

Implement a function that handles the "Send Message" event as a pure function.

CRITICAL CONSTRAINTS (must be strictly followed)

Your function MUST:

Be pure and stateless
Have ZERO side effects
No networking
No WebSocket usage
No threading
No I/O (print, file, etc.)
NOT mutate input arguments
Return all outcomes explicitly
Be deterministic
Functional Model

You MUST implement logic as:

(state, event) → (new_state, actions)
Required Function Signature
def handle_send_message(state: dict, event: dict) -> dict:
Data Contracts
State
{
    "connected": bool,
    "username": str,
    "chat_history": list[str]
}
Event
{
    "type": "send_message",
    "content": str,
    "trigger": "button" | "enter"
}
Output Format
{
    "new_state": {...},
    "actions": [...]
}
Actions Specification (MANDATORY)

Each action must be explicit and structured.

Allowed action types:

{"type": "send_to_server", "payload": {...}}
{"type": "show_error", "message": str}
{"type": "no_op"}
Behavioral Requirements (STRICT)

You MUST enforce ALL of the following:

1. Connection validation
If NOT connected → return error action
2. Empty message validation
If message is empty → return no_op
3. Trigger handling
Only allow "button" and "enter"
Any other trigger → no_op
4. Message formatting
If username exists → format message as:
username: content
5. NO chat history update
Do NOT modify chat_history when sending
Message appears only after server echo
6. No hidden logic
All decisions must be visible in returned actions
Additional Constraint (IMPORTANT)

You must follow an immutable approach:

Do NOT modify state directly
Always return a new new_state
Output Requirements
Return ONLY the function
No explanations
No comments
No extra text

## 2. Result: Did the AI succeed on the first try?

YES

### AI-generated code:
```python
def handle_send_message(state: dict, event: dict) -> dict:
    """
    Handles the send message event in the chat.

    Args:
        state (dict): Current client state containing keys 'connected', 'username', 'chat_history'.
        event (dict): Send event containing keys 'type', 'content', 'trigger'.

    Returns:
        dict: New dictionary with keys 'new_state' and 'actions' describing state changes and actions.
    """
    trigger = event.get("trigger")
    if trigger not in ["button", "enter"]:
        return {"new_state": state.copy(), "actions": [{"type": "no_op"}]}
    connected = bool(state.get("connected"))
    if not connected:
        return {"new_state": state.copy(), "actions": [{"type": "show_error", "message": "Not connected to server"}]}
    content = event.get("content", "")
    if not isinstance(content, str) or content.strip() == "":
        return {"new_state": state.copy(), "actions": [{"type": "no_op"}]}
    username = state.get("username", "")
    payload = f"{username}: {content}" if username else content
    return {"new_state": state.copy(), "actions": [{"type": "send_to_server", "payload": payload}]}
```
````