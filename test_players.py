import io
import unittest
from unittest.mock import patch

from players import HumanPlayer, RandomPlayer, get_move
from tictactoe import legal_moves, make_move, new_board


class GetMoveTests(unittest.TestCase):
    @patch("builtins.input", side_effect=["1", "2"])
    def test_reads_coordinates_in_order(self, mock_input):
        self.assertEqual(get_move(), (1, 2))
        prompts = [call.args[0] for call in mock_input.call_args_list]
        self.assertEqual(
            prompts,
            [
                "What is your move's X co-ordinate?: ",
                "What is your move's Y co-ordinate?: ",
            ],
        )

    @patch("builtins.input", side_effect=["abc", "4", "0"])
    def test_reprompts_on_non_numeric_input(self, _):
        with patch("sys.stdout", new=io.StringIO()) as out:
            self.assertEqual(get_move(), (4, 0))
        self.assertIn("whole number", out.getvalue())


class HumanPlayerTests(unittest.TestCase):
    @patch("players.get_move", side_effect=[(0, 0), (0, 0), (1, 1)])
    def test_reprompts_after_illegal_move(self, mock_get_move):
        board = make_move(new_board(), (0, 0), "X")
        with patch("sys.stdout", new=io.StringIO()) as out:
            move = HumanPlayer("O", "You").choose_move(board)
        self.assertEqual(move, (1, 1))
        self.assertEqual(mock_get_move.call_count, 3)
        self.assertIn("Invalid move", out.getvalue())


class RandomPlayerTests(unittest.TestCase):
    def test_returns_legal_moves_only(self):
        board = new_board()
        board = make_move(board, (1, 1), "X")
        ai = RandomPlayer("O", seed=3)
        for _ in range(50):
            self.assertIn(ai.choose_move(board), legal_moves(board))

    def test_same_seed_gives_same_moves(self):
        board = new_board()
        first = RandomPlayer("X", seed=7)
        second = RandomPlayer("X", seed=7)
        self.assertEqual([first.choose_move(board) for _ in range(10)], [second.choose_move(board) for _ in range(10)])


class PlayerLabelTests(unittest.TestCase):
    def test_label_includes_name_and_symbol(self):
        self.assertEqual(str(HumanPlayer("X", "You")), "You (X)")


if __name__ == "__main__":
    unittest.main()
