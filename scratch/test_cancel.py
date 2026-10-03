import asyncio

async def test_obs():
    try:
        print("Running...")
        await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("Cancelled!")
        try:
            await asyncio.sleep(1)
            print("Finished final update!")
        except asyncio.CancelledError:
            print("Final update also cancelled!")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_obs())
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt")
