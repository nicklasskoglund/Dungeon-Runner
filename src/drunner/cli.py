# src/drunner/cli.py

'''
Command-line interface (CLI) for the drunner package.

This module defines available CLI commands and dispatches them to the
application entry points.
'''

from __future__ import annotations

import argparse

from drunner.main import run


def build_parser() -> argparse.ArgumentParser:
    '''
    Create and return the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: Configured parser with subcommands.
    '''
    p = argparse.ArgumentParser(prog='drunner', description='Dungeon Runner (v1)')
    # Subcommands: `drunner play ...`
    sub = p.add_subparsers(dest='cmd', required=True)
    
    play = sub.add_parser('play', help='Start the game')
    # Optional level path/name (currently forwarded to run()).
    play.add_argument('--level', default=None, help='Level file (week2)')
    
    return p


def main(argv: list[str] | None = None) -> int:
    '''
    CLI entry point.

    Args:
        argv: Optional list of arguments (useful for testing). If None, argparse
              reads from sys.argv.

    Returns:
        int: Process exit code (0 = success).
    '''
    args = build_parser().parse_args(argv)
    
    if args.cmd == 'play':
        return run(level=args.level)
    
    # Should not happen because subcommands are required, but keep a safe fallback.
    return 2