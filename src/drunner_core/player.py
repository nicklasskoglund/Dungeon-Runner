# src/drunner_core/player.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Player:
    """
    Player position in tile coordinates (x, y).
    """

    x: int
    y: int
