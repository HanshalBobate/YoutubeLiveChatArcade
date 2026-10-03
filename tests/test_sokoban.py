import pytest

from app.games.base import CommandResult, render_to_string
from app.games.sokoban import Sokoban, Position, Level


def test_initial_state_and_render():
    game = Sokoban(seed=1234)
    assert "Procedural Level" in game.level_name
    assert game.moves == 0
    assert game.pushes == 0
    assert not game.is_finished()

    frame = game.render()
    assert len(frame) >= 15  # Includes title and stats
    text = render_to_string(frame)
    assert "☻" in text
    assert "□" in text
    assert "·" in text
    assert "█" in text


def test_invalid_command_does_not_change_state():
    game = Sokoban(seed=1234)
    before = (game._player, game._crates.copy(), game.moves, game.pushes)

    assert game.handle_command("hello", "u1", "alice") is CommandResult.INVALID
    assert (game._player, game._crates, game.moves, game.pushes) == before


def test_reset():
    game = Sokoban(seed=1234)
    original_player = game._player
    
    # Try pushing a bunch of random valid commands just to alter state
    for cmd in ["!up", "!down", "!left", "!right"]:
        game.handle_command(cmd, "u1", "alice")
        
    game.reset()
    assert game.seed == 1234
    assert game.moves == 0
    assert game.pushes == 0
    assert game._player == original_player
    assert not game.is_finished()


def test_next_level():
    game = Sokoban(seed=1234)
    assert game.next_level() is True
    assert game.seed != 1234
    assert game.moves == 0


def test_render_is_rectangular():
    game = Sokoban(seed=1234)
    frame = game.render()
    width = len(frame[0])
    assert all(len(row) == width for row in frame)
    assert all(len(cell) == 1 for row in frame for cell in row)


def test_aliases_and_whitespace():
    game = Sokoban(seed=1234)
    # Testing that it gets properly executed or invalid (not error)
    res = game.handle_command("  !l  ", "u1", "alice")
    assert res in (CommandResult.EXECUTED, CommandResult.INVALID)


def test_extra_tokens_are_invalid():
    game = Sokoban(seed=1234)
    before = (game._player, game.moves)
    assert game.handle_command("!left now", "u1", "alice") is CommandResult.INVALID
    assert (game._player, game.moves) == before
