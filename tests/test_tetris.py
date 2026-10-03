import unittest

from app.games.tetris import TetrisGame
from app.games.base import CommandResult, render_to_string


class TetrisTests(unittest.TestCase):
    def test_initial_state(self):
        game = TetrisGame(seed=1)
        self.assertFalse(game.is_finished())
        self.assertIsNotNone(game.current)
        self.assertEqual(len(game.board), 14)
        self.assertTrue(all(len(row) == 15 for row in game.board))

    def test_invalid_command_does_not_change_state(self):
        game = TetrisGame(seed=1)
        before = [row.copy() for row in game.board]
        piece = game.current
        self.assertEqual(
            game.handle_command("!banana", "u1", "Alice"),
            CommandResult.INVALID,
        )
        self.assertEqual(game.board, before)
        self.assertEqual(game.current, piece)

    def test_left_and_right(self):
        game = TetrisGame(seed=1)
        start = game.current.col
        self.assertEqual(
            game.handle_command("!left", "u1", "Alice"),
            CommandResult.EXECUTED,
        )
        self.assertEqual(game.current.col, start - 1)

        self.assertEqual(
            game.handle_command("!right", "u1", "Alice"),
            CommandResult.EXECUTED,
        )
        self.assertEqual(game.current.col, start)

    def test_rotate(self):
        game = TetrisGame(seed=1)
        old_rotation = game.current.rotation
        result = game.handle_command("!rotate", "u1", "Alice")
        self.assertEqual(result, CommandResult.EXECUTED)
        self.assertEqual(game.current.rotation, (old_rotation + 1) % 4)

    def test_hard_drop_locks_piece(self):
        game = TetrisGame(seed=1)
        first_kind = game.current.kind
        result = game.handle_command("!drop", "u1", "Alice")
        self.assertEqual(result, CommandResult.EXECUTED)
        self.assertIsNotNone(game.current)
        self.assertNotEqual(game.current.kind, first_kind)
        self.assertTrue(any(cell != "." for row in game.board for cell in row))

    def test_down_at_floor_locks_piece(self):
        game = TetrisGame(seed=1)
        for _ in range(30):
            result = game.handle_command("!down", "u1", "Alice")
            self.assertEqual(result, CommandResult.EXECUTED)
            if game.current is not None and game.current.row == 0:
                break
        self.assertIsNotNone(game.current)

    def test_render_is_rectangular(self):
        game = TetrisGame(seed=1)
        frame = game.render()
        self.assertTrue(frame)
        width = len(frame[0])
        self.assertTrue(all(len(row) == width for row in frame))
        self.assertTrue(all(len(cell) == 1 for row in frame for cell in row))
        self.assertIn("TETRIS", render_to_string(frame))

    def test_lines_can_be_cleared(self):
        game = TetrisGame(seed=1)
        # Fill bottom row except four cells, then force an I piece horizontally.
        game.board[-1] = ["X"] * 15
        game.board[-1][0:4] = ["."] * 4
        game.current.kind = "I"
        game.current.rotation = 0
        game.current.row = 12
        game.current.col = 0
        game.handle_command("!drop", "u1", "Alice")
        self.assertGreaterEqual(game.lines, 1)

    def test_finished_game_rejects_commands(self):
        game = TetrisGame(seed=1)
        game.finished = True
        self.assertEqual(
            game.handle_command("!left", "u1", "Alice"),
            CommandResult.INVALID,
        )


if __name__ == "__main__":
    unittest.main()
