import pytchat

chat = pytchat.create(video_id="m_xljeM72zQ")
for i in range(1):
    for c in chat.get().sync_items():
        print(f"message: {c.message}")
        if hasattr(c, 'messageEx'):
            print(f"messageEx: {c.messageEx}")
        else:
            print("No messageEx")
        break
