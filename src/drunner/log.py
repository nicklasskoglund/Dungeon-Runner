# src/drunner/log.py

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

from drunner.config import AppConfig


def _level(level_name: str, default: int) -> int:
    try:
        return int(getattr(logging, level_name.upper()))
    except Exception:
        return default
    
    
def configure_logging(cfg: AppConfig) -> Logger:
    logger = logging.getLogger('drunner')
    logger.setLevel(logging.DEBUG)      # handlers styr vad som faktiskt skrivs
    
    # undvik dubbla handlers om configure_logging körs flera gånger
    if logger.handlers:
        return logger
    
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # console
    ch = logging.StreamHandler()
    ch.setLevel(_level(cfg.console_level, logging.INFO))
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    
    # file
    _ensure_parent(cfg.log_file)
    fh = logging.FileHandler(cfg.log_file, encoding='utf-8')
    fh.setLevel(_level(cfg.file_level, logging.DEBUG))
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    
    logger.debug('Logger configured. file=%s', cfg.log_file)
    return logger


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)