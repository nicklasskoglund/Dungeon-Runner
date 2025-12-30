# src/drunner/cli.py

from __future__ import annotations

import argparse

from drunner.main import run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='drunner', description='Dungeon Runner (v1)')
    sub = p.add_subparsers(dest='cmd', required=True)

    play = sub.add_parser('play', help='Start the game')
    play.add_argument('--level', default=None, help='Level file (week2)')

    # NEW: generator flags
    play.add_argument('--generate', action='store_true', help='Generate a level (seeded) instead of loading a file')
    play.add_argument('--seed', type=int, default=None, help='Seed for generator (int). If omitted, uses current time.')
    play.add_argument('--width', type=int, default=None, help='Generated level width (tiles)')
    play.add_argument('--height', type=int, default=None, help='Generated level height (tiles)')

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == 'play':
        generate_mode = args.generate or (args.seed is not None and args.level is None)

        return run(
            level=args.level,
            generate=generate_mode,
            seed=args.seed,
            width=args.width,
            height=args.height,
        )

    return 2
