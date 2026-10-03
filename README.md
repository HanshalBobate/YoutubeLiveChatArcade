# YouTube Live Chat Arcade

YouTube Live Chat Arcade is an interactive streaming engine that allows your YouTube audience to collectively play classic arcade games directly through YouTube Live Chat!

## Features

The arcade features a 1-second action window that throttles input and processes the first valid command received, providing a chaotic but highly playable group experience. The games run in a rigid 15x43 character grid designed perfectly for OBS overlay integration!

### Available Games

- **Tic-Tac-Toe**: Classic 1v1 battle. Players type `!ttt join` to play. The engine clearly displays `X: @user | O: @user` underneath the board. The winner gets a 3-second victory freeze on screen before the system automatically declares the victor in the global chat.
- **Tetris**: Endlessly falling blocks in a wide 14x15 board. Every 10 seconds, the engine enforces a strict auto-drop to ensure the game never stalls. A live side-panel scoreboard tracks exactly which user made the last successful move (`By: @username`).
- **Sokoban**: A puzzle game where the chat works together to push crates onto goals. Uses a completely procedural level generator that limits map density to 2% obstacles and strictly 1 to 3 crates to keep it engaging. Features a minimalist UI that highlights the last player's username.

## Architecture

The project is built entirely in Python using `asyncio` to simultaneously read the YouTube chat API and tick the game engine. 

- `app/core/engine.py`: Manages the event loop, chat queue, and action-window rules.
- `app/core/manager.py`: Connects chat commands to the active game and dynamically handles screen rendering, voting mechanisms, and global commands like `!game quit`.
- `app/output/obs.py`: Pushes the 15x43 ASCII-rendered frame buffer instantly to an OBS Text source via OBS WebSocket!

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   Create a `.env` file in the root directory:
   ```env
   YOUTUBE_VIDEO_ID=your_video_id
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_websocket_password
   OBS_TEXT_SOURCE=ArcadeText
   MOCK_MODE=True
   ```
   > Note: To test the app locally in your terminal without connecting to a live stream, keep `MOCK_MODE=True`.

3. **Running the Arcade**
   Start the engine:
   ```bash
   python -m app.main
   ```
   
   If `MOCK_MODE=True`, the mock client will connect, and you can type commands directly into standard input (e.g., `!game tetris`) to test the flow!

## Web Interface

The arcade is paired with a beautiful HTML guide located at `index.html`. This page can be hosted on GitHub Pages or any static host to explain the game rules, limits, and chat commands to your audience!
