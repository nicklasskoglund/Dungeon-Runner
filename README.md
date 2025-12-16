# Dungeon Runner

## Install
```bash
python -m venv .venv

# Windows: .venv\Scripts\activate
source .venv/bin/activate

# Install in development mode (editable)
pip install -e .

# Or install normally
pip install .
```

---

## Run
```bash
python -m drunner play
```

---

## Project structure
- `src/drunner/` – app/CLI/config/logging/security/reporting
- `src/drunner_core/` – spelkärna (pygame loop, level, entities, systems)

---
