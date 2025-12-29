# src/drunner_core/state.py

from __future__ import annotations

from enum import Enum, auto


class GameState(Enum):
    RUNNING = auto()
    WON = auto()
    LOST = auto()