# src/drunner_core/level_io.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from drunner_core.level import Level, LevelValidationError, Tile


class LevelIOError(ValueError):
    '''
    Raised when a level file cannot be parsed or does not match the expected schema.
    '''
    
    
def load_level(path: Path) -> Level:
    '''
    Load a level from a JSON file.

    Expected schema (v1):
      {
        'version': 1,
        'name': 'demo',
        'grid': [[1,1,1,...], [1,2,0,...], ...]
      }

    Tile encoding must match Tile enum integers.
    '''
    if not path.exists():
        raise FileNotFoundError(f'Level file not found: {path}')
    
    try:
        raw = path.read_text(encoding='utf-8')
        data: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as e:
        raise LevelIOError(f'Invalid JSON in {path}: {e}') from e
    
    version = int(data.get('version', 1))
    if version != 1:
        raise LevelIOError(f'Unsupported level version in {path}: {version}')
    
    name = str(data.get('name', path.stem))
    grid = data.get('grid')
    
    if not isinstance(grid, list) or not grid or not all(isinstance(r, list) for r in grid):
        raise LevelIOError(f'Invalid or missing "grid" in {path}. Expected 2D list.')
    
    try:
        level = Level.from_rows(grid, name=name)
    except (ValueError, LevelValidationError) as e:
        raise LevelIOError(f'Invalid grid data in {path}: {e}') from e
    
    _validate_required_tiles(level, path)
    return level


def save_level(level: Level, path: Path) -> None:
    '''
    Save a level to JSON.

    Produces schema v1 with integer tile values.
    '''
    payload = {
        'version': 1,
        'name': level.name,
        'grid': [[int(t) for t in row] for row in level.tiles],
    }
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    
    
def _validate_required_tiles(level: Level, source: Path) -> None:
    '''
    Enforce minimal constraints so levels are playable.
    '''
    if level.find_first(Tile.START) is None:
        raise LevelIOError(f'Level missing START tile in {source}')
    if level.find_first(Tile.EXIT) is None:
        raise LevelIOError(f'Level missing EXIT tile in {source}')