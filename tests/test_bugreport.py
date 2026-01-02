# tests/test_bugreport.py

import json
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from drunner import main as app_main
from drunner.bugreport import run_guarded


def test_crash_report_created_on_exception(tmp_path: Path) -> None:
    class DummyCfg:
        root_dir = tmp_path
        title = "Dungeon Runner"
        fps = 60

    def boom() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        run_guarded(
            boom,
            project_root=tmp_path,
            cfg=DummyCfg(),
            run_id="abc123",
            seed=123,
            log_file_path=None,
            logger=None,
        )

    reports_dir = tmp_path / "reports"
    files = list(reports_dir.glob("crash_*_abc123.json"))
    assert len(files) == 1

    data = json.loads(files[0].read_text(encoding="utf-8"))
    for key in (
        "run_id",
        "timestamp",
        "seed",
        "stacktrace",
        "config",
        "exception_type",
        "exception_message",
    ):
        assert key in data

    assert data["run_id"] == "abc123"
    assert data["seed"] == 123
    assert "RuntimeError" in data["stacktrace"]


class DummyLogger:
    def info(self, *_a, **_k): ...
    def debug(self, *_a, **_k): ...
    def error(self, *_a, **_k): ...
    def exception(self, *_a, **_k): ...


class DummyCfg:
    def __init__(self, root_dir: Path, log_file: Path):
        self.root_dir = root_dir
        self.log_file = str(log_file)
        self.api_token = "supersecret"  # should be sanitized to [REDACTED]


def test_entrypoint_creates_crash_report(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    # create a log file so bugreport can include log_tail
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "drunner.log"
    log_path.write_text("line1\nline2\n", encoding="utf-8")

    cfg = DummyCfg(root_dir=tmp_path, log_file=log_path)

    # patch config + logger
    monkeypatch.setattr(app_main, "load_config", lambda: cfg)
    monkeypatch.setattr(app_main, "configure_logging", lambda _cfg: DummyLogger())

    # patch run_game so it crashes
    def boom(*_args, **_kwargs) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(app_main, "run_game", boom)

    exit_code = app_main.run(None)
    assert exit_code == 1

    crash_files = list((tmp_path / "reports").glob("crash_*.json"))
    assert len(crash_files) == 1

    data = json.loads(crash_files[0].read_text(encoding="utf-8"))

    # acceptance: stacktrace + seed + run_id + sanitized config
    for k in ("stacktrace", "seed", "run_id", "config"):
        assert k in data

    assert "RuntimeError" in data["stacktrace"]
    assert data["config"].get("api_token") == "[REDACTED]"

    # logfile is pointed out and/or tail is included (we expect both if you pass log_file_path in main.py)
    assert data.get("log_file") is not None
    assert data.get("log_tail") is not None
