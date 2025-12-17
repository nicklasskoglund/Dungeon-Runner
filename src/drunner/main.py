# src/drunner/main.py

'''
Application entry points for drunner.

This module wires together configuration + logging and starts the game loop.
'''

from __future__ import annotations

from drunner.config import load_config
from drunner.log import configure_logging
from drunner_core.game import run_game


def run(level: str | None = None) -> int:
    '''
    Start the game with application configuration and logging.

    Args:
        level: Optional level identifier/path. Currently not used by the game loop,
               but kept for future support.

    Returns:
        int: Process exit code (0 = success).
    '''
    cfg = load_config()
    logger = configure_logging(cfg)
    
    logger.info('Starting Dungeon Runner')
    logger.debug('Config root=%s', cfg.root_dir)
    
    # NOTE: `level` is not used yet, but CLI can already pass it in.
    run_game(cfg, logger)
    
    logger.info('Exiting Dungeon Runner')
    return 0