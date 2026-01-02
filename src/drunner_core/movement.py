# src/drunner_core/movement.py

from __future__ import annotations

from drunner_core.level import Level
from drunner_core.player import Player


def try_move(level: Level, player: Player, dx: int, dy: int) -> bool:
    """
    Try to move the player by one tile step (dx, dy).

    Returns:
        True if the target tile is walkable and the player position was updated,
        otherwise False.

    Notes:
        This function relies on Level.is_walkable() to enforce bounds and walls.
    """
    if dx == 0 and dy == 0:
        return False

    target_x = player.x + dx
    target_y = player.y + dy

    if level.is_walkable(target_x, target_y):
        player.x = target_x
        player.y = target_y
        return True

    return False
