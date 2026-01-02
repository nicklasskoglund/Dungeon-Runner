# Dungeon Runner
### Current version: v0.3.0

**Dungeon Runner** is a small 2D tile-based game in Python running with Pygame.

---

## Installation:
- ### Create a virtual environment
```bash
python -m venv .venv
```
- ### Activate the virtual environment
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

# Install dev tools (Ruff + pytest)
pip install -e ".[dev]"

# Optional
pip install -r requirements.txt
- Note: requirements.txt contains -e . and can be used as an alternative install path.
```

---

## Run (v0.3.0)
```bash
# Play a JSON level
python -m drunner play --level demo_level.json

# Generate a seeded level (rooms + corridors)
python -m drunner play --generate --seed 123

#Optional generator parameters:
python -m drunner play --generate --seed 123 --width 41 --height 31
```
#### Generated levels are saved under:
- levels/generated/seed_<_seed_>_<_width_>x<_height_>.json
- Recommended: keep levels/generated/ ignored in git (generated artifacts).

---

### Controls
- WASD/arrow keys: move
- ESC / window close: quit

### Outcome + reports
- Win/lose writes a run report file:
    - reports/run_<_timestamp_>_<_run_id_>.json

---

## Release versions (roadmap)
- v0.1.0 = “Foundation baseline”: project structure, CLI working, pygame-window clean open/closing, README with install/run.
- v0.2.0 = “First playable slice”: render grid + player movement + win/lose + run report.
- v0.3.0 = “Enemies + generator + polish”: enemy AI, seeded generator, tests, Ruff polish.
- vX.X.X = ...
- v1.0.0 = “Submission-ready”: crash/report robustness, full README, screenshots, tagged release. (TBC)

---

## Project structure
- `src/drunner/` – app/CLI/config/logging/security/reporting
- `src/drunner_core/` – game core (pygame loop, level, entities, systems)
```
/Dungeon-Runner/
    ├─ README.md
    ├─ .gitignore
    ├─ config.toml
    ├─ pyproject.toml
    ├─ pytest.ini
    ├─ requirements.txt
    ├─ requirements-dev.txt
    ├─ /src/
    │   ├─ /drunner/
    │   │   ├─ __init__.py
    │   │   ├─ __main__.py
    │   │   ├─ bugreport.py
    │   │   ├─ cli.py
    │   │   ├─ config.py
    │   │   ├─ log.py
    │   │   ├─ main.py
    │   │   ├─ report.py
    │   │   └─ security.py
    │   └─ /drunner_core/
    │       ├─ __init__.py
    │       ├─ enemy.py
    │       ├─ game.py
    │       ├─ game_helpers.py
    │       ├─ generators.py
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
        ├─ test_enemy_random_walk.py
        ├─ test_generators.py
        ├─ test_level_io.py
        ├─ test_report.py
        └─ test_security.py
```

---

## Tests
```bash
pytest -q
```

## Lint / format
```bash
ruff format .
ruff check .
```

---
