import asyncio

from app.chat.models import ChatMessage


class CommandQueue:
    def __init__(self):
        self.queue: asyncio.Queue[ChatMessage] = asyncio.Queue()
        
    async def add(self, message: ChatMessage):
        await self.queue.put(message)

    def get_messages(self) -> list[ChatMessage]:
        messages = []
        while not self.queue.empty():
            messages.append(self.queue.get_nowait())
        return messages
