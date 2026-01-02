# src/drunner_core/enemy.py

from __future__ import annotations

import random
from dataclasses import dataclass, field

from drunner_core.level import Level


@dataclass(slots=True)
class Enemy:
    """
    Basic tile-based enemy with random-walk movement (4-way).

    Moves one tile every move_interval seconds. On each move tick it may keep
    direction, or pick a new direction; if blocked it always picks a new one.
    """

    x: int
    y: int

    # Current direction (tile step)
    dx: int = 1
    dy: int = 0

    # Movement cadence
    move_interval: float = 0.35
    _accum: float = 0.0

    # Randomness (injectable for tests / determinism)
    rng: random.Random = field(default_factory=random.Random)

    # Chance to change direction on each step even if not blocked
    direction_change_chance: float = 0.35

    def update(self, dt: float, level: Level) -> None:
        """
        Per-frame update. Advances movement on a timer.
        """
        self._accum += float(dt)
        if self._accum < self.move_interval:
            return

        # keep leftover time so movement is stable across varying frame times
        self._accum -= self.move_interval

        nx, ny = self.x + self.dx, self.y + self.dy

        # If blocked, or randomly, choose a new direction (including vertical)
        if (not level.is_walkable(nx, ny)) or (self.rng.random() < self.direction_change_chance):
            self.dx, self.dy = self._pick_direction(level)
            nx, ny = self.x + self.dx, self.y + self.dy

        if level.is_walkable(nx, ny):
            self.x, self.y = nx, ny

    def _pick_direction(self, level: Level) -> tuple[int, int]:
        """
        Pick a walkable direction among 4-neighborhood, shuffled by rng.
        Returns (0,0) if no move is possible.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.rng.shuffle(directions)

        for dx, dy in directions:
            if level.is_walkable(self.x + dx, self.y + dy):
                return dx, dy

        return (0, 0)
