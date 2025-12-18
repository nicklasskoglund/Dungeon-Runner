# src/drunner/main.py

'''
Application entry points for drunner.

This module wires together configuration + logging and starts the game loop.
'''

from __future__ import annotations

import sys
from pathlib import Path

from drunner.config import load_config
from drunner.log import configure_logging
from drunner.security import SecurityError, require_suffix, safe_resolve
from drunner_core.game import run_game
from drunner_core.level_io import LevelIOError


def run(level: str | None = None) -> int:
    '''
    Start the game with application configuration and logging.

    Args:
        level: Optional level identifier/path.

    Returns:
        int: Process exit code (0 = success).
    '''
    cfg = load_config()
    logger = configure_logging(cfg)

    logger.info('Starting Dungeon Runner')
    logger.debug('Config root=%s', cfg.root_dir)
    
    try:
        level_path: Path | None = None
        if level:
            p = safe_resolve(cfg.levels_dir, level)
            require_suffix(p, '.json')
            level_path = p
            
        run_game(cfg, logger, level_path=level_path)
        
        logger.info('Exiting Dungeon Runner')
        return 0
    
    except (FileNotFoundError, SecurityError, LevelIOError) as e:
        logger.error('%s', e)
        print(f'ERROR: {e}', file=sys.stderr)
        print(f'See log file: {cfg.log_file}', file=sys.stderr)
        return 2
    
    except Exception:
        logger.exception('Unhandled exception')
        print('ERROR: Unexpected crash.', file=sys.stderr)
        print(f'See log file: {cfg.log_file}', file=sys.stderr)
        return 1