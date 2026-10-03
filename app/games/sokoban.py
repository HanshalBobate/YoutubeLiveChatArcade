from __future__ import annotations

import random
from dataclasses import dataclass
from typing import ClassVar

from .base import CommandResult, Game


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass(frozen=True)
class Level:
    name: str
    rows: tuple[str, ...]


def generate_procedural_level(seed: int, width: int = 30, height: int = 15) -> Level:
    rng = random.Random(seed)
    
    for attempt in range(100):
        terrain = [[" " for _ in range(width)] for _ in range(height)]
        for i in range(width):
            terrain[0][i] = "#"
            terrain[height-1][i] = "#"
        for i in range(height):
            terrain[i][0] = "#"
            terrain[i][width-1] = "#"
            
        # Add random obstacles
        for _ in range((width * height) // 50):
            r = rng.randint(2, height-3)
            c = rng.randint(2, width-3)
            terrain[r][c] = "#"
            
        def is_empty(r, c, c_set):
            return terrain[r][c] != "#" and Position(r, c) not in c_set

        target_crates = rng.randint(1, 3)
        crates = set()
        while len(crates) < target_crates:
            r = rng.randint(2, height-3)
            c = rng.randint(2, width-3)
            if is_empty(r, c, crates):
                crates.add(Position(r, c))
                
        player = None
        while player is None:
            r = rng.randint(1, height-2)
            c = rng.randint(1, width-2)
            if is_empty(r, c, crates):
                player = Position(r, c)
                
        current_crates = set(crates)
        current_player = player
        
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moved_at_least_once = False
        
        for _ in range(1500):
            dr, dc = rng.choice(moves)
            tr, tc = current_player.row + dr, current_player.col + dc
            target = Position(tr, tc)
            
            if terrain[tr][tc] == "#":
                continue
                
            if target in current_crates:
                br, bc = tr + dr, tc + dc
                beyond = Position(br, bc)
                if terrain[br][bc] == "#" or beyond in current_crates:
                    continue
                current_crates.remove(target)
                current_crates.add(beyond)
                moved_at_least_once = True
                
            current_player = target
            
        # Only accept levels where crates actually got moved around
        if moved_at_least_once and current_crates != crates:
            # Remove any crates that ended up on a starting position
            # This ensures no crates start on goals!
            goals = current_crates - crates
            starting_crates = crates - current_crates
            
            if not (1 <= len(goals) <= 3):
                continue
                
            rows = []
            for r in range(height):
                row_chars = []
                for c in range(width):
                    pos = Position(r, c)
                    if terrain[r][c] == "#":
                        row_chars.append("█")
                    elif pos in goals and pos == player:
                        row_chars.append("☺")
                    elif pos in goals:
                        row_chars.append("·")
                    elif pos in starting_crates:
                        row_chars.append("□")
                    elif pos == player:
                        row_chars.append("☻")
                    else:
                        row_chars.append(" ")
                rows.append("".join(row_chars))
                
            return Level(f"Seed: {seed}", tuple(rows))
            
    # Fallback if generation fails
    return Level("Fallback", ("████████", "█ · □☻ █", "████████"))


class Sokoban(Game):
    WALL: ClassVar[str] = "█"
    FLOOR: ClassVar[str] = " "
    GOAL: ClassVar[str] = "·"
    CRATE: ClassVar[str] = "□"
    PLAYER: ClassVar[str] = "☻"
    CRATE_ON_GOAL: ClassVar[str] = "▣"
    PLAYER_ON_GOAL: ClassVar[str] = "☺"

    COMMANDS: ClassVar[dict[str, tuple[int, int]]] = {
        "!up": (-1, 0),
        "!u": (-1, 0),
        "!down": (1, 0),
        "!d": (1, 0),
        "!left": (0, -1),
        "!l": (0, -1),
        "!right": (0, 1),
        "!r": (0, 1),
    }

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed if seed is not None else random.randint(1000, 9999)
        self.moves = 0
        self.pushes = 0
        self.finished = False
        self.last_move_username: str | None = None
        self.frame_count = 0
        self._terrain: list[list[str]] = []
        self._goals: set[Position] = set()
        self._crates: set[Position] = set()
        self._player = Position(0, 0)
        self._load_level(self.seed)

    @property
    def level_name(self) -> str:
        return f"Procedural Level (Seed {self.seed})"

    def reset(self) -> None:
        self._load_level(self.seed)

    def next_level(self) -> bool:
        self.seed = random.randint(1000, 9999)
        self._load_level(self.seed)
        return True

    def handle_command(
        self, command: str, user_id: str, username: str
    ) -> CommandResult:
        if self.finished:
            return CommandResult.INVALID

        normalized = command.strip().lower().split()
        if not normalized or normalized[0] not in self.COMMANDS:
            return CommandResult.INVALID

        if len(normalized) != 1:
            return CommandResult.INVALID

        dr, dc = self.COMMANDS[normalized[0]]
        target = Position(self._player.row + dr, self._player.col + dc)

        if not self._in_bounds(target) or self._terrain[target.row][target.col] == self.WALL:
            return CommandResult.INVALID

        if target in self._crates:
            beyond = Position(target.row + dr, target.col + dc)
            if (
                not self._in_bounds(beyond)
                or self._terrain[beyond.row][beyond.col] == self.WALL
                or beyond in self._crates
            ):
                return CommandResult.INVALID

            self._crates.remove(target)
            self._crates.add(beyond)
            self.pushes += 1

        self._player = target
        self.moves += 1
        self.last_move_username = username
        self.finished = self._is_solved()
        return CommandResult.EXECUTED

    def update(self) -> None:
        self.frame_count += 1

    def is_finished(self) -> bool:
        return self.finished

    def render(self) -> list[list[str]]:
        # Draw game frame
        frame = [row[:] for row in self._terrain]

        for pos in self._goals:
            frame[pos.row][pos.col] = self.GOAL

        for pos in self._crates:
            frame[pos.row][pos.col] = (
                self.CRATE_ON_GOAL if pos in self._goals else self.CRATE
            )

        # Blink player: visible for 5 frames, invisible for 5 frames
        if self.frame_count % 10 < 5:
            player_glyph = self.PLAYER_ON_GOAL if self._player in self._goals else self.PLAYER
        else:
            player_glyph = self.GOAL if self._player in self._goals else self.FLOOR
            
        frame[self._player.row][self._player.col] = player_glyph
        
        # Expand frame to 43 width to make space for UI without interfering with 30-width game
        for row in frame:
            if len(row) < 43:
                row.extend([" "] * (43 - len(row)))
                
        # Draw the latest move
        if self.last_move_username:
            text = f"By: @{self.last_move_username}"
        else:
            text = "By: -"
            
        for j, ch in enumerate(text):
            if 32 + j < 43:
                frame[2][32 + j] = ch
                
        return frame

    def _load_level(self, seed: int) -> None:
        level = generate_procedural_level(seed)

        terrain: list[list[str]] = []
        goals: set[Position] = set()
        crates: set[Position] = set()
        player: Position | None = None

        for r, row in enumerate(level.rows):
            parsed_row: list[str] = []
            for c, char in enumerate(row):
                pos = Position(r, c)
                if char == self.WALL:
                    parsed_row.append(self.WALL)
                elif char in (self.GOAL, self.CRATE_ON_GOAL, self.PLAYER_ON_GOAL):
                    parsed_row.append(self.GOAL)
                else:
                    parsed_row.append(self.FLOOR)

                if char in (self.GOAL, self.CRATE_ON_GOAL, self.PLAYER_ON_GOAL):
                    goals.add(pos)
                if char in (self.CRATE, self.CRATE_ON_GOAL):
                    crates.add(pos)
                if char in (self.PLAYER, self.PLAYER_ON_GOAL):
                    player = pos

            terrain.append(parsed_row)

        self._terrain = terrain
        self._goals = goals
        self._crates = crates
        if player is not None:
            self._player = player
        self.moves = 0
        self.pushes = 0
        self.finished = self._is_solved()

    def _in_bounds(self, pos: Position) -> bool:
        return (
            0 <= pos.row < len(self._terrain)
            and 0 <= pos.col < len(self._terrain[0])
        )

    def _is_solved(self) -> bool:
        return self._crates == self._goals
