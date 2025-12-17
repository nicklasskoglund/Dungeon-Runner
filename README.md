# Dungeon Runner

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

### Run
```bash
drunner play
```

---

## Project structure
- `src/drunner/` – app/CLI/config/logging/security/reporting
- `src/drunner_core/` – spelkärna (pygame loop, level, entities, systems)

---
