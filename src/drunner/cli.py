# src/drunner/cli.py

from __future__ import annotations

import argparse

from drunner.main import run


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='drunner', description='Dungeon Runner (v1)')
    sub = p.add_subparsers(dest='cmd', required=True)
    
    play = sub.add_parser('play', help='Start the game')
    play.add_argument('--level', default=None, help='Level file (week2)')
    
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    
    if args.cmd == 'play':
        return run(level=args.level)
    
    return 2