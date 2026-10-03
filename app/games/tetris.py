from __future__ import annotations

import random
from dataclasses import dataclass

from typing import ClassVar
from .base import CommandResult, Game


@dataclass
class Piece:
    kind: str
    rotation: int
    row: int
    col: int


class TetrisGame(Game):
    """Deterministic, chat-controlled Tetris.

    Every successful command advances exactly one action. No keyboard or
    realtime input is required.

    Commands:
        !left
        !right
        !down
        !rotate
        !drop
        !harddrop

    A piece locks when it can no longer move downward. After locking,
    completed lines are cleared and a new piece is spawned.
    """

    WIDTH = 15
    HEIGHT = 14

    # Four rotations are defined for each tetromino. Coordinates are
    # (row, col), relative to the piece's top-left bounding box.
    SHAPES: ClassVar[dict[str, tuple[tuple[tuple[int, int], ...], ...]]] = {
        "I": (
            ((1, 0), (1, 1), (1, 2), (1, 3)),
            ((0, 2), (1, 2), (2, 2), (3, 2)),
            ((2, 0), (2, 1), (2, 2), (2, 3)),
            ((0, 1), (1, 1), (2, 1), (3, 1)),
        ),
        "O": (
            ((0, 1), (0, 2), (1, 1), (1, 2)),
        ) * 4,
        "T": (
            ((0, 1), (1, 0), (1, 1), (1, 2)),
            ((0, 1), (1, 1), (1, 2), (2, 1)),
            ((1, 0), (1, 1), (1, 2), (2, 1)),
            ((0, 1), (1, 0), (1, 1), (2, 1)),
        ),
        "J": (
            ((0, 0), (1, 0), (1, 1), (1, 2)),
            ((0, 1), (0, 2), (1, 1), (2, 1)),
            ((0, 0), (0, 1), (0, 2), (1, 2)),
            ((0, 1), (1, 1), (2, 0), (2, 1)),
        ),
        "L": (
            ((0, 2), (1, 0), (1, 1), (1, 2)),
            ((0, 1), (1, 1), (2, 1), (2, 2)),
            ((0, 0), (0, 1), (0, 2), (1, 0)),
            ((0, 0), (0, 1), (1, 1), (2, 1)),
        ),
        "S": (
            ((0, 1), (0, 2), (1, 0), (1, 1)),
            ((0, 1), (1, 1), (1, 2), (2, 2)),
            ((1, 0), (1, 1), (2, 1), (2, 2)),
            ((0, 0), (1, 0), (1, 1), (2, 1)),
        ),
        "Z": (
            ((0, 0), (0, 1), (1, 1), (1, 2)),
            ((0, 2), (1, 1), (1, 2), (2, 1)),
            ((1, 0), (1, 1), (2, 1), (2, 2)),
            ((0, 1), (1, 0), (1, 1), (2, 0)),
        ),
    }

    COMMANDS: ClassVar[dict[str, str]] = {
        "!left": "left",
        "!l": "left",
        "!right": "right",
        "!r": "right",
        "!down": "down",
        "!d": "down",
        "!rotate": "rotate",
        "!rot": "rotate",
        "!up": "rotate",
        "!drop": "drop",
        "!harddrop": "drop",
    }

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        import time
        self.last_drop_time = time.time()
        self.reset()

    def reset(self) -> None:
        self.board: list[list[str]] = [
            ["."] * self.WIDTH for _ in range(self.HEIGHT)
        ]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.finished = False
        self.last_move_username: str | None = None
        self.current: Piece | None = None
        self.next_kind = self._random_kind()
        self._spawn_piece()

    def _random_kind(self) -> str:
        return self._rng.choice(tuple(self.SHAPES))

    def _spawn_piece(self) -> None:
        kind = self.next_kind
        self.next_kind = self._random_kind()
        self.current = Piece(
            kind=kind,
            rotation=0,
            row=0,
            col=(self.WIDTH - 4) // 2,
        )

        if not self._can_place(self.current):
            self.finished = True

    def _cells(self, piece: Piece | None = None) -> tuple[tuple[int, int], ...]:
        piece = piece or self.current
        if piece is None:
            return ()
        return self.SHAPES[piece.kind][piece.rotation % 4]

    def _can_place(self, piece: Piece) -> bool:
        for dr, dc in self._cells(piece):
            r = piece.row + dr
            c = piece.col + dc
            if r < 0 or r >= self.HEIGHT or c < 0 or c >= self.WIDTH:
                return False
            if self.board[r][c] != ".":
                return False
        return True

    def _try_move(self, dr: int, dc: int) -> bool:
        if self.current is None:
            return False
        candidate = Piece(
            self.current.kind,
            self.current.rotation,
            self.current.row + dr,
            self.current.col + dc,
        )
        if not self._can_place(candidate):
            return False
        self.current = candidate
        return True

    def _try_rotate(self) -> bool:
        if self.current is None:
            return False

        candidate = Piece(
            self.current.kind,
            (self.current.rotation + 1) % 4,
            self.current.row,
            self.current.col,
        )

        # Small wall-kick set. This is intentionally deterministic.
        kicks = ((0, 0), (0, -1), (0, 1), (-1, 0), (0, -2), (0, 2))
        for dr, dc in kicks:
            kicked = Piece(
                candidate.kind,
                candidate.rotation,
                candidate.row + dr,
                candidate.col + dc,
            )
            if self._can_place(kicked):
                self.current = kicked
                return True

        return False

    def _lock_piece(self) -> None:
        if self.current is None:
            return

        for r, c in self._cells():
            rr = self.current.row + r
            cc = self.current.col + c
            if 0 <= rr < self.HEIGHT and 0 <= cc < self.WIDTH:
                self.board[rr][cc] = self.current.kind

        cleared = self._clear_lines()
        if cleared:
            self.lines += cleared
            self.score += (100, 300, 500, 800)[cleared - 1] * self.level
            self.level = 1 + self.lines // 10

        self._spawn_piece()

    def _clear_lines(self) -> int:
        remaining = [
            row for row in self.board
            if any(cell == "." for cell in row)
        ]
        cleared = self.HEIGHT - len(remaining)
        self.board = [[ "."] * self.WIDTH for _ in range(cleared)] + remaining
        return cleared

    def _hard_drop(self) -> int:
        distance = 0
        while self._try_move(1, 0):
            distance += 1
        return distance

    def handle_command(
        self,
        command: str,
        user_id: str,
        username: str,
    ) -> CommandResult:
        if self.finished or not command.strip():
            return CommandResult.INVALID

        action = self.COMMANDS.get(command.strip().lower())
        if action is None:
            return CommandResult.INVALID

        if self.current is None:
            return CommandResult.INVALID

        result = CommandResult.INVALID
        if action == "left" and self._try_move(0, -1):
            result = CommandResult.EXECUTED
        elif action == "right" and self._try_move(0, 1):
            result = CommandResult.EXECUTED
        elif action == "down":
            if not self._try_move(1, 0):
                self._lock_piece()
            result = CommandResult.EXECUTED
        elif action == "rotate" and self._try_rotate():
            result = CommandResult.EXECUTED
        elif action == "drop":
            self._hard_drop()
            self._lock_piece()
            result = CommandResult.EXECUTED

        if result == CommandResult.EXECUTED:
            self.last_move_username = username
            
        return result

    def update(self) -> None:
        if self.finished:
            return
            
        import time
        current_time = time.time()
        if current_time - self.last_drop_time >= 10.0:
            self.last_drop_time = current_time
            if not self._try_move(1, 0):
                self._lock_piece()
            self.last_move_username = "SYSTEM (Auto-Drop)"

    def is_finished(self) -> bool:
        return self.finished

    def render(self) -> list[list[str]]:
        # Hard constraint: 15 rows by 43 columns max.
        grid = [[" " for _ in range(43)] for _ in range(15)]
        
        visible = [row.copy() for row in self.board]
        if self.current is not None and not self.finished:
            for dr, dc in self._cells():
                r = self.current.row + dr
                c = self.current.col + dc
                if 0 <= r < self.HEIGHT and 0 <= c < self.WIDTH:
                    visible[r][c] = self.current.kind

        # Draw left board with side borders only
        for r in range(self.HEIGHT):
            row_str = "|" + "".join(visible[r]) + "|"
            for j, ch in enumerate(row_str):
                grid[r][j] = ch

        # Draw right panel
        panel = [
            "TETRIS",
            "",
            f"Score: {self.score}",
            f"Level: {self.level}",
            f"Lines: {self.lines}",
            "",
            "!left !right",
            "!down !drop",
            "!rotate",
            "",
        ]
        
        if self.last_move_username:
            panel.append(f"By: @{self.last_move_username}")
        else:
            panel.append("By: -")
        
        if self.finished:
            panel.append("")
            panel.append("GAME OVER")
            
        for i, line in enumerate(panel):
            for j, ch in enumerate(line):
                grid[i+1][self.WIDTH + 3 + j] = ch

        return grid
