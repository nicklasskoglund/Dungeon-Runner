# Dungeon Runner — V1 Spec (Underlag)

## Översikt
**Dungeon Runner** är ett litet 2D tile-baserat spel i Python (Pygame) med fokus på tydlig projektstruktur, config-baserad pathing, robust logging, filbaserade reports/bug reports, säker input-hantering och testning.

V1 ska vara fullt körbar lokalt via CLI och uppfylla kurskraven:
- Minst 2 paket, minst 5 moduler
- Minst 3 saker: läsa → bearbeta → skriva
- Minst 1 klass + minst 1 funktion i separat modul
- Config-fil för pathing
- Custom logger
- Säker input-hantering (om input finns)
- README (install + körning)
- Git + feature branching
- venv + requirements.txt

---

## V1 Scope

### In scope (V1)
- Pygame-baserad game loop med clean exit
- Level laddas från JSON **(obligatoriskt i V1)**
- (Valfritt i V1) Level genereras från seed via enkel generator
- Player movement + collision mot väggar
- Minst 1 enemy med enkel rörelse (random-walk eller patrol)
- Win/Lose conditions:
  - Win: nå exit
  - Lose: kollision med enemy (eller HP=0 om du vill lägga till HP)
- Filbaserad run report (JSON)
- Filbaserad crash/bug report (JSON) vid exception
- Config via `config.toml` styr paths, logging nivåer, default settings
- `security.py` validerar input (CLI + paths)
- Pytest-tester för centrala delar (security, level_io, report, generator om den ingår)

### Out of scope (V1)
- Databas (SQLite/Supabase/Postgres) — stretch (V1.1)
- Avancerad pathfinding för enemies
- Menysystem, inventory, avancerade sprites/animationer
- Multiplayer, nätverk

---

## CLI (V1)

### Kommandon (exempel)
- Kör med level-fil:
  - `python -m drunner --level demo_level.json`
- Kör med seed (om generator används som default eller valfritt läge):
  - `python -m drunner --seed 12345 --width 41 --height 31`
- Debug-läge:
  - `python -m drunner --level demo_level.json --debug`

### Argument (V1)
- `--level <filename>`: laddar en level JSON från `levels_dir` (inte godtycklig path)
- `--seed <int|random>`: seed för generator eller RNG (om generator inte används kan seed styra enemy RNG)
- `--width <int>` / `--height <int>`: dimensioner (clampas)
- `--fps <int>`: (valfritt) clampas
- `--debug`: sätter log level DEBUG och ev. debug overlay

---

## Säkerhet (security.py) — Regler (V1)
`security.py` ska tillämpa:
- Numeriska clamps:
  - width: 15–101
  - height: 15–101
  - fps: 30–240
- Seed:
  - `random` eller heltal i rimligt intervall (t.ex. 0–2^31-1)
- Level-fil:
  - får endast laddas från `levels_dir`
  - stoppa path traversal (`../`) med `safe_join`
- Report/Log output:
  - skriv endast till `reports_dir` respektive `logs_dir`

---

## Logging (V1)
- Console logging: INFO (default)
- File logging: DEBUG (default) eller konfigurerbart
- Varje run har:
  - `run_id` (UUID)
  - `seed` (om finns)
  - `level_source` ("file" eller "generated")

**Minimum events att logga:**
- GameStarted (run_id, seed, level_source)
- LevelLoaded/LevelGenerated
- GameResult (won/lost/quit)
- ReportWritten (path)
- CrashReportWritten (path) vid exception

---

## Reports (V1)

### Run report (JSON)
Skrivs vid avslut (win/lose/quit):
- Fil: `reports/run_<timestamp>_<run_id>.json`
- Måste innehålla seed/run_id/result/duration och några enkla stats.

### Crash report (JSON)
Skrivs vid exception:
- Fil: `reports/crash_<timestamp>_<run_id>.json`
- Innehåller exception + stacktrace + seed/run_id + config-snapshot (sanerad)

---

## Level-format (JSON) — V1 (minsta schema)

### Regler
- `width` och `height` matchar dimensionerna i `tiles`
- `tiles` är en lista av strängar (en sträng per rad)
- Tecken:
  - `#` = wall
  - `.` = floor
  - `P` = player start
  - `E` = exit
  - `M` = enemy spawn (valfritt; alternativt via enemies-listan)
- Exakt 1 `P` och 1 `E`

### Exempel: `levels/demo_level.json`
```json
{
  "id": "demo_level",
  "width": 15,
  "height": 11,
  "tiles": [
    "###############",
    "#P....#.......#",
    "#.##..#..####..#",
    "#..#..#.....#..#",
    "#..#..#####.#..#",
    "#..#......#.#..#",
    "#..######.#.#..#",
    "#......#..#.#..#",
    "#.####.#..#.#E.#",
    "#......#....M..#",
    "###############"
  ],
  "enemies": [
    { "type": "basic", "x": 12, "y": 9 }
  ]
}
```

---

## JSON-exempel: Run Report (V1)

