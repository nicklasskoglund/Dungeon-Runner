# src/drunner/bugreport.py

from __future__ import annotations

import json
import secrets
import traceback
import uuid
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CrashReport:
    run_id: str
    timestamp: str
    seed: int
    exception_type: str
    exception_message: str
    stacktrace: str
    config: dict[str, Any]
    log_file: str | None = None
    log_tail: str | None = None
    version: str | None = None


def _make_run_id() -> str:
    return uuid.uuid4().hex[:10]


def _make_seed() -> int:
    return secrets.randbits(32)


def _make_timestamp() -> str:
    """
    Return a timestamp string: YYYYMMDD_HHMMSS_mmm (milliseconds).
    """
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S_") + f"{int(now.microsecond / 1000):03d}"


def _default_reports_dir(project_root: Path) -> Path:
    return project_root / "reports"


def sanitize_config(cfg: Any) -> dict[str, Any]:
    """
    Create a sanitized snapshot of cfg:
    - converts dataclasses/objects/mappings to dict
    - strips sensitive keys
    - converts Paths to strings
    """
    if cfg is None:
        raw: dict[str, Any] = {}
    elif isinstance(cfg, Mapping):
        raw = dict(cfg)
    elif is_dataclass(cfg):
        raw = asdict(cfg)
    else:
        raw = dict(vars(cfg))

    sensitive_markers = ("password", "secret", "token", "api_key", "apikey", "key")
    out: dict[str, Any] = {}

    for k, v in raw.items():
        lk = str(k).lower()
        if any(m in lk for m in sensitive_markers):
            out[str(k)] = "[REDACTED]"
            continue

        if isinstance(v, Path):
            out[str(k)] = str(v)
        else:
            # best effort JSON friendliness
            try:
                json.dumps(v)
                out[str(k)] = v
            except TypeError:
                out[str(k)] = str(v)

    return out


def tail_text_file(path: Path, max_lines: int = 80) -> str | None:
    """
    Return the last max_lines lines from a text file (best-effort).
    """
    if not path or not path.exists():
        return None

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-max_lines:])
    except Exception:
        return None


def write_crash_report(
    *,
    project_root: Path,
    exc: BaseException,
    cfg: Any,
    run_id: str | None = None,
    seed: int | None = None,
    log_file_path: Path | None = None,
    version: str | None = None,
) -> Path:
    """
    Write a crash report JSON under reports/ and return the created path.

    If seed/run_id are not provided, they are generated.
    """
    rid = run_id or _make_run_id()
    s = seed if seed is not None else _make_seed()
    ts = _make_timestamp()

    reports_dir = _default_reports_dir(project_root)
    reports_dir.mkdir(parents=True, exist_ok=True)

    crash_path = reports_dir / f"crash_{ts}_{rid}.json"

    stack = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    report = CrashReport(
        run_id=rid,
        timestamp=ts,
        seed=s,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        stacktrace=stack,
        config=sanitize_config(cfg),
        log_file=str(log_file_path) if log_file_path else None,
        log_tail=tail_text_file(log_file_path) if log_file_path else None,
        version=version,
    )

    payload: dict[str, Any] = asdict(report)
    with crash_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return crash_path


def run_guarded(
    func: Callable[[], Any],
    *,
    project_root: Path,
    cfg: Any,
    run_id: str | None = None,
    seed: int | None = None,
    log_file_path: Path | None = None,
    version: str | None = None,
    logger: Any | None = None,
) -> Any:
    """
    Execute func(). On exception, write crash report and re-raise.
    This is convenient for entrypoints and easy to unit test.
    """
    rid = run_id or _make_run_id()
    s = seed if seed is not None else _make_seed()

    try:
        return func()
    except Exception as exc:
        crash_path = write_crash_report(
            project_root=project_root,
            exc=exc,
            cfg=cfg,
            run_id=rid,
            seed=s,
            log_file_path=log_file_path,
            version=version,
        )
        if logger is not None:
            logger.exception("Unhandled exception. Crash report saved: %s", crash_path)
        raise
