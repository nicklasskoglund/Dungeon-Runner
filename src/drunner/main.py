# src/drunner/main.py

from __future__ import annotations

import sys
import time
from pathlib import Path

from drunner.bugreport import write_crash_report
from drunner.config import load_config
from drunner.log import configure_logging
from drunner.security import SecurityError, require_suffix, safe_resolve
from drunner_core.game import run_game
from drunner_core.generators import generate_level
from drunner_core.level_io import LevelIOError, save_level


def run(
    level: str | None = None,
    *,
    generate: bool = False,
    seed: int | None = None,
    width: int | None = None,
    height: int | None = None,
) -> int:
    """
    Application entrypoint used by the CLI.

    Loads config + logging, resolves a level source (file or generator),
    starts the pygame loop, and returns a process exit code.

    Exit codes:
        0: clean exit
        1: unexpected crash (crash report written)
        2: expected/user error (bad input, missing level, invalid level, security)
    """
    cfg = load_config()
    logger = configure_logging(cfg)

    logger.info("Starting Dungeon Runner")
    logger.debug("Config root=%s", cfg.root_dir)

    try:
        level_path: Path | None = None

        if generate:
            # Default seed: current epoch seconds (easy to reproduce if logged)
            seed_final = int(seed) if seed is not None else int(time.time())
            w = int(width) if width is not None else 41
            h = int(height) if height is not None else 31

            lvl = generate_level(seed_final, w, h)

            cfg.levels_dir.mkdir(parents=True, exist_ok=True)
            gen_dir = cfg.levels_dir / "generated"
            gen_dir.mkdir(parents=True, exist_ok=True)

            gen_file = gen_dir / f"seed_{seed_final}_{w}x{h}.json"
            save_level(lvl, gen_file)

            logger.info(
                "Generated level saved: %s (seed=%s size=%sx%s)", gen_file, seed_final, w, h
            )
            level_path = gen_file

        else:
            if level:
                p = safe_resolve(cfg.levels_dir, level)
                require_suffix(p, ".json")
                level_path = p

        run_game(cfg, logger, level_path=level_path)

        logger.info("Exiting Dungeon Runner")
        return 0

    except (FileNotFoundError, SecurityError, LevelIOError) as e:
        logger.error("%s", e)
        print(f"ERROR: {e}", file=sys.stderr)
        print(f"See log file: {cfg.log_file}", file=sys.stderr)
        return 2

    except Exception as e:
        crash_path = write_crash_report(
            project_root=cfg.root_dir,
            exc=e,
            cfg=cfg,
            run_id=None,
            seed=None,
            log_file_path=Path(cfg.log_file) if getattr(cfg, "log_file", None) else None,
            version=None,
        )

        logger.exception("Unhandled exception. Crash report saved: %s", crash_path)

        print("ERROR: Unexpected crash.", file=sys.stderr)
        print(f"Crash report: {crash_path}", file=sys.stderr)
        print(f"See log file: {cfg.log_file}", file=sys.stderr)
        return 1