### Exempel: reports/run_20251213_153012_4f2a...json
```json
{
  "run_id": "4f2a7b2c-6d2e-4e77-9f2f-1bb5d7c8c2d1",
  "timestamp_utc": "2025-12-13T14:30:12Z",
  "level_source": "file",
  "level_id": "demo_level",
  "seed": 12345,
  "result": "won",
  "duration_ms": 84213,
  "stats": {
    "steps": 310,
    "collisions": 27,
    "enemy_hits": 0
  },
  "version": "v1.0.0"
}
```

---

## JSON-exempel: Crash Report (V1)

### Exempel: reports/crash_20251213_153500_4f2a...json
```json
{
  "run_id": "4f2a7b2c-6d2e-4e77-9f2f-1bb5d7c8c2d1",
  "timestamp_utc": "2025-12-13T14:35:00Z",
  "level_source": "generated",
  "level_id": null,
  "seed": 418203,
  "exception": {
    "type": "IndexError",
    "message": "list index out of range"
  },
  "stacktrace": "Traceback (most recent call last):\n  ...",
  "config_snapshot": {
    "paths": {
      "levels_dir": "levels",
      "reports_dir": "reports",
      "logs_dir": "logs"
    },
    "game": {
      "fps": 60,
      "default_width": 41,
      "default_height": 31
    },
    "logging": {
      "level": "INFO",
      "file_level": "DEBUG"
    }
  },
  "log_file": "logs/run_4f2a7b2c-6d2e-4e77-9f2f-1bb5d7c8c2d1.log"
}
```

---

## Modulkontrakt (funktioner & klasser)

### drunner (app/infrastruktur)
```bash
drunner/config.py

- load_config(config_path: Path) -> AppConfig

- resolve_paths(cfg: AppConfig) -> AppConfig (skapar mappar vid behov)

drunner/log.py

- get_logger(name: str, cfg: AppConfig, run_id: str) -> logging.Logger

drunner/security.py

- clamp_int(value: int, min_v: int, max_v: int) -> int

- validate_seed(seed_str: str | None) -> int | None (stöd "random")

- validate_level_name(name: str) -> str

- safe_join(base_dir: Path, user_filename: str) -> Path (stoppar traversal)

drunner/report.py

- build_run_report(context: RunContext, result: str, stats: dict) -> dict

- write_run_report(report: dict, reports_dir: Path) -> Path

drunner/bugreport.py

- write_crash_report(exc: BaseException, context: dict, reports_dir: Path, log_file: Path | None) -> Path

drunner/cli.py

- parse_args(argv: list[str]) -> argparse.Namespace

- validate_args(args: argparse.Namespace, cfg: AppConfig) -> ValidatedArgs

drunner/__main__.py

- main() -> int (entrypoint; fångar exceptions och skriver crash report)
```

### drunner_core (spel/core)
```bash
drunner_core/level.py

- class Level:

    - width: int, height: int, grid: list[list[str]]

    - player_start: tuple[int,int], exit_pos: tuple[int,int]

    - helpers: is_wall(x,y) -> bool

drunner_core/level_io.py

- load_level(path: Path) -> Level

- (valfritt) save_level(level: Level, path: Path) -> None

drunner_core/generators.py (valfritt i V1 men rekommenderas)

- generate_level(seed: int, width: int, height: int) -> Level

- deterministisk: samma seed → samma level

drunner_core/entities.py

- class Player: (x,y, speed, etc.)

- class Enemy: (x,y, kind, etc.)

drunner_core/systems.py

- update_player(player, level, input_state, dt) -> dict(stats_delta)

- update_enemies(enemies, level, dt, rng) -> dict(stats_delta)

- resolve_collisions(...) -> dict(stats_delta)

drunner_core/render.py

- render(screen, level, player, enemies, debug: bool) -> None

drunner_core/game.py

- class Game:

    - init(level, cfg, logger, rng, run_context)

    - run() -> tuple[result: str, stats: dict]
```

---

## Map-/filstruktur (V1 — lås denna)
```bash
dungeon-runner/
  README.md
  .gitignore
  config.toml
  requirements.txt

  src/
    drunner/
      __init__.py
      __main__.py
      cli.py
      config.py
      log.py
      bugreport.py
      security.py
      report.py

    drunner_core/
      __init__.py
      game.py
      level.py
      level_io.py
      generators.py
      entities.py
      systems.py
      render.py

  assets/
    tiles/
    fonts/

  levels/
    demo_level.json

  logs/
    .gitkeep

  reports/
    .gitkeep

  tests/
    test_security.py
    test_level_io.py
    test_reports.py
    test_generators.py

```

---

## Requirements.txt (förslag, V1)
Minst externa bibliotek (justera efter behov):
- pygame
- pytest
- ruff
- python-dotenv (valfritt)

---

## Git workflow (V1)
- main: alltid körbar
- feature-branches: feature/ 'kortnamn'
- Merge via PR (även solo) med kort beskrivning och hur testat (pytest)

---

## Acceptance: “Submission-ready”
V1 är klar när:
- python -m drunner --level demo_level.json fungerar på en ren maskin (efter install)
- run report skapas i reports/
- crash report skapas vid simulerat fel
- minst 3 testfiler finns och pytest passerar
- README har install + run + exempel
- requirements.txt finns
- repo är public och har rimlig commit-historik med feature branches