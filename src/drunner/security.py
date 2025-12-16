# src/drunner/security.py

from __future__ import annotations

from pathlib import Path


class SecurityError(ValueError):
    pass


def safe_resolve(base_dir: Path, user_path: str) -> Path:
    '''
    Resolve user supplied path inside base_dir.
    Prevents path traversal (e.g. ../../secret).
    '''
    base = base_dir.resolve()
    candidate = (base / user_path).resolve()
    
    if base not in candidate.parents and candidate != base:
        raise SecurityError(f'Unsafe path: {user_path}')
    
    return candidate


def require_suffix(p: Path, suffix: str) -> Path:
    if p.suffix.lower() != suffix.lower():
        raise SecurityError(f'Invalid file type: expected {suffix}, got {p.suffix}')
    return p