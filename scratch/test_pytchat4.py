import pytchat

chat = pytchat.create(video_id="m_xljeM72zQ")
for c in chat.get().sync_items():
    if hasattr(c, 'messageEx'):
        for item in c.messageEx:
            if not isinstance(item, str):
                try:
                    with open("scratch/test2.txt", "w", encoding="utf-8") as f:
                        if isinstance(item, dict):
                            f.write(f"DICT: {item}\n")
                        else:
                            f.write(f"OBJ dict: {item.__dict__}\n")
                            f.write(f"OBJ dir: {dir(item)}\n")
                except Exception:
                    pass
                exit(0)
