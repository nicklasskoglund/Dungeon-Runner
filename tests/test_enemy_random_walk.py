# tests/test_enemy_random_walk.py

import random

from drunner_core.enemy import Enemy
from drunner_core.level import Level


def test_enemy_random_walk_moves_in_both_axes():
    level = Level.from_ascii(
        [
            '#######',
            '#.....#',
            '#.....#',
            '#..S..#',
            '#.....#',
            '#..E..#',
            '#######',
        ],
        name='test',
    )

    e = Enemy(
        x=2,
        y=2,
        move_interval=0.0,                 # move every update call
        direction_change_chance=1.0,       # always pick new direction
        rng=random.Random(123),            # deterministic test
    )

    deltas: set[tuple[int, int]] = set()
    for _ in range(40):
        ox, oy = e.x, e.y
        e.update(1.0, level)
        deltas.add((e.x - ox, e.y - oy))

    assert any(dx != 0 and dy == 0 for dx, dy in deltas)  # horizontal happened
    assert any(dx == 0 and dy != 0 for dx, dy in deltas)  # vertical happened
