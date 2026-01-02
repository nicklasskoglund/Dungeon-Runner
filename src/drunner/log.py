# src/drunner/log.py

"""
Logging setup for drunner.

Creates a logger with console and file handlers, based on the application's
configuration.
"""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

from drunner.config import AppConfig


def _level(level_name: str, default: int) -> int:
    """
    Convert a log level name (e.g., 'INFO') into a logging level integer.

    Args:
        level_name: Log level name from config (case-insensitive).
        default: Fallback level if the name is invalid.

    Returns:
        int: A logging level constant (e.g., logging.INFO).
    """
    try:
        return int(getattr(logging, level_name.upper()))
    except Exception:
        # If config contains an unknown level name, use a safe default.
        return default


def configure_logging(cfg: AppConfig) -> Logger:
    """
    Configure and return the application's logger.

    Adds:
      - Console handler (level from cfg.console_level)
      - File handler (level from cfg.file_level, writing to cfg.log_file)

    Args:
        cfg: Application config.

    Returns:
        Logger: Configured logger instance.
    """
    logger = logging.getLogger("drunner")
    logger.setLevel(logging.DEBUG)  # Handlers decide what actually gets emitted.

    # Avoid duplicate handlers if this is called more than once.
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console output
    ch = logging.StreamHandler()
    ch.setLevel(_level(cfg.console_level, logging.INFO))
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File output
    _ensure_parent(cfg.log_file)  # Make sure the log directory exists.
    fh = logging.FileHandler(cfg.log_file, encoding="utf-8")
    fh.setLevel(_level(cfg.file_level, logging.DEBUG))
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.debug("Logger configured. file=%s", cfg.log_file)
    return logger


def _ensure_parent(p: Path) -> None:
    """
    Ensure the parent directory for a file path exists.

    Args:
        p: File path whose parent directory should be created if missing.
    """
    p.parent.mkdir(parents=True, exist_ok=True)
