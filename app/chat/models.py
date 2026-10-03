import time
from dataclasses import dataclass


@dataclass
class ChatMessage:
    message_id: str
    user_id: str
    username: str
    text: str
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
