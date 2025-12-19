# tests/test_report.py

import json
from pathlib import Path

from drunner.report import write_run_report


def test_write_run_report_creates_file_with_fields(tmp_path: Path) -> None:
    p = write_run_report(
        project_root=tmp_path,
        result='WON',
        duration_seconds=1.23,
        level_source='demo_level.json',
        seed=123,
        run_id='abc123',
        score=None,
        version=None,
    )

    assert p.exists()
    data = json.loads(p.read_text(encoding='utf-8'))

    # Required fields
    for key in ('seed', 'duration_seconds', 'result', 'level_source', 'run_id', 'timestamp'):
        assert key in data

    assert data['result'] == 'WON'
    assert data['seed'] == 123
    assert data['run_id'] == 'abc123'