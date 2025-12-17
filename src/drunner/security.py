# src/drunner/security.py

'''
Security helpers for drunner.

Provides small utilities to validate user-supplied paths and file types.
'''

from __future__ import annotations

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