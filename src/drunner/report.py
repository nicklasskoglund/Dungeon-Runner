# src/drunner/report.py

from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunReport:
    """
    Minimal run report persisted on win/lose.
    """

    run_id: str
    timestamp: str  # local timestamp string used in filename
    seed: int
    duration_seconds: float
    result: str  # 'WON' / 'LOST'
    level_source: str
    score: int | None = None
    version: str | None = None


def _make_run_id() -> str:
    return uuid.uuid4().hex[:10]


def _make_seed() -> int:
    # 32-bit seed is enough for reproducibility later
    return secrets.randbits(32)


def _make_timestamp() -> str:
    # Example: 20251219_151230_123
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S_") + f"{int(now.microsecond / 1000):03d}"


def _default_reports_dir(project_root: Path) -> Path:
    return project_root / "reports"


def write_run_report(
    *,
    project_root: Path,
    result: str,
    duration_seconds: float,
    level_source: str,
    seed: int | None = None,
    run_id: str | None = None,
    score: int | None = None,
    version: str | None = None,
) -> Path:
    """
    Write reports/run_<timestamp>_<run_id>.json and return the created path.
    """
    rid = run_id or _make_run_id()
    ts = _make_timestamp()
    s = seed if seed is not None else _make_seed()

    report = RunReport(
        run_id=rid,
        timestamp=ts,
        seed=s,
        duration_seconds=float(duration_seconds),
        result=str(result),
        level_source=str(level_source),
        score=score,
        version=version,
    )

    reports_dir = _default_reports_dir(project_root)
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = f"run_{ts}_{rid}.json"
    path = reports_dir / filename

    payload: dict[str, Any] = asdict(report)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return path
