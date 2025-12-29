# src/drunner_core/player.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    x: int
    y: int