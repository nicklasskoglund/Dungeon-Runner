# src/drunner/main.py

from __future__ import annotations

from drunner.config import load_config
from drunner.log import configure_logging
from drunner_core.game import run_game


def run(level: str | None = None) -> int:
    cfg = load_config()
    logger = configure_logging(cfg)
    
    logger.info('Starting Dungeon Runner')
    logger.debug('Config root=%s', cfg.root_dir)
    
    # Week 1: level används inte ännu i game-loop, men vi tar in parametern
    run_game(cfg, logger)
    logger.info('Exiting Dungeon Runner')
    return 0