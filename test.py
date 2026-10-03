import asyncio, traceback
from app.main import main
async def run():
 try: await main()
 except Exception: print(traceback.format_exc())
asyncio.run(run())