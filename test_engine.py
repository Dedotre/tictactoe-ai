import unittest

from tictactoe import (
    IllegalMoveError,
    get_winner,
    is_board_full,
    is_valid_move,
    legal_moves,
    make_move,
    new_board,
    render,
)


def board_from(*rows: str) -> list[list[str | None]]:
    return [[None if cell == "." else cell for cell in row] for row in rows]


class NewBoardTests(unittest.TestCase):
    def test_is_three_by_three_and_empty(self):
        board = new_board()
        self.assertEqual(len(board), 3)
        for row in board:
            self.assertEqual(row, [None, None, None])

    def test_rows_are_independent(self):
        board = new_board()
        board[0][0] = "X"
        self.assertIsNone(board[1][0])


class RenderTests(unittest.TestCase):
    def test_empty_board(self):
        expected = "\n".join(
            [
                "  0 1 2",
                "  ------",
                "0|     |",
                "1|     |",
                "2|     |",
                "  ------",
            ]
        )
        self.assertEqual(render(new_board()), expected)

    def test_board_with_moves(self):
        board = board_from("XO.", "...", "...")
        expected = "\n".join(
            [
                "  0 1 2",
                "  ------",
                "0|X O  |",
                "1|     |",
                "2|     |",
                "  ------",
            ]
        )
        self.assertEqual(render(board), expected)


class MakeMoveTests(unittest.TestCase):
    def test_places_symbol_at_coordinates(self):
        board = make_move(new_board(), (1, 2), "X")
        self.assertEqual(board[2][1], "X")

    def test_does_not_mutate_the_original_board(self):
        board = new_board()
        new = make_move(board, (0, 0), "O")
        self.assertIsNone(board[0][0])
        self.assertEqual(new[0][0], "O")
        self.assertIsNot(new, board)
        for old_row, new_row in zip(board, new):
            self.assertIsNot(old_row, new_row)

    def test_raises_on_taken_square(self):
        board = make_move(new_board(), (2, 0), "X")
        with self.assertRaisesRegex(IllegalMoveError, "already taken"):
            make_move(board, (2, 0), "O")

    def test_raises_on_out_of_bounds(self):
        for move in [(3, 0), (0, 3), (-1, 1), (1, -2)]:
            with self.subTest(move=move):
                with self.assertRaisesRegex(IllegalMoveError, "outside the board"):
                    make_move(new_board(), move, "X")

    def test_raises_on_malformed_moves(self):
        for move in [None, "00", (0,), (0, 0, 0), ("0", "1"), (0.5, 1), (True, 0)]:
            with self.subTest(move=move):
                with self.assertRaises(IllegalMoveError):
                    make_move(new_board(), move, "X")


class IsValidMoveTests(unittest.TestCase):
    def test_empty_square_is_valid(self):
        self.assertTrue(is_valid_move(new_board(), (2, 2)))

    def test_taken_square_is_invalid(self):
        board = make_move(new_board(), (1, 1), "X")
        self.assertFalse(is_valid_move(board, (1, 1)))

    def test_out_of_bounds_and_malformed_are_invalid(self):
        for move in [(3, 3), (-1, 0), None, "x", (0, 0, 0)]:
            with self.subTest(move=move):
                self.assertFalse(is_valid_move(new_board(), move))


class LegalMovesTests(unittest.TestCase):
    def test_all_squares_when_board_is_empty(self):
        self.assertEqual(len(legal_moves(new_board())), 9)

    def test_excludes_taken_squares(self):
        board = make_move(new_board(), (0, 0), "X")
        moves = legal_moves(board)
        self.assertEqual(len(moves), 8)
        self.assertNotIn((0, 0), moves)


class WinnerTests(unittest.TestCase):
    def test_no_winner_on_empty_board(self):
        self.assertIsNone(get_winner(new_board()))

    def test_row_win(self):
        self.assertEqual(get_winner(board_from("XXX", "OO.", "...")), "X")

    def test_column_win(self):
        self.assertEqual(get_winner(board_from("O.X", "O.X", "O..")), "O")

    def test_main_diagonal_win(self):
        self.assertEqual(get_winner(board_from("X.O", "OX.", "O.X")), "X")

    def test_anti_diagonal_win(self):
        self.assertEqual(get_winner(board_from("O.X", "OX.", "X.O")), "X")

    def test_partial_line_is_not_a_win(self):
        self.assertIsNone(get_winner(board_from("XX.", "OO.", "X..")))

    def test_draw_has_no_winner(self):
        board = board_from("XOX", "XXO", "OXO")
        self.assertIsNone(get_winner(board))
        self.assertTrue(is_board_full(board))


class BoardFullTests(unittest.TestCase):
    def test_empty_board_is_not_full(self):
        self.assertFalse(is_board_full(new_board()))

    def test_board_with_one_gap_is_not_full(self):
        self.assertFalse(is_board_full(board_from("XOX", "XXO", "OX.")))

    def test_full_board_is_full(self):
        self.assertTrue(is_board_full(board_from("XOX", "XXO", "OXO")))


if __name__ == "__main__":
    unittest.main()
