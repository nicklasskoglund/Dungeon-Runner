# src/drunner/security.py

'''
Security helpers for drunner.

Provides small utilities to validate user-supplied paths and file types.
'''

from __future__ import annotations

import re
from pathlib import Path

class SecurityError(ValueError):
    '''
    Raised when a security validation fails (e.g., unsafe path or file type).
    '''
    pass


def safe_resolve(base_dir: Path, user_path: str) -> Path:
    '''
    Resolve a user-supplied path inside a base directory.

    This prevents path traversal (e.g., ../../secret) by ensuring the resolved
    path stays within base_dir.

    Args:
        base_dir: The allowed root directory.
        user_path: A path provided by the user (relative or absolute).

    Returns:
        Path: A resolved, safe path within base_dir.

    Raises:
        SecurityError: If the resolved path is outside base_dir.
    '''
    base = base_dir.resolve()
    # Resolve/normalize to collapse '..' and follow symlinks.
    candidate = (base / user_path).resolve()
    
    # Allow exactly base itself, otherwise require candidate to be a child of base.
    if base not in candidate.parents and candidate != base:
        raise SecurityError(f'Unsafe path: {user_path}')
    
    return candidate


def require_suffix(p: Path, suffix: str) -> Path:
    '''
    Require a specific file suffix (case-insensitive).

    Args:
        p: Path to validate.
        suffix: Expected suffix (e.g., '.toml', '.json').

    Returns:
        Path: The same path, if valid.

    Raises:
        SecurityError: If the suffix does not match.
    '''
    # Compare case-insensitively so '.TOML' also matches '.toml'.
    if p.suffix.lower() != suffix.lower():
        raise SecurityError(f'Invalid file type: expected {suffix}, got {p.suffix}')
    return p


_LEVEL_NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,63}(\.json)?$')


def clamp_int(value, min_value: int, max_value: int, field_name: str = 'value') -> int:
    '''
    Clamp/validate an integer-like input into an inclusive range.

    Args:
        value: Value to validate (int or str-int).
        min_value: Inclusive lower bound.
        max_value: Inclusive upper bound.
        field_name: Name used in error messages.

    Returns:
        int: Parsed integer value.

    Raises:
        SecurityError: If conversion fails or value is outside range.
    '''
    try:
        ivalue = int(value)
    except (TypeError, ValueError) as e:
        raise SecurityError(f'{field_name} must be an integer') from e

    if ivalue < min_value or ivalue > max_value:
        raise SecurityError(f'{field_name} must be between {min_value} and {max_value}')
    return ivalue


def validate_seed(seed, *, min_value: int = 0, max_value: int = 2**32 - 1):
    '''
    Validate a RNG seed.

    Args:
        seed: Seed value (int/str-int) or None.
        min_value: Inclusive lower bound (default 0).
        max_value: Inclusive upper bound (default 2**32-1).

    Returns:
        int | None: Validated seed or None.

    Raises:
        SecurityError: If seed is invalid.
    '''
    if seed is None:
        return None
    return clamp_int(seed, min_value, max_value, field_name='seed')


def safe_join(base_dir: Path, user_path: str | Path) -> Path:
    '''
    Join/resolve user_path within base_dir while preventing traversal.

    This is a naming wrapper required by Trello card 5.
    Internally reuses safe_resolve().

    Args:
        base_dir: Allowed base directory.
        user_path: User-supplied path (relative).

    Returns:
        Path: Safe absolute resolved path.
    '''
    return safe_resolve(base_dir, str(user_path))


def validate_level_name(name: str) -> str:
    '''
    Validate a level name so it cannot be used for traversal.

    Allowed:
      - letters, numbers, underscore, dash
      - optional .json suffix
      - max length 64 (excluding path separators since they are disallowed)

    Examples allowed: 'level1', 'level_01', 'boss-level.json'
    Disallowed: '../x', 'levels/a.json', 'a/b', 'a\\b', '.hidden', 'a..', 'a.json.bak'

    Args:
        name: User-provided level name.

    Returns:
        str: The same validated name.

    Raises:
        SecurityError: If invalid.
    '''
    if not isinstance(name, str):
        raise SecurityError('level name must be a string')

    cleaned = name.strip()
    if not cleaned:
        raise SecurityError('level name cannot be empty')

    # Hard-block separators/traversal primitives early.
    if '/' in cleaned or '\\' in cleaned or '..' in cleaned:
        raise SecurityError('invalid level name')

    if not _LEVEL_NAME_RE.fullmatch(cleaned):
        raise SecurityError('invalid level name')

    return cleaned
