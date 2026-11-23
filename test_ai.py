import io
import unittest
from unittest.mock import patch

from players import (
    PLAYER_TYPES,
    MinimaxPlayer,
    RandomPlayer,
    WinningAndBlockingPlayer,
    WinningPlayer,
    create_player,
)
from game import play_game
from tictactoe import get_winner, legal_moves, make_move, new_board


def board_from(*rows: str) -> list[list[str | None]]:
    return [[None if cell == "." else cell for cell in row] for row in rows]


def silent_play(x_player, o_player) -> str | None:
    with patch("sys.stdout", new=io.StringIO()):
        return play_game(x_player, o_player, display=False)


class WinningPlayerTests(unittest.TestCase):
    def test_takes_an_immediate_win_as_x(self):
        board = board_from("XX.", "OO.", "...")
        self.assertEqual(WinningPlayer("X").choose_move(board), (2, 0))

    def test_takes_an_immediate_win_as_o(self):
        board = board_from("XX.", "OO.", "...")
        self.assertEqual(WinningPlayer("O").choose_move(board), (2, 1))

    def test_falls_back_to_a_legal_move(self):
        board = new_board()
        self.assertIn(WinningPlayer("O", seed=1).choose_move(board), legal_moves(board))


class WinningAndBlockingPlayerTests(unittest.TestCase):
    def test_prefers_its_own_win_over_blocking(self):
        board = board_from("XX.", "OO.", "...")
        ai = WinningAndBlockingPlayer("O")
        self.assertEqual(ai.choose_move(board), (2, 1))

    def test_blocks_the_opponents_win(self):
        board = board_from("XX.", ".O.", "..O")
        ai = WinningAndBlockingPlayer("O")
        self.assertEqual(ai.choose_move(board), (2, 0))

    def test_falls_back_to_a_legal_move(self):
        board = new_board()
        self.assertIn(WinningAndBlockingPlayer("X", seed=1).choose_move(board), legal_moves(board))


class MinimaxPlayerTests(unittest.TestCase):
    def test_takes_an_immediate_win(self):
        board = board_from("XOX", "OO.", "X..")
        self.assertEqual(MinimaxPlayer("O").choose_move(board), (2, 1))

    def test_blocks_an_immediate_loss_when_blocking_saves_the_game(self):
        board = board_from("XX.", ".O.", "..O")
        self.assertEqual(MinimaxPlayer("O").choose_move(board), (2, 0))

    def test_only_ever_returns_legal_moves(self):
        board = board_from("XO.", "X..", "O..")
        self.assertIn(MinimaxPlayer("O").choose_move(board), legal_moves(board))

    def test_always_draws_against_a_perfect_opponent(self):
        for _ in range(10):
            self.assertIsNone(silent_play(MinimaxPlayer("X"), MinimaxPlayer("O")))

    def test_never_loses_against_random(self):
        for seed in range(60):
            with self.subTest(seed=seed):
                self.assertNotEqual(silent_play(MinimaxPlayer("X"), RandomPlayer("O", seed=seed)), "O")
                self.assertNotEqual(silent_play(RandomPlayer("X", seed=seed), MinimaxPlayer("O")), "X")

    def test_never_loses_against_the_blocking_ai(self):
        for seed in range(30):
            with self.subTest(seed=seed):
                self.assertNotEqual(
                    silent_play(MinimaxPlayer("X"), WinningAndBlockingPlayer("O", seed=seed)), "O"
                )
                self.assertNotEqual(
                    silent_play(WinningAndBlockingPlayer("X", seed=seed), MinimaxPlayer("O")), "X"
                )

    def test_caches_scores_between_lookups(self):
        ai = MinimaxPlayer("X")
        ai.choose_move(new_board())
        self.assertGreater(len(ai._cache), 0)


class CreatePlayerTests(unittest.TestCase):
    def test_builds_each_known_player_type(self):
        expected = {
            "human": "HumanPlayer",
            "random": "RandomPlayer",
            "winning": "WinningPlayer",
            "blocking": "WinningAndBlockingPlayer",
            "minimax": "MinimaxPlayer",
        }
        for kind, class_name in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(type(create_player(kind, "X")).__name__, class_name)

    def test_assigns_the_requested_symbol(self):
        self.assertEqual(create_player("minimax", "O").symbol, "O")

    def test_rejects_unknown_player_types(self):
        with self.assertRaises(ValueError):
            create_player("cheating", "X")

    def test_player_types_lists_all_factories(self):
        self.assertEqual(set(PLAYER_TYPES), {"human", "random", "winning", "blocking", "minimax"})


class HeuristicBattleTests(unittest.TestCase):
    def test_blocking_ai_never_loses_to_random(self):
        for seed in range(20):
            with self.subTest(seed=seed):
                self.assertNotEqual(
                    silent_play(WinningAndBlockingPlayer("X", seed=seed), RandomPlayer("O", seed=seed + 50)),
                    "O",
                )


if __name__ == "__main__":
    unittest.main()
