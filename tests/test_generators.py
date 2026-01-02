# tests/test_generators.py

import hashlib

from drunner_core.generators import generate_level
from drunner_core.level import Tile


def _sig(level) -> str:
    blob = "\n".join("".join(str(int(t)) for t in row) for row in level.tiles).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def test_same_seed_same_signature():
    a = generate_level(seed=123, width=41, height=31)
    b = generate_level(seed=123, width=41, height=31)
    assert _sig(a) == _sig(b)


def test_has_exactly_one_start_and_one_exit():
    lvl = generate_level(seed=999, width=41, height=31)
    starts = list(lvl.positions_of(Tile.START))
    exits = list(lvl.positions_of(Tile.EXIT))
    assert len(starts) == 1
    assert len(exits) == 1
    assert starts[0] != exits[0]
