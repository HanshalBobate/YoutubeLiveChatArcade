import pytchat

chat = pytchat.create(video_id="m_xljeM72zQ")
for c in chat.get().sync_items():
    if hasattr(c, 'messageEx'):
        res = []
        for item in c.messageEx:
            if isinstance(item, str):
                res.append(item)
            elif isinstance(item, dict):
                # Is it a dict?
                pass
            else:
                if hasattr(item, 'txt'):
                    res.append(item.txt)
        
        try:
            with open("scratch/test.txt", "a", encoding="utf-8") as f:
                f.write(f"messageEx type: {[type(x) for x in c.messageEx]}\n")
                if len(c.messageEx) > 0 and type(c.messageEx[0]) != str:
                    f.write(f"Attributes: {dir(c.messageEx[0])}\n")
        except Exception:
            pass
        break
