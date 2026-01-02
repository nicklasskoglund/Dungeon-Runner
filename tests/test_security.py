# tests/test_security.py

from pathlib import Path

import pytest

from drunner.security import (
    SecurityError,
    require_suffix,
    safe_join,
    safe_resolve,
    validate_level_name,
    validate_seed,
)


def test_safe_resolve_allows_child_path(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    p = safe_resolve(base, "levels/level1.json")

    assert p.is_absolute()
    assert base.resolve() in p.parents
    assert p.name == "level1.json"


def test_safe_resolve_allows_base_itself(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    p = safe_resolve(base, ".")
    assert p == base.resolve()


def test_safe_resolve_blocks_traversal(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    with pytest.raises(SecurityError):
        safe_resolve(base, "../evil.txt")


def test_require_suffix_case_insensitive(tmp_path: Path) -> None:
    p = tmp_path / "config.TOML"
    assert require_suffix(p, ".toml") == p


def test_require_suffix_raises_on_mismatch(tmp_path: Path) -> None:
    p = tmp_path / "level.json"
    with pytest.raises(SecurityError):
        require_suffix(p, ".toml")


def test_safe_join_allows_child_path(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    p = safe_join(base, "level1.json")

    assert p.is_absolute()
    assert p.parent == base.resolve()
    assert p.name == "level1.json"


def test_safe_join_blocks_traversal(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir()

    with pytest.raises(SecurityError):
        safe_join(base, "../evil.json")


def test_validate_level_name_ok() -> None:
    assert validate_level_name("level1") == "level1"
    assert validate_level_name("boss-level.json") == "boss-level.json"
    assert validate_level_name("level_01") == "level_01"


@pytest.mark.parametrize("bad", ["../x", "a/b", r"a\b", "..", ".hidden", "a.json.bak", ""])
def test_validate_level_name_rejects(bad: str) -> None:
    with pytest.raises(SecurityError):
        validate_level_name(bad)


def test_validate_seed_allows_none() -> None:
    assert validate_seed(None) is None


def test_validate_seed_valid() -> None:
    assert validate_seed("123") == 123


def test_validate_seed_rejects_out_of_range() -> None:
    with pytest.raises(SecurityError):
        validate_seed(-1)


def test_validate_seed_allows_max() -> None:
    assert validate_seed(2**32 - 1) == 2**32 - 1


def test_validate_seed_rejects_too_large() -> None:
    with pytest.raises(SecurityError):
        validate_seed(2**32)
