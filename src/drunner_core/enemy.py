# src/drunner_core/enemy.py

from __future__ import annotations

from dataclasses import dataclass

from drunner_core.level import Level


@dataclass(slots=True)
class Enemy:
    '''
    Basic tile-based enemy with patrol movement.

    Moves one tile every move_interval seconds. If blocked, reverses direction.
    '''
    x: int
    y: int
    dx: int = 1
    dy: int = 0
    move_interval: float = 0.35
    _accum: float = 0.0

    def update(self, dt: float, level: Level) -> None:
        '''
        Per-frame update. Advances movement on a timer.
        '''
        self._accum += float(dt)
        if self._accum < self.move_interval:
            return

        # keep leftover time so movement is stable across varying frame times
        self._accum -= self.move_interval

        nx, ny = self.x + self.dx, self.y + self.dy
        if not level.is_walkable(nx, ny):
            # reverse and try once
            self.dx, self.dy = -self.dx, -self.dy
            nx, ny = self.x + self.dx, self.y + self.dy

        if level.is_walkable(nx, ny):
            self.x, self.y = nx, ny
