# src/drunner_core/enemy.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Enemy:
    x: int
    y: int
    dx: int = 1
    dy: int = 0
    move_interval: float = 0.35
    _timer: float = 0.0

    def update(self, dt: float, level) -> None:
        '''
        Update enemy movement (tile-based patrol).

        level must expose a 'is_walkable(x, y) -> bool' or similar.
        '''
        self._timer += dt
        if self._timer < self.move_interval:
            return

        # consume one step
        self._timer = 0.0

        nx, ny = self.x + self.dx, self.y + self.dy
        if level.is_walkable(nx, ny):
            self.x, self.y = nx, ny
            return

        # blocked -> reverse direction and try once
        self.dx, self.dy = -self.dx, -self.dy
        nx, ny = self.x + self.dx, self.y + self.dy
        if level.is_walkable(nx, ny):
            self.x, self.y = nx, ny
