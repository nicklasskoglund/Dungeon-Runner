# src/drunner/config.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


try:
    import tomllib              # Python 3.11+
except ModuleNotFoundError:     # pragma: no cover
    tomllib = None


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    logs_dir: Path
    reports_dir: Path
    levels_dir: Path
    assets_dir: Path
    
    console_level: str
    file_level: str
    log_file: Path
    
    window_width: int
    window_height: int
    fps: int
    title: str
    
def _project_root() -> Path:
    # src/drunner/config.py -> parants[2] = repo-root
    return Path(__file__).resolve().parents[2]


def load_config(config_path: Path | None = None) -> AppConfig:
    root = _project_root()
    cfg_path = config_path or (root / 'config.toml')
    
    if not cfg_path.exists():
        raise FileNotFoundError(f'Missing config file: {cfg_path}')
    
    if tomllib is None:
        raise RuntimeError('tomllib not available. Use Python 3.11+ for config.toml support')
    
    data: dict[str, Any] = tomllib.loads(cfg_path.read_text(encoding='utf-8'))
    
    paths = data.get('paths', {})
    logging_cfg = data.get('logging', {})
    game = data.get('game', {})
    
    logs_dir = root / paths.get('logs_dir', 'logs')
    reports_dir = root / paths.get('reports_dir', 'reports')
    levels_dir = root / paths.get('levels_dir', 'levels')
    assets_dir = root / paths.get('assets_dir', 'assets')
    
    # säkerställ att output-mappar finns
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / str(logging_cfg.get('file_name', 'drunner.log'))
    
    return AppConfig(
        root_dir=root,
        logs_dir=logs_dir,
        reports_dir=reports_dir,
        levels_dir=levels_dir,
        assets_dir=assets_dir,
        console_level=str(logging_cfg.get('console_level', 'INFO')),
        file_level=str(logging_cfg.get('file_level', 'DEBUG')),
        log_file=log_file,
        window_width=int(game.get('window_width', 960)),
        window_height=int(game.get('window_height', 540)),
        fps=int(game.get('fps', 60)),
        title=str(game.get('title', 'Dungeon Runner')),
    )