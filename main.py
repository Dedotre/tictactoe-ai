"""Command-line entry point for the Tic-Tac-Toe game."""

from __future__ import annotations

import argparse

from game import play_game
from players import PLAYER_TYPES, Player, create_player


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    if args.simulate is not None:
        _print_simulation(
            args.simulate,
            args.x or "random",
            args.o or "random",
            args.seed,
        )
        return

    x_player = create_player(args.x or "human", "X", args.seed)
    o_player = create_player(args.o or "human", "O", _offset_seed(args.seed, 1))
    _play_until_quit(x_player, o_player)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Tic-Tac-Toe in your terminal.")
    parser.add_argument(
        "--x", choices=PLAYER_TYPES, help="who plays X (default: human)"
    )
    parser.add_argument(
        "--o", choices=PLAYER_TYPES, help="who plays O (default: human)"
    )
    parser.add_argument(
        "--simulate",
        type=int,
        metavar="N",
        help="play N games between the chosen AIs and print the statistics",
    )
    parser.add_argument(
        "--seed", type=int, help="seed the AIs' random moves for reproducible games"
    )
    args = parser.parse_args(argv)

    if args.simulate is not None:
        if args.simulate < 1:
            parser.error("--simulate must be at least 1")
        if "human" in (args.x or "random", args.o or "random"):
            parser.error("--simulate needs two AI players, not 'human'")
    return args


def _play_until_quit(x_player: Player, o_player: Player) -> None:
    while True:
        try:
            play_game(x_player, o_player)
        except EOFError:
            print()
            return
        try:
            again = input("\nPlay again? (y/n): ").strip().lower()
        except EOFError:
            print()
            return
        if again not in ("y", "yes"):
            print("Thanks for playing!")
            return


def _print_simulation(games: int, x_name: str, o_name: str, seed: int | None) -> None:
    x_player = create_player(x_name, "X", seed)
    o_player = create_player(o_name, "O", _offset_seed(seed, 1))
    results: dict[str | None, int] = {"X": 0, "O": 0, None: 0}
    for _ in range(games):
        results[play_game(x_player, o_player, display=False)] += 1

    print(f"Played {games:,} games: {x_name} (X) vs {o_name} (O)")
    print(f"  X wins: {results['X']:,} ({_percent(results['X'], games)})")
    print(f"  O wins: {results['O']:,} ({_percent(results['O'], games)})")
    print(f"  Draws:  {results[None]:,} ({_percent(results[None], games)})")


def _offset_seed(seed: int | None, offset: int) -> int | None:
    return None if seed is None else seed + offset


def _percent(count: int, total: int) -> str:
    return f"{100 * count / total:.1f}%"


if __name__ == "__main__":
    main()
