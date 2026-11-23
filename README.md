# Tic-Tac-Toe AI

A command-line Tic-Tac-Toe game in Python with human players, heuristic computer opponents, and a perfect [minimax](https://en.wikipedia.org/wiki/Minimax) AI that can never be beaten. Includes per-side AI selection, AI-vs-AI battle simulations, and a 58-test unittest suite.

Built while working through Robert Heaton's [Programming Projects for Advanced Beginners #3a](https://robertheaton.com/2018/10/09/programming-projects-for-advanced-beginners-3-a/) and [#3b](https://robertheaton.com/2018/10/09/programming-projects-for-advanced-beginners-3-b/).

## Features

- Non-mutating rules engine (`make_move` returns a new board and raises on illegal moves)
- Human, random, winning, blocking, and perfect minimax players behind one interface
- Memoised minimax: the opening move takes about 40 ms after caching 5,477 board states
- Choose a different AI for each side, watch AIs play each other, or run thousands of games for statistics
- Fully unit tested with the standard library only

## Requirements

- Python 3.10 or newer (tested on 3.14)
- No third-party packages

## Setup

```bash
git clone https://github.com/Dedotre/tictactoe-ai.git
cd tictactoe-ai
python main.py
```

That last command starts a game between two humans. On Windows you can run the same commands from PowerShell, Command Prompt, or Git Bash.

## How to play

Moves are entered as an **X co-ordinate (column)** followed by a **Y co-ordinate (row)**, each from 0 to 2. The board labels show the co-ordinates:

```
  0 1 2
  ------
0|     |
1|  X  |
2|     |
  ------
```

Here X is in the centre, at co-ordinate `1, 1`. Invalid or non-numeric input re-prompts, and so does an occupied square. After each game, type `y` to play again or `n` to quit.

## Usage examples

| Command | What it does |
| --- | --- |
| `python main.py` | Two humans play each other |
| `python main.py --o minimax` | You play X against the perfect AI (best case: a draw) |
| `python main.py --x minimax` | The perfect AI plays X against you |
| `python main.py --x minimax --o random` | Watch the perfect AI play the random AI |
| `python main.py --x winning --o blocking` | Pit two heuristic AIs against each other |
| `python main.py --simulate 1000 --x minimax --o random --seed 1` | Play 1,000 silent games and print statistics |
| `python main.py --help` | Show all options |

Available AI names for `--x` and `--o`:

| Name | Behaviour |
| --- | --- |
| `human` | You, typing co-ordinates (default) |
| `random` | Any legal move |
| `winning` | Takes an immediate win if one exists, otherwise a random move |
| `blocking` | Takes a win, else blocks the opponent's win, else a random move |
| `minimax` | Perfect play: never loses, draws against perfect play |

`--simulate N` defaults to `random` vs `random` and requires two non-human players. Add `--seed` to any command for reproducible AI games. Example output:

```
$ python main.py --simulate 1000 --x minimax --o random --seed 1
Played 1,000 games: minimax (X) vs random (O)
  X wins: 992 (99.2%)
  O wins: 0 (0.0%)
  Draws:  8 (0.8%)
```

The perfect AI never loses from either side, and two perfect AIs always draw. The heuristic AIs are much stronger than random play but can still be beaten.

## Running the tests

```bash
python -m unittest
```

58 tests cover the engine (rendering, move validation, win and draw detection, immutability), every player, the game loop, and the CLI. They also assert the minimax AI never loses against random or blocking opponents and always draws against itself.

## Project layout

| File | Responsibility |
| --- | --- |
| `tictactoe.py` | Rules engine: `new_board`, `render`, `make_move`, `get_winner`, `is_board_full`, `legal_moves` |
| `players.py` | `Player` interface, human input, heuristic AIs, minimax AI, `create_player` registry |
| `game.py` | Turn loop that alternates X and O until a win or draw |
| `main.py` | Command-line interface, player selection, battle simulations |
| `test_engine.py`, `test_players.py`, `test_game.py`, `test_ai.py`, `test_main.py` | Unit tests |

The engine knows nothing about players, and every player implements the same interface:

```python
class Player:
    def choose_move(self, board) -> tuple[int, int]:
        ...
```

The game loop only calls `choose_move`, so any new AI that follows the interface can be dropped in without touching the engine.

## How the minimax AI works

Minimax assumes both players play perfectly and picks the move whose outcome is best for the AI even under that assumption. If the AI can force a win, it takes it; if it can only draw, it draws; it never loses.

### 1. Scores

Every position gets an integer score from X's point of view:

| Result | Score |
| --- | --- |
| X wins | `+10` |
| O wins | `-10` |
| Draw | `0` |

X wants to maximise the score and O wants to minimise it, so a single score works for both sides.

### 2. Scoring non-terminal positions recursively

A position that is not finished is scored by looking at every legal move, scoring the position that results after that move, and then:

- if it is **X's turn**, return the **maximum** of those scores (X picks its best move);
- if it is **O's turn**, return the **minimum** (O picks its best move).

The terminal checks at the top of the recursion are the base case:

```python
def _score(board, current_player):
    if X has won:        return +10
    if O has won:        return -10
    if board is full:    return 0

    scores = [
        _score(make_move(board, move, current_player), opponent(current_player))
        for move in legal_moves(board)
    ]
    return max(scores) if current_player == "X" else min(scores)
```

Because `make_move` returns a new board rather than mutating the old one, the search can explore every branch without undoing moves.

### 3. Choosing a move

`MinimaxPlayer.choose_move` scores every candidate move the same way, then picks the highest score for X or the lowest score for O. Ties are broken by taking the first legal move in row-major order, which is why the AI always opens in a corner — with perfect play every opening move is equally good, so it simply picks the first.

### 4. Caching

Naive minimax walks the same positions many times, because different move orders can reach identical boards. The AI memoises each result in a dictionary, keyed by the board (serialised to a nine-character string of `X`, `O`, and `.`) plus the side to move:

```python
key = ("".join(cell if cell is not None else "." for row in board for cell in row), current_player)
```

An empty board expands to 5,477 unique (position, side-to-move) pairs, and caching cuts the opening move from seconds to about 40 ms. Without caching, the same position reached by two different move orders is scored from scratch both times; the cache lets the later branch reuse the earlier conclusion.

### Why it cannot be beaten

The AI considers every reply its opponent could make, not just likely ones, so any line where it loses is rejected. Every line that survives the search is at worst a draw. That guarantee is checked by the tests and by the simulations:

```
$ python main.py --simulate 1000 --x minimax --o random --seed 1
  O wins: 0 (0.0%)
$ python main.py --simulate 10 --x minimax --o minimax
  Draws:  10 (100.0%)
```

## Credits

The project design and milestones come from Robert Heaton's [Programming Projects for Advanced Beginners #3a: Tic-Tac-Toe](https://robertheaton.com/2018/10/09/programming-projects-for-advanced-beginners-3-a/) and [#3b: Tic-Tac-Toe AI](https://robertheaton.com/2018/10/09/programming-projects-for-advanced-beginners-3-b/).
