import asyncio

import pytchat

from .models import ChatMessage


class YouTubeChatClient:
    def __init__(self, video_id: str):
        if "youtube.com/watch?v=" in video_id:
            self.video_id = video_id.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_id:
            self.video_id = video_id.split("youtu.be/")[1].split("?")[0]
        else:
            self.video_id = video_id
        self.chat = None
        self.running = False

    async def connect(self):
        if not self.video_id:
            print("Error: YOUTUBE_VIDEO_ID not set.")
            return
        self.chat = pytchat.create(video_id=self.video_id)
        self.running = True
        print(f"Connected to YouTube chat for video {self.video_id}")

    async def messages(self):
        while self.running and self.chat and self.chat.is_alive():
            for c in self.chat.get().sync_items():
                
                # Rebuild text with actual emojis
                text = ""
                if hasattr(c, 'messageEx'):
                    for chunk in c.messageEx:
                        if isinstance(chunk, str):
                            text += chunk
                        elif isinstance(chunk, dict):
                            em_id = chunk.get('id', '')
                            if len(em_id) < 15:
                                text += em_id
                            else:
                                text += chunk.get('txt', '')
                else:
                    text = c.message

                msg = ChatMessage(
                    message_id=c.id,
                    user_id=c.author.channelId,
                    username=c.author.name,
                    text=text
                )
                yield msg
            await asyncio.sleep(1)
