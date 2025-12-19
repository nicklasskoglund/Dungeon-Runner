# src/drunner_core/movement.py

from __future__ import annotations

from drunner_core.level import Level
from drunner_core.player import Player


def try_move(level: Level, player: Player, dx: int, dy: int) -> bool:
    """
    Attempt to move player by (dx,dy). Returns True if moved.
    """
    nx = player.x + dx
    ny = player.y + dy

    if not level.is_walkable(nx, ny):
        return False

    player.x = nx
    player.y = ny
    return True
