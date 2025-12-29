# tests/test_level_io.py

import json
from pathlib import Path

import pytest

from drunner_core.level import Level, Tile
from drunner_core.level_io import LevelIOError, load_level, save_level


def _valid_grid() -> list[list[int]]:
    return [
        [1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 3, 1],
        [1, 1, 1, 1, 1],
    ]


def test_load_level_success(tmp_path: Path) -> None:
    path = tmp_path / 'demo.json'
    payload = {'version': 1, 'name': 'demo', 'grid': _valid_grid()}
    path.write_text(json.dumps(payload), encoding='utf-8')

    level = load_level(path)

    assert level.name == 'demo'
    assert len(list(level.positions_of(Tile.START))) == 1
    assert len(list(level.positions_of(Tile.EXIT))) == 1


def test_save_then_load_roundtrip(tmp_path: Path) -> None:
    grid = _valid_grid()
    level = Level.from_rows(grid, name='roundtrip')

    path = tmp_path / 'roundtrip.json'
    save_level(level, path)
    assert path.exists()

    loaded = load_level(path)
    assert loaded.name == 'roundtrip'

    loaded_grid = [[int(t) for t in row] for row in loaded.tiles]
    assert loaded_grid == grid


def test_load_level_raises_on_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / 'missing.json'
    with pytest.raises(FileNotFoundError):
        load_level(missing)


def test_load_level_raises_on_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / 'bad.json'
    path.write_text('{not valid json', encoding='utf-8')

    with pytest.raises(LevelIOError):
        load_level(path)


def test_load_level_raises_on_unsupported_version(tmp_path: Path) -> None:
    path = tmp_path / 'v2.json'
    payload = {'version': 2, 'name': 'v2', 'grid': _valid_grid()}
    path.write_text(json.dumps(payload), encoding='utf-8')

    with pytest.raises(LevelIOError):
        load_level(path)


def test_load_level_raises_on_missing_start(tmp_path: Path) -> None:
    grid = _valid_grid()
    grid[1][1] = 0

    path = tmp_path / 'no_start.json'
    payload = {'version': 1, 'name': 'no_start', 'grid': grid}
    path.write_text(json.dumps(payload), encoding='utf-8')

    with pytest.raises(LevelIOError):
        load_level(path)


def test_load_level_raises_on_multiple_exits(tmp_path: Path) -> None:
    grid = _valid_grid()
    grid[1][2] = 3

    path = tmp_path / 'two_exits.json'
    payload = {'version': 1, 'name': 'two_exits', 'grid': grid}
    path.write_text(json.dumps(payload), encoding='utf-8')

    with pytest.raises(LevelIOError):
        load_level(path)
