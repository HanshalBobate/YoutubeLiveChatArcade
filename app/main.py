import asyncio
import os

from app.config import config
from app.core.engine import Engine
from app.output.obs import OBSOutput


async def main():
    engine = Engine()
    obs_out = OBSOutput(
        host=config.OBS_HOST,
        port=config.OBS_PORT,
        password=config.OBS_PASSWORD,
        source_name=config.OBS_TEXT_SOURCE
    )
    
    # We monkey patch engine to also send to OBS
    original_game_loop = engine._game_loop
    
    async def hooked_game_loop():
        await original_game_loop()
        if hasattr(engine, 'last_text'):
            await obs_out.update_text(engine.last_text)
            
    engine._game_loop = hooked_game_loop
    await engine.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down Arcade...")
        try:
            from app.output.obs import OBSOutput
            from app.config import config
            obs_out = OBSOutput(
                host=config.OBS_HOST,
                port=config.OBS_PORT,
                password=config.OBS_PASSWORD,
                source_name=config.OBS_TEXT_SOURCE
            )
            obs_out.update_text_sync("Youtube Arcade Offline . . .")
        except Exception:
            pass
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        os._exit(0)
