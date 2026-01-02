# src/drunner_core/game_players.py

from __future__ import annotations

from drunner_core.level import Level, Tile


def find_spawn(level: Level) -> tuple[int, int]:
    """
    Find player spawn position. Prefer START tile, fallback to (0,0).
    """
    for x, y, tile in level.iter_tiles():
        if tile == Tile.START:
            return x, y

    return (0, 0)
