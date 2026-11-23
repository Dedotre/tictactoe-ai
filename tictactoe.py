"""Tic-Tac-Toe rules engine.

A board is a list of 3 rows, each a list of 3 cells: board[row][col].
Cells contain 'X', 'O' or None.
Moves are (x, y) pairs where x is the column and y is the row.
"""

from __future__ import annotations

from typing import Optional

SYMBOLS = ("X", "O")
SIZE = 3

Board = list[list[Optional[str]]]
Move = tuple[int, int]


class IllegalMoveError(ValueError):
    """Raised for malformed, out-of-bounds or already-taken moves."""


def new_board() -> Board:
    return [[None for _ in range(SIZE)] for _ in range(SIZE)]


def render(board: Board) -> str:
    rule = "  " + "-" * (SIZE * 2)
    lines = ["  " + " ".join(str(i) for i in range(SIZE)), rule]
    for y, row in enumerate(board):
        cells = " ".join(cell if cell is not None else " " for cell in row)
        lines.append(f"{y}|{cells}|")
    lines.append(rule)
    return "\n".join(lines)


def get_winner(board: Board) -> Optional[str]:
    for line in _lines(board):
        first = line[0]
        if first is not None and all(cell == first for cell in line):
            return first
    return None


def is_board_full(board: Board) -> bool:
    return all(cell is not None for row in board for cell in row)


def is_valid_move(board: Board, move: object) -> bool:
    if not _is_well_formed(move):
        return False
    x, y = move
    return 0 <= x < SIZE and 0 <= y < SIZE and board[y][x] is None


def make_move(board: Board, move: Move, player: str) -> Board:
    if not _is_well_formed(move):
        raise IllegalMoveError(f"Move must be an (x, y) pair of integers, got {move!r}")
    x, y = move
    if not (0 <= x < SIZE and 0 <= y < SIZE):
        raise IllegalMoveError(f"Can't make move {(x, y)}, square is outside the board!")
    if board[y][x] is not None:
        raise IllegalMoveError(f"Can't make move {(x, y)}, square already taken!")
    new = [row[:] for row in board]
    new[y][x] = player
    return new


def legal_moves(board: Board) -> list[Move]:
    return [(x, y) for y in range(SIZE) for x in range(SIZE) if board[y][x] is None]


def _lines(board: Board) -> list[list[Optional[str]]]:
    rows = [list(row) for row in board]
    columns = [[board[y][x] for y in range(SIZE)] for x in range(SIZE)]
    diagonals = [
        [board[i][i] for i in range(SIZE)],
        [board[i][SIZE - 1 - i] for i in range(SIZE)],
    ]
    return rows + columns + diagonals


def _is_well_formed(move: object) -> bool:
    return (
        isinstance(move, (tuple, list))
        and len(move) == 2
        and all(
            isinstance(coordinate, int) and not isinstance(coordinate, bool)
            for coordinate in move
        )
    )
