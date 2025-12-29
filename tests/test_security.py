# tests/test_security.py

from pathlib import Path

import pytest

from drunner.security import SecurityError, require_suffix, safe_resolve


def test_safe_resolve_allows_child_path(tmp_path: Path) -> None:
    base = tmp_path / 'base'
    base.mkdir()

    p = safe_resolve(base, 'levels/level1.json')

    assert p.is_absolute()
    assert base.resolve() in p.parents
    assert p.name == 'level1.json'


def test_safe_resolve_allows_base_itself(tmp_path: Path) -> None:
    base = tmp_path / 'base'
    base.mkdir()

    p = safe_resolve(base, '.')
    assert p == base.resolve()


def test_safe_resolve_blocks_traversal(tmp_path: Path) -> None:
    base = tmp_path / 'base'
    base.mkdir()

    with pytest.raises(SecurityError):
        safe_resolve(base, '../evil.txt')


def test_require_suffix_case_insensitive(tmp_path: Path) -> None:
    p = tmp_path / 'config.TOML'
    assert require_suffix(p, '.toml') == p


def test_require_suffix_raises_on_mismatch(tmp_path: Path) -> None:
    p = tmp_path / 'level.json'
    with pytest.raises(SecurityError):
        require_suffix(p, '.toml')
