from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto


class CommandResult(Enum):
    """Result of attempting to process a chat command."""

    INVALID = auto()
    EXECUTED = auto()


class Game(ABC):
    """Base interface for all chat-controlled games.

    A game owns only its own state and rules. The GameManager owns
    application-level lifecycle decisions such as switching games or
    returning to the main menu.
    """

    @abstractmethod
    def handle_command(
        self,
        command: str,
        user_id: str,
        username: str,
    ) -> CommandResult:
        """Process one command.

        Return EXECUTED only when the command was valid and actually
        changed the game state. Return INVALID when the command should
        be discarded and the command queue should consider another
        message.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        """Advance automatic/time-based state.

        Turn-based games may legitimately implement this as a no-op.
        """
        raise NotImplementedError

    @abstractmethod
    def render(self) -> list[list[str]]:
        """Return the current frame as a 2D array of single characters."""
        raise NotImplementedError

    @abstractmethod
    def is_finished(self) -> bool:
        """Return whether the game has reached a terminal state."""
        raise NotImplementedError


def render_to_string(frame: list[list[str]]) -> str:
    """Convert a character matrix to the text consumed by OBS."""
    if not frame:
        return ""

    width = len(frame[0])
    if any(len(row) != width for row in frame):
        raise ValueError("Renderer returned a non-rectangular frame.")

    if any(len(char) != 1 for row in frame for char in row):
        raise ValueError("Every rendered cell must contain exactly one character.")

    return "\n".join("".join(row) for row in frame)
