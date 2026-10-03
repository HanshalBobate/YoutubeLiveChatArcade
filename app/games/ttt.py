from __future__ import annotations

from .base import CommandResult, Game


class TicTacToeGame(Game):
    """Two-player Tic-Tac-Toe controlled through YouTube chat.

    Commands:
        !ttt join
        !ttt 1 ... !ttt 9

    The first two unique users to join become X and O respectively.
    Only the player whose turn it is may make a move.
    """

    BOARD_SIZE = 9
    WIN_CONDITIONS = (
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    )

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Return the game to its initial waiting-for-players state."""
        self.board: list[str] = [" "] * self.BOARD_SIZE
        self.players: dict[str, str | None] = {"X": None, "O": None}
        self.usernames: dict[str, str] = {}
        self.turn = "X"
        self.finished = False
        self.winner: str | None = None
        self.finish_time: float | None = None

    @property
    def player_count(self) -> int:
        return sum(user_id is not None for user_id in self.players.values())

    @property
    def started(self) -> bool:
        return self.player_count == 2

    def _parse_move(self, command: str) -> int | None:
        parts = command.strip().lower().split()
        if len(parts) != 2 or parts[0] != "!ttt":
            return None

        try:
            position = int(parts[1])
        except ValueError:
            return None

        if not 1 <= position <= 9:
            return None

        return position - 1

    def _join(self, user_id: str, username: str) -> CommandResult:
        if self.finished:
            self.reset()

        if not user_id:
            return CommandResult.INVALID

        # A user can never occupy both slots.
        if user_id in self.players.values():
            self.usernames[user_id] = username
            return CommandResult.INVALID

        if self.players["X"] is None:
            self.players["X"] = user_id
            self.usernames[user_id] = username
            return CommandResult.EXECUTED

        if self.players["O"] is None:
            self.players["O"] = user_id
            self.usernames[user_id] = username
            return CommandResult.EXECUTED

        return CommandResult.INVALID

    def handle_command(
        self,
        command: str,
        user_id: str,
        username: str,
    ) -> CommandResult:
        command = command.strip()

        if not command or not user_id:
            return CommandResult.INVALID

        if command.lower() == "!ttt join":
            return self._join(user_id, username)

        # No moves are accepted until two players exist.
        if not self.started or self.finished:
            return CommandResult.INVALID

        index = self._parse_move(command)
        if index is None:
            return CommandResult.INVALID

        current_player_id = self.players[self.turn]
        if user_id != current_player_id:
            return CommandResult.INVALID

        if self.board[index] != " ":
            return CommandResult.INVALID

        self.board[index] = self.turn
        self._check_game_end()

        if not self.finished:
            self.turn = "O" if self.turn == "X" else "X"

        return CommandResult.EXECUTED

    def _check_game_end(self) -> None:
        for a, b, c in self.WIN_CONDITIONS:
            if (
                self.board[a] != " "
                and self.board[a] == self.board[b] == self.board[c]
            ):
                self.winner = self.board[a]
                self.finished = True
                import time
                self.finish_time = time.time()
                return

        if " " not in self.board:
            self.winner = "DRAW"
            self.finished = True
            import time
            self.finish_time = time.time()

    def update(self) -> None:
        """TTT has no automatic/time-based simulation."""
        return

    def is_finished(self) -> bool:
        if self.finished and self.finish_time is not None:
            import time
            return time.time() - self.finish_time >= 3.0
        return False

    def render(self) -> list[list[str]]:
        width = 30
        inner = width - 2

        def line(text: str = "") -> str:
            # Keep every rendered row exactly width characters.
            text = text[:inner]
            return "|" + text.center(inner) + "|"

        lines: list[str] = [
            "+" + "-" * inner + "+",
            line("TIC TAC TOE"),
            line(),
        ]

        if not self.started:
            lines.append(line(f"Waiting for players... ({self.player_count}/2)"))
            lines.append(line("Type !ttt join"))
        else:
            cells = [
                str(i + 1) if value == " " else value
                for i, value in enumerate(self.board)
            ]

            lines.extend(
                [
                    line(f" {cells[0]} | {cells[1]} | {cells[2]} "),
                    line("-----------"),
                    line(f" {cells[3]} | {cells[4]} | {cells[5]} "),
                    line("-----------"),
                    line(f" {cells[6]} | {cells[7]} | {cells[8]} "),
                    line(),
                ]
            )

            if self.finished:
                if self.winner == "DRAW":
                    status = "DRAW!"
                else:
                    winner_id = self.players.get(self.winner)
                    winner_name = self.usernames.get(winner_id, self.winner) if winner_id else self.winner
                    status = f"@{winner_name} won!"
                lines.append(line(status))
                lines.append(line("Returning to chat..."))
            else:
                pX_id = self.players.get("X")
                pX = self.usernames.get(pX_id, "X") if pX_id else "X"
                pO_id = self.players.get("O")
                pO = self.usernames.get(pO_id, "O") if pO_id else "O"
                lines.append(line(f"X: @{pX} | O: @{pO}"))
                
                current_player_id = self.players.get(self.turn)
                username = self.usernames.get(current_player_id, self.turn) if current_player_id else self.turn
                lines.append(line(f"TURN: @{username}"))

        lines.append("+" + "-" * inner + "+")
        return [list(row) for row in lines]
