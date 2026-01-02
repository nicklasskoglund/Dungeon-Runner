# src/drunner_core/level.py

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import IntEnum


class LevelValidationError(ValueError):
    """
    Raised when a level grid is invalid (non-rectangular, empty, bad tile values).
    """


class Tile(IntEnum):
    """
    Tile types used by the game.

    Keep these stable because they will be referenced by JSON in level_io later.
    """

    FLOOR = 0
    WALL = 1
    START = 2
    EXIT = 3


WALKABLE_TILES: set[Tile] = {Tile.FLOOR, Tile.START, Tile.EXIT}


@dataclass(slots=True)
class Level:
    """
    Represents a single level as a rectangular grid of tiles.

    Coordinates:
      - (x, y) where x increases to the right and y increases downward.
      - (0, 0) is the top-left tile.
    """

    tiles: list[list[Tile]]
    name: str = "unnamed"
    enemies: list[tuple[int, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate that tiles are a non-empty rectangular grid of Tile values.
        """
        if not self.tiles or not self.tiles[0]:
            raise LevelValidationError("Level grid is empty.")

        width = len(self.tiles[0])
        for y, row in enumerate(self.tiles):
            if len(row) != width:
                raise LevelValidationError(
                    f"Non-rectangular grid: row 0 width={width}, row {y} width={len(row)}"
                )
            for x, t in enumerate(row):
                if not isinstance(t, Tile):
                    raise LevelValidationError(f"Invalid tile at ({x},{y}): {t!r}")

        for ex, ey in self.enemies:
            if not self.in_bounds(ex, ey):
                raise LevelValidationError(f"Enemy out of bounds: ({ex},{ey})")
            if not self.is_walkable(ex, ey):
                raise LevelValidationError(f"Enemy on non-walkable tile at ({ex},{ey})")
            if self.tile_at(ex, ey) == Tile.START:
                raise LevelValidationError("Enemy cannot spawn on START tile")

    @property
    def width(self) -> int:
        """
        Number of columns in the grid.
        """
        return len(self.tiles[0])

    @property
    def height(self) -> int:
        """
        Number of rows in the grid.
        """
        return len(self.tiles)

    def in_bounds(self, x: int, y: int) -> bool:
        """
        Return True if (x, y) is inside the grid.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, x: int, y: int) -> Tile:
        """
        Get tile at (x, y). Raises if out of bounds.
        """
        if not self.in_bounds(x, y):
            raise IndexError(f"Out of bounds: ({x},{y})")
        return self.tiles[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        """
        Return True if the tile at (x, y) can be entered by the player.
        """
        if not self.in_bounds(x, y):
            return False
        return self.tiles[y][x] in WALKABLE_TILES

    def positions_of(self, tile: Tile) -> Iterable[tuple[int, int]]:
        """
        Yield all (x, y) positions matching a given tile type.
        """
        for y, row in enumerate(self.tiles):
            for x, t in enumerate(row):
                if t == tile:
                    yield (x, y)

    def find_first(self, tile: Tile) -> tuple[int, int] | None:
        """
        Return first (x, y) position of tile, or None if not found.
        """
        for pos in self.positions_of(tile):
            return pos
        return None

    def iter_tiles(self) -> Iterable[tuple[int, int, Tile]]:
        """
        Iterate over all tiles as (x, y, tile). Useful for rendering later.
        """
        for y, row in enumerate(self.tiles):
            for x, t in enumerate(row):
                yield (x, y, t)

    @classmethod
    def from_rows(
        cls,
        rows: Sequence[Sequence[int | Tile]],
        name: str = "unnamed",
        enemies: Sequence[Sequence[int]] | None = None,
    ) -> Level:
        """
        Build a Level from numeric rows (or Tiles).

        This will be used by JSON loader later (level_io).
        """
        tiles: list[list[Tile]] = []
        for row in rows:
            converted: list[Tile] = []
            for v in row:
                converted.append(v if isinstance(v, Tile) else Tile(int(v)))
            tiles.append(converted)
        enemy_list: list[tuple[int, int]] = []
        if enemies:
            for e in enemies:
                enemy_list.append((int(e[0]), int(e[1])))

        return cls(tiles=tiles, name=name, enemies=enemy_list)

    @classmethod
    def from_ascii(cls, lines: Sequence[str], name: str = "ascii") -> Level:
        """
        Convenience constructor for quick testing.

        Legend:
          '.' = FLOOR
          '#' = WALL
          'S' = START
          'E' = EXIT
        """
        legend = {
            ".": Tile.FLOOR,
            "#": Tile.WALL,
            "S": Tile.START,
            "E": Tile.EXIT,
        }

        tiles: list[list[Tile]] = []
        for y, line in enumerate(lines):
            line = line.rstrip("\n")
            if not line:
                continue
            row: list[Tile] = []
            for x, ch in enumerate(line):
                if ch not in legend:
                    raise LevelValidationError(f"Unknown char '{ch}' at ({x},{y})")
                row.append(legend[ch])
            tiles.append(row)

        return cls(tiles=tiles, name=name)
