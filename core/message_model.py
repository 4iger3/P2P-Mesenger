from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class MessageModel:
    """Structured message model for public and private messages."""

    type: str = "public_message"
    sender: str = ""
    recipient: str = ""
    text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    raw: str = ""

    @classmethod
    def from_payload(cls, payload: Any) -> "MessageModel":
        """Create a MessageModel from raw text or JSON payload."""
        if isinstance(payload, dict):
            message_type = str(payload.get("type", "public_message"))
            sender = str(payload.get("sender", "") or "").strip()
            recipient = str(payload.get("recipient", "") or "").strip()
            text = str(payload.get("text", "") or "")
            timestamp_raw = payload.get("timestamp")
            timestamp = cls._parse_timestamp(timestamp_raw)
            return cls(type=message_type, sender=sender, recipient=recipient, text=text, timestamp=timestamp)

        if isinstance(payload, str):
            payload = payload.strip()
            if not payload:
                return cls()

            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                return cls.from_string(payload)

            if isinstance(data, dict):
                return cls.from_payload(data)

        return cls()

    @classmethod
    def from_string(cls, raw_text: str) -> "MessageModel":
        """Parse legacy raw text payload into a MessageModel."""
        raw_text = raw_text.strip()
        sender = ""
        text = raw_text
        if ": " in raw_text:
            sender_part, text_part = raw_text.split(": ", 1)
            sender = sender_part.strip()
            text = text_part.strip()

        return cls(type="public_message", sender=sender, text=text, raw=raw_text)

    @staticmethod
    def _parse_timestamp(timestamp_raw: Any) -> datetime:
        """Parse timestamp field into a datetime object or default now."""
        if isinstance(timestamp_raw, str):
            try:
                return datetime.fromisoformat(timestamp_raw)
            except ValueError:
                pass
        return datetime.now()

    def formatted(self) -> str:
        """Return a readable formatted message string for display."""
        if self.type == "private_message":
            return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender}: {self.text}"
        if self.sender:
            return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender}: {self.text}"
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.text}"

    def to_json(self) -> str:
        """Serialize the structured message to JSON string."""
        payload = {
            "type": self.type,
            "sender": self.sender,
            "recipient": self.recipient,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
        }
        return json.dumps(payload)
