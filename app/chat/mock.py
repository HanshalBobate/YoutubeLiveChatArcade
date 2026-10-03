import asyncio
import sys
import uuid

from .models import ChatMessage


class MockChatClient:
    def __init__(self):
        self.running = False
        self.message_queue = asyncio.Queue()

    async def connect(self):
        self.running = True
        asyncio.create_task(self._read_input())
        print("Mock chat connected. Type your messages (e.g., '!game sokoban').")

    async def _read_input(self):
        loop = asyncio.get_event_loop()
        while self.running:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            line = line.strip()
            if line:
                user_id = "mock_user_1"
                username = "MockUser"
                if line.startswith("@"):
                    parts = line.split(" ", 1)
                    if len(parts) > 1:
                        username = parts[0][1:]
                        user_id = f"mock_{username}"
                        line = parts[1]

                msg = ChatMessage(
                    message_id=str(uuid.uuid4()),
                    user_id=user_id,
                    username=username,
                    text=line
                )
                await self.message_queue.put(msg)

    async def messages(self):
        while self.running:
            msg = await self.message_queue.get()
            yield msg
