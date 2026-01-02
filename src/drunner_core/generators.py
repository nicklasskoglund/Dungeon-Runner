# src/drunner_core/generators.py

from __future__ import annotations

import random
from dataclasses import dataclass

from drunner_core.level import Level, Tile


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: Rect, pad: int = 1) -> bool:
        return not (
            self.x + self.w + pad <= other.x
            or other.x + other.w + pad <= self.x
            or self.y + self.h + pad <= other.y
            or other.y + other.h + pad <= self.y
        )


def generate_level(seed: int, width: int, height: int) -> Level:
    """
    Generate a deterministic rooms + corridors dungeon.

    Contract:
      - Same seed + same dimensions => same grid
      - Exactly 1 START tile and exactly 1 EXIT tile
      - Returns drunner_core.level.Level (compatible with level_io v1)
    """
    _validate_dimensions(width, height)

    rng = random.Random(seed)

    # Work on integer grid first (matches level_io schema), convert via Level.from_rows at end.
    WALL = int(Tile.WALL)
    FLOOR = int(Tile.FLOOR)
    START = int(Tile.START)
    EXIT = int(Tile.EXIT)

    grid: list[list[int]] = [[WALL for _ in range(width)] for _ in range(height)]

    rooms: list[Rect] = []
    room_attempts = 80
    min_size = 4
    max_size = 10

    for _ in range(room_attempts):
        w = rng.randint(min_size, min(max_size, width - 3))
        h = rng.randint(min_size, min(max_size, height - 3))
        x = rng.randint(1, width - w - 2)
        y = rng.randint(1, height - h - 2)
        candidate = Rect(x, y, w, h)

        if any(candidate.intersects(r, pad=1) for r in rooms):
            continue

        _carve_room(grid, candidate, FLOOR)
        rooms.append(candidate)

    if not rooms:
        # Deterministic fallback: single corridor in the middle.
        _carve_fallback(grid, FLOOR)

        # Place start/exit deterministically on that corridor
        sy = height // 2
        start = (2, sy)
        exit_ = (width - 3, sy)
    else:
        # Stable connection order for determinism
        rooms_sorted = sorted(rooms, key=lambda r: (r.center()[0], r.center()[1]))

        for a, b in zip(rooms_sorted, rooms_sorted[1:]):
            _carve_corridor(grid, a.center(), b.center(), FLOOR, rng)

        start = rooms_sorted[0].center()
        exit_ = rooms_sorted[-1].center()

    # Ensure walkable tiles under start/exit and then stamp unique START/EXIT
    sx, sy = start
    ex, ey = exit_
    grid[sy][sx] = START
    grid[ey][ex] = EXIT

    # Final conversion to Level (validates tiles etc.)
    level = Level.from_rows(
        grid,
        name=f"generated_seed_{seed}",
        enemies=[],
    )
    return level


def _validate_dimensions(width: int, height: int) -> None:
    # Rooms+corridors needs some space, keep this simple and explicit.
    if width < 15 or height < 11:
        raise ValueError("width/height too small for rooms+corridors generator (min 15x11).")


def _carve_room(grid: list[list[int]], r: Rect, floor: int) -> None:
    for y in range(r.y, r.y + r.h):
        for x in range(r.x, r.x + r.w):
            grid[y][x] = floor


def _carve_corridor(
    grid: list[list[int]],
    a: tuple[int, int],
    b: tuple[int, int],
    floor: int,
    rng: random.Random,
) -> None:
    ax, ay = a
    bx, by = b

    # Randomize L-turn direction, but via rng for determinism.
    if rng.random() < 0.5:
        _carve_h(grid, ax, bx, ay, floor)
        _carve_v(grid, ay, by, bx, floor)
    else:
        _carve_v(grid, ay, by, ax, floor)
        _carve_h(grid, ax, bx, by, floor)


def _carve_h(grid: list[list[int]], x1: int, x2: int, y: int, floor: int) -> None:
    if x2 < x1:
        x1, x2 = x2, x1
    for x in range(x1, x2 + 1):
        grid[y][x] = floor


def _carve_v(grid: list[list[int]], y1: int, y2: int, x: int, floor: int) -> None:
    if y2 < y1:
        y1, y2 = y2, y1
    for y in range(y1, y2 + 1):
        grid[y][x] = floor


def _carve_fallback(grid: list[list[int]], floor: int) -> None:
    h = len(grid)
    w = len(grid[0])
    y = h // 2
    for x in range(1, w - 1):
        grid[y][x] = floor
