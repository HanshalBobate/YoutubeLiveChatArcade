import asyncio
import time

from app.chat.mock import MockChatClient
from app.chat.models import ChatMessage
from app.chat.youtube import YouTubeChatClient
from app.config import config
from app.core.manager import GameManager
from app.core.queue import CommandQueue
from app.core.renderer import render_to_string


class Engine:
    def __init__(self):
        self.manager = GameManager()
        self.queue = CommandQueue()
        if config.MOCK_MODE:
            self.chat_client = MockChatClient()
        else:
            self.chat_client = YouTubeChatClient(config.YOUTUBE_VIDEO_ID)
            
        self.last_action_time = time.time()
        self.action_window = 1.0 # seconds

    async def run(self):
        await self.chat_client.connect()
        asyncio.create_task(self._read_chat())
        
        while True:
            await self._game_loop()
            await asyncio.sleep(0.1)

    async def _read_chat(self):
        async for msg in self.chat_client.messages():
            await self.queue.add(msg)
            
    async def _game_loop(self):
        messages = self.queue.get_messages()
        
        # Give messages to manager for chat history and global commands
        self.manager.process_messages(messages)
        
        # If in a game, process game-specific commands with time window if applicable
        if self.manager.state != "MAIN_MENU" and self.manager.active_game:
            current_time = time.time()
            
            # Reset timer if we just transitioned into a game
            if not hasattr(self, 'last_state') or self.last_state == "MAIN_MENU":
                self.last_action_time = current_time
                
            if self.manager.state in ["SOKOBAN", "TETRIS"]:
                # Use 1-second action window rule
                if current_time - self.last_action_time >= self.action_window:
                    # Find first valid command
                    from app.games.base import CommandResult
                    valid_command_executed = False
                    for msg in self.manager.chat_history:
                        if msg.timestamp > self.last_action_time and msg.text.startswith("!"):
                            result = self.manager.active_game.handle_command(msg.text, msg.user_id, msg.username)
                            if result == CommandResult.EXECUTED:
                                valid_command_executed = True
                                break
                    
                    if valid_command_executed:
                        self.last_action_time = current_time
            elif self.manager.state == "TTT":
                # Tic-tac-toe doesn't need a strict 5s delay, it processes instantly
                from app.games.base import CommandResult
                for msg in messages:
                    if msg.text.startswith("!"):
                        result = self.manager.active_game.handle_command(msg.text, msg.user_id, msg.username)
                        if result == CommandResult.EXECUTED:
                            self.last_action_time = current_time
                        
            # Update game
            self.manager.active_game.update()
            
            # Check for end
            if self.manager.active_game.is_finished():
                if self.manager.state == "SOKOBAN":
                    if current_time - self.last_action_time >= self.action_window:
                        self.manager._end_game()
                        self.last_action_time = current_time
                elif self.manager.state == "TTT":
                    game = self.manager.active_game
                    if hasattr(game, 'players'):
                        p1_id = game.players.get("X")
                        p1 = game.usernames.get(p1_id, "Player 1") if p1_id else "Player 1"
                        p2_id = game.players.get("O")
                        p2 = game.usernames.get(p2_id, "Player 2") if p2_id else "Player 2"
                        
                        if game.winner == "DRAW":
                            sys_msg = f"TicTacToe finished in a draw! @{p1} vs @{p2}."
                        else:
                            winner_id = game.players.get(game.winner)
                            winner_name = game.usernames.get(winner_id, game.winner) if winner_id else game.winner
                            sys_msg = f"TicTacToe was finished, @{p1} vs @{p2}. The winner is @{winner_name}!"
                            
                        self.manager.chat_history.append(ChatMessage(
                            message_id="sys",
                            user_id="sys",
                            username="SYSTEM",
                            text=sys_msg,
                            timestamp=time.time()
                        ))
                    self.manager._end_game()
                    self.last_action_time = current_time
                else:
                    pass
                    
            if not self.manager.active_game.is_finished() and current_time - self.last_action_time >= 120.0:
                self.manager._end_game()
                self.last_action_time = current_time
                
        self.last_state = self.manager.state
        # Output frame
        frame = self.manager.get_current_frame()
        text = render_to_string(frame)
        
        # Output to console for mock mode debugging
        # In a real app we'd throttle console output, but for now print if changed
        force_redraw = bool(messages)
        if force_redraw or not hasattr(self, 'last_text') or self.last_text != text:
            print("\033[H\033[J", end="") # Clear screen
            print(text)
            self.last_text = text
