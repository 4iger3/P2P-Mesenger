from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MessageModel:
    text: str
    timestamp: datetime = field(default_factory=datetime.now)

    def formatted(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.text}"
