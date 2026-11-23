"""Players: humans at the terminal, heuristic AIs and the perfect minimax AI."""

from __future__ import annotations

import random

from tictactoe import (
    Board,
    Move,
    get_winner,
    is_board_full,
    is_valid_move,
    legal_moves,
    make_move,
)

X_PROMPT = "What is your move's X co-ordinate?: "
Y_PROMPT = "What is your move's Y co-ordinate?: "

PLAYER_TYPES = ("human", "random", "winning", "blocking", "minimax")
MAX_SCORE = 10


def get_move() -> Move:
    return _prompt_int(X_PROMPT), _prompt_int(Y_PROMPT)


def _prompt_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


class Player:
    def __init__(self, symbol: str, name: str):
        self.symbol = symbol
        self.name = name

    def choose_move(self, board: Board) -> Move:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"


class HumanPlayer(Player):
    def choose_move(self, board: Board) -> Move:
        while True:
            move = get_move()
            if is_valid_move(board, move):
                return move
            print("Invalid move, try again.")


class RandomPlayer(Player):
    def __init__(self, symbol: str, name: str = "Random AI", seed: int | None = None):
        super().__init__(symbol, name)
        self._rng = random.Random(seed)

    def choose_move(self, board: Board) -> Move:
        return self._rng.choice(legal_moves(board))


class WinningPlayer(Player):
    def __init__(self, symbol: str, name: str = "Winning AI", seed: int | None = None):
        super().__init__(symbol, name)
        self._rng = random.Random(seed)

    def choose_move(self, board: Board) -> Move:
        winning = _first_winning_move(board, self.symbol)
        if winning is not None:
            return winning
        return self._rng.choice(legal_moves(board))


class WinningAndBlockingPlayer(WinningPlayer):
    def __init__(
        self, symbol: str, name: str = "Blocking AI", seed: int | None = None
    ):
        super().__init__(symbol, name, seed)

    def choose_move(self, board: Board) -> Move:
        winning = _first_winning_move(board, self.symbol)
        if winning is not None:
            return winning
        blocking = _first_winning_move(board, _opponent(self.symbol))
        if blocking is not None:
            return blocking
        return self._rng.choice(legal_moves(board))


class MinimaxPlayer(Player):
    """Perfect player: minimax search with memoised scores, X's view (+10/-10/0)."""

    def __init__(self, symbol: str, name: str = "Minimax AI"):
        super().__init__(symbol, name)
        self._cache: dict[tuple[str, str], int] = {}

    def choose_move(self, board: Board) -> Move:
        opponent = _opponent(self.symbol)
        scored = [
            (self._score(make_move(board, move, self.symbol), opponent), move)
            for move in legal_moves(board)
        ]
        if self.symbol == "X":
            best = max(score for score, _ in scored)
        else:
            best = min(score for score, _ in scored)
        return next(move for score, move in scored if score == best)

    def _score(self, board: Board, current_player: str) -> int:
        key = (self._cache_key(board), current_player)
        if key in self._cache:
            return self._cache[key]

        winner = get_winner(board)
        if winner == "X":
            score = MAX_SCORE
        elif winner == "O":
            score = -MAX_SCORE
        elif is_board_full(board):
            score = 0
        else:
            opponent = _opponent(current_player)
            child_scores = [
                self._score(make_move(board, move, current_player), opponent)
                for move in legal_moves(board)
            ]
            score = max(child_scores) if current_player == "X" else min(child_scores)

        self._cache[key] = score
        return score

    @staticmethod
    def _cache_key(board: Board) -> str:
        return "".join(cell if cell is not None else "." for row in board for cell in row)


def create_player(kind: str, symbol: str, seed: int | None = None) -> Player:
    if kind == "human":
        return HumanPlayer(symbol, "Human")
    if kind == "random":
        return RandomPlayer(symbol, "Random AI", seed)
    if kind == "winning":
        return WinningPlayer(symbol, "Winning AI", seed)
    if kind == "blocking":
        return WinningAndBlockingPlayer(symbol, "Blocking AI", seed)
    if kind == "minimax":
        return MinimaxPlayer(symbol, "Minimax AI")
    raise ValueError(f"Unknown player type: {kind!r}")


def _opponent(symbol: str) -> str:
    return "O" if symbol == "X" else "X"


def _first_winning_move(board: Board, player: str) -> Move | None:
    for move in legal_moves(board):
        if get_winner(make_move(board, move, player)) == player:
            return move
    return None
