import io
import unittest
from unittest.mock import patch

from game import play_game
from players import Player, RandomPlayer


class ScriptedPlayer(Player):
    def __init__(self, symbol: str, moves):
        super().__init__(symbol, f"Scripted {symbol}")
        self._moves = iter(moves)

    def choose_move(self, board):
        return next(self._moves)


def silent_game(x_player, o_player) -> str | None:
    with patch("sys.stdout", new=io.StringIO()):
        return play_game(x_player, o_player)


class PlayGameTests(unittest.TestCase):
    def test_x_wins_with_a_diagonal(self):
        x = ScriptedPlayer("X", [(0, 0), (1, 1), (2, 2)])
        o = ScriptedPlayer("O", [(0, 1), (0, 2)])
        self.assertEqual(silent_game(x, o), "X")

    def test_o_can_win(self):
        x = ScriptedPlayer("X", [(0, 0), (2, 2), (1, 0)])
        o = ScriptedPlayer("O", [(0, 1), (1, 1), (2, 1)])
        self.assertEqual(silent_game(x, o), "O")

    def test_full_board_without_a_line_is_a_draw(self):
        x = ScriptedPlayer("X", [(0, 0), (2, 0), (0, 1), (1, 2), (2, 2)])
        o = ScriptedPlayer("O", [(1, 0), (1, 1), (2, 1), (0, 2)])
        self.assertIsNone(silent_game(x, o))

    def test_display_false_prints_nothing(self):
        x = ScriptedPlayer("X", [(0, 0), (1, 1), (2, 2)])
        o = ScriptedPlayer("O", [(0, 1), (0, 2)])
        out = io.StringIO()
        with patch("sys.stdout", new=out):
            result = play_game(x, o, display=False)
        self.assertEqual(result, "X")
        self.assertEqual(out.getvalue(), "")

    def test_display_true_announces_the_winner(self):
        x = ScriptedPlayer("X", [(0, 0), (1, 1), (2, 2)])
        o = ScriptedPlayer("O", [(0, 1), (0, 2)])
        out = io.StringIO()
        with patch("sys.stdout", new=out):
            play_game(x, o)
        self.assertIn("WINNER IS X!!", out.getvalue())

    def test_random_games_always_reach_a_result(self):
        for seed in range(50):
            with self.subTest(seed=seed):
                x = RandomPlayer("X", seed=seed)
                o = RandomPlayer("O", seed=seed + 100)
                self.assertIn(silent_game(x, o), ("X", "O", None))


if __name__ == "__main__":
    unittest.main()
