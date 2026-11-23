"""Game loop that alternates two players until someone wins or the board fills up."""

from __future__ import annotations

from players import Player
from tictactoe import get_winner, is_board_full, make_move, new_board, render


def play_game(x_player: Player, o_player: Player, display: bool = True) -> str | None:
    """Play a single game and return 'X', 'O' or None for a draw."""
    board = new_board()
    players = {"X": x_player, "O": o_player}
    current = "X"

    while True:
        if display:
            print()
            print(render(board))
            print(f"{players[current]} to play.")

        board = make_move(board, players[current].choose_move(board), current)

        winner = get_winner(board)
        if winner is not None:
            if display:
                print()
                print(render(board))
                print(f"WINNER IS {winner}!!")
            return winner

        if is_board_full(board):
            if display:
                print()
                print(render(board))
                print("IT'S A DRAW!!")
            return None

        current = "O" if current == "X" else "X"
