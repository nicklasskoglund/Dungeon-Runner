# src/drunner_core/enemy.py

from __future__ import annotations

import random
from dataclasses import dataclass, field

from drunner_core.level import Level

DIRECTIONS_4: tuple[tuple[int, int], ...] = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
)


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
        if self.move_interval <= 0:
            self._step(level)
            return

        self._accum += float(dt)

        # Allow multiple steps if dt is large (e.g., window lag/focus loss),
        # while still keeping deterministic step size.
        while self._accum >= self.move_interval:
            self._accum -= self.move_interval
            self._step(level)

    def _step(self, level: Level) -> None:
        """
        Execute a single tile step according to the current direction and RNG.
        """
        nx, ny = self.x + self.dx, self.y + self.dy

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
        directions = list(DIRECTIONS_4)
        self.rng.shuffle(directions)

        for dx, dy in directions:
            if level.is_walkable(self.x + dx, self.y + dy):
                return dx, dy

        return (0, 0)
