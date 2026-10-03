import pytchat

chat = pytchat.create(video_id="m_xljeM72zQ")
for c in chat.get().sync_items():
    if ":" in c.message:
        print(f"message: {c.message}")
        if hasattr(c, 'messageEx'):
            print(f"messageEx: {c.messageEx}")
        break
