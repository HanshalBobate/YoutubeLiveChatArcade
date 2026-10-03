import asyncio
import sys

if __name__ == "__main__":
    from app.main import main
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
