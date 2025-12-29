# Dungeon Runner
### Current version: v0.2.0

**Dungeon Runner** is a smal 2D tile-based game in Python runing Pygame.

---

## Installation:
- ### Install venv
```bash
# Create venv:
python -m venv .venv
```
- ### Activate venv
```bash
# Windows:
source .venv/scripts/activate

# macOS/Linux:
source .venv/bin/activate
```


- ### Install
```bash
# Install in development mode (editable):
pip install -e .

# Optional
pip install -r requirements.txt
```

---

## Run (v0.2.0)
```bash
python -m drunner play --level demo_level.json
```

### Controls
- WASD/arrow keys: move
- ESC / window close: quit

### Outcome + reports
- win/lose creates a reportfile: reports/run_<_timestamp_>_<_run_id_>.json

---

## Release versions (roadmap)
- v0.1.0 = “Foundation baseline”: projectstructure, CLI working, pygame-window clean open/closing, README with install/run.
- v0.2.0 = “First playable slice”: render grid + player movement + win/lose + report.
- v0.3.0 = “Enemy + full loop”: + polish (TBC)
- vX.X.X = ...
- v1.0.0 = “Submission-ready”: tests, crash/report robustness, full README, screenshots, tagged release. (TBC)

---

## Project structure
- `src/drunner/` – app/CLI/config/logging/security/reporting
- `src/drunner_core/` – gamecore (pygame loop, level, entities, systems)
```
/Dungeon-Runner/
    ├─ README.md
    ├─ .gitignore
    ├─ config.toml
    ├─ pyproject.toml
    ├─ requirements.txt
    ├─ /src/
    │   ├─ /drunner/
    │   │   ├─ __init__.py
    │   │   ├─ __main__.py
    │   │   ├─ bureport.py
    │   │   ├─ cli.py
    │   │   ├─ config.py
    │   │   ├─ log.py
    │   │   ├─ main.py
    │   │   ├─ report.py
    │   │   └─ security.py
    │   └─ /drunner_core/
    │       ├─ __init__.py
    │       ├─ game.py
    │       ├─ game_helpers.py
    │       ├─ level.py
    │       ├─ level_io.py
    │       ├─ movement.py
    │       ├─ player.py
    │       ├─ render.py
    │       └─ state.py
    ├─ /assets/
    │   ├─ /fonts/
    │   └─ /tiles/
    ├─ /docs/
    │   └─ spec.md
    ├─ /levels/
    │   └─ demo_level.json
    ├─ /logs/
    │   └─ .gitkeep
    ├─ /reports/
    │   └─ .gitkeep
    └─ /tests/
        ├─ test_bugreport.py
        └─ test_report.py
```

---

## Tests
```bash
# .venv
pytest -q
```

---
