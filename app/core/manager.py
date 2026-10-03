
from app.chat.models import ChatMessage
from app.games.base import Game
from app.games.sokoban import Sokoban
from app.games.tetris import TetrisGame
from app.games.ttt import TicTacToeGame


class GameManager:
    def __init__(self):
        self.state = "MAIN_MENU"
        self.active_game: Game = None
        self.chat_history: list[ChatMessage] = []
        self.quit_votes = set()
        self.viewer_count = 100 # Mock viewer count for now, realistically this comes from YT API
        
    def get_current_frame(self) -> list[list[str]]:
        if self.state == "MAIN_MENU":
            return self._render_main_menu()
        elif self.active_game:
            frame = self.active_game.render()
            if self.quit_votes:
                req = self._get_required_quit_votes()
                votes = min(len(self.quit_votes), req)
                filled = int((votes / req) * 10) if req > 0 else 0
                bar = "█" * filled + "·" * (10 - filled)
                vote_str = f"QUIT:[{bar}] {votes}/{req}"
                if frame:
                    top_row = 0
                    width = len(frame[top_row])
                    offset = max(0, width - len(vote_str) - 1)
                    for i, c in enumerate(vote_str):
                        if offset + i < width:
                            frame[top_row][offset + i] = c
            return frame
        return [["E", "R", "R", "O", "R"]]

    def _render_main_menu(self) -> list[list[str]]:
        width = 43
        height = 15
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        # Border
        for i in range(width):
            grid[0][i] = "-"
            grid[height-1][i] = "-"
        for i in range(height):
            grid[i][0] = "|"
            grid[i][width-1] = "|"
        grid[0][0] = "+"
        grid[0][width-1] = "+"
        grid[height-1][0] = "+"
        grid[height-1][width-1] = "+"
        
        # Draw chat
        import textwrap
        chat_start_y = 1
        max_lines = height - 4
        
        wrapped_lines = []
        for msg in self.chat_history:
            username = msg.username[1:] if msg.username.startswith("@") else msg.username
            full_str = f"@{username}: {msg.text}"
            wrapped = textwrap.wrap(full_str, width - 4)
            wrapped_lines.extend(wrapped)
            
        lines_to_draw = wrapped_lines[-max_lines:] if wrapped_lines else []
        
        for i, row_str in enumerate(lines_to_draw):
            for j, c in enumerate(row_str):
                if 2 + j < width - 1:
                    grid[chat_start_y + i][2 + j] = c
                
        # Footer
        footer = "!game ttt / sokoban / tetris"
        f_start_x = (width - len(footer)) // 2
        for i, c in enumerate(footer):
            grid[height-2][f_start_x + i] = c
            
        return grid

    def _get_required_quit_votes(self) -> int:
        return (self.viewer_count + 2) // 2

    def process_messages(self, messages: list[ChatMessage]):
        for msg in messages:
            self.chat_history.append(msg)
            if len(self.chat_history) > 20:
                self.chat_history.pop(0)

            cmd = msg.text.lower().strip()
            
            # Global commands
            if cmd == "!game quit" and self.state != "MAIN_MENU":
                self.quit_votes.add(msg.user_id)
                if len(self.quit_votes) >= self._get_required_quit_votes():
                    self._end_game()
                continue
                
            if cmd.startswith("!game "):
                if self.state == "MAIN_MENU":
                    game_name = cmd.split(" ")[1]
                    self._start_game(game_name, msg)
                continue
                
        # We process game commands through a separate logic flow to enforce 5-second action window for Sokoban/Tetris
        # Wait, the prompt says for Sokoban: 
        # "At the beginning of a turn/window: ... Find the earliest message that begins with ! ... Execute the first valid command. Reset timer."

    def _start_game(self, game_name: str, msg):
        if game_name == "sokoban":
            self.active_game = Sokoban()
            self.state = "SOKOBAN"
        elif game_name == "ttt":
            self.active_game = TicTacToeGame()
            self.active_game.handle_command("!ttt join", msg.user_id, msg.username)
            self.state = "TTT"
        elif game_name == "tetris":
            self.active_game = TetrisGame()
            self.state = "TETRIS"
        self.quit_votes.clear()

    def _end_game(self):
        self.active_game = None
        self.state = "MAIN_MENU"
        self.quit_votes.clear()
