# src/drunner/cli.py

from __future__ import annotations

import argparse

from drunner.main import run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="drunner", description="Dungeon Runner (v1)")
    sub = p.add_subparsers(dest="cmd", required=True)

    play = sub.add_parser("play", help="Start the game")
    play.add_argument(
        "--level",
        default=None,
        help="Path to a level JSON file (relative to levels/). Ignored when --generate is used.",
    )

    # NEW: generator flags
    play.add_argument(
        "--generate",
        action="store_true",
        help="Generate a level (seeded) instead of loading a file",
    )
    play.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for generator (int). If omitted, uses current time.",
    )
    play.add_argument(
        "--width", type=int, default=None, help="Generated level width in tiles (default: 41)"
    )
    play.add_argument(
        "--height", type=int, default=None, help="Generated level height in tiles (default: 31)"
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "play":
        generate_mode = args.generate or (
            args.level is None
            and (args.seed is not None or args.width is not None or args.height is not None)
        )

        if generate_mode:
            if args.width is not None and args.width < 15:
                raise SystemExit("--width must be >= 15 for --generate")
            if args.height is not None and args.height < 11:
                raise SystemExit("--height must be >= 11 for --generate")

        return run(
            level=args.level,
            generate=generate_mode,
            seed=args.seed,
            width=args.width,
            height=args.height,
        )

    return 2
