# tests/test_report.py

import json
import re
from pathlib import Path

import pytest

from drunner.report import write_run_report


def test_write_run_report_creates_file_and_fields(tmp_path: Path) -> None:
    out = write_run_report(
        project_root=tmp_path,
        result='WON',
        duration_seconds=1.23,
        level_source='levels/demo.json',
        seed=123,
        run_id='abc123',
        score=10,
        version='0.2.0',
    )

    assert out.exists()
    assert out.parent == tmp_path / 'reports'
    assert out.name.startswith('run_')
    assert 'abc123' in out.name

    data = json.loads(out.read_text(encoding='utf-8'))

    assert data['run_id'] == 'abc123'
    assert data['seed'] == 123
    assert data['result'] == 'WON'
    assert data['level_source'] == 'levels/demo.json'
    assert data['score'] == 10
    assert data['version'] == '0.2.0'
    assert data['duration_seconds'] == pytest.approx(1.23)

    # timestamp format: YYYYMMDD_HHMMSS_mmm
    assert re.fullmatch(r'\d{8}_\d{6}_\d{3}', data['timestamp']) is not None
