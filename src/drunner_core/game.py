# src/drunner_core/game.py

'''
Core game loop for Dungeon Runner.

Sets up pygame, opens a window, handles basic events, and renders a minimal frame.
'''

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame
import random

from drunner_core.enemy import Enemy
from drunner_core.level import Level, Tile
from drunner_core.level_io import load_level
from drunner_core.render import compute_render_params, draw_level, draw_player, draw_enemies
from drunner_core.game_helpers import find_spawn
from drunner_core.movement import try_move
from drunner_core.player import Player
from drunner_core.state import GameState
from drunner.report import write_run_report

TIME_LIMIT_SECONDS = 60
RESULT_HOLD_MS = 1200

if TYPE_CHECKING:
    # Imported only for type hints (avoids runtime imports/circular dependencies).
    import logging
    from drunner.config import AppConfig
    
    
def run_game(cfg: 'AppConfig', logger: 'logging.Logger', level_path: Path | None = None) -> None:
    '''
    Run the main pygame loop.

    Args:
        cfg: Game/app configuration (window size, FPS, title).
        logger: Application logger for lifecycle messages.
        level_path: Optional path to a JSON level file. If None, uses a fallback demo level.
    '''
    # Load level (from JSON if provided, otherwise fallback)
    level = load_level(level_path) if level_path else Level.from_ascii(
        [
            '##########',
            '#S......E#',
            '#........#',
            '##########',
        ],
        name='fallback_demo',
    )
    logger.info('Level loaded: %s (%dx%d)', level.name, level.width, level.height)
    
    # Spawn player (prefer START tile)
    sx, sy = find_spawn(level)
    player = Player(x=sx, y=sy)
    logger.info('Player spawned at (%d,%d)', player.x, player.y)
    
    # Project root for reports: prefer cfg.root if it exists, else CWD
    project_root = Path(getattr(cfg, 'root', Path.cwd()))
    
    report_written = False
    level_source = str(level_path) if level_path else f'ascii:{level.name}'
    
    # Keep one seed/run_id per run (seed can be used later for determinism)
    run_seed = None
    run_id = None
    
    state = GameState.RUNNING
    state_end_ticks: int | None = None

    # Enemy entities (spawn from level if present; fallback otherwise)
    spawn_points = getattr(level, "enemies", [])
    enemies: list[Enemy] = [Enemy(x=int(x), y=int(y)) for (x, y) in spawn_points] if spawn_points else []
    
    if not enemies:
        # Fallback: place one enemy on a random walkable tile that isn't the player spawn.
        candidates: list[tuple[int, int]] = []
        for x, y, _tile in level.iter_tiles():
            if (x, y) != (player.x, player.y) and level.is_walkable(x, y):
                candidates.append((x, y))

    if candidates:
        ex, ey = random.choice(candidates)
        enemies = [Enemy(x=ex, y=ey)]
        logger.info("Enemy spawned (fallback, random) at (%d,%d)", ex, ey)

    pygame.init()
    start_ticks = pygame.time.get_ticks()
    
    try:
        # Create the window and set the title.
        screen = pygame.display.set_mode((cfg.window_width, cfg.window_height))
        pygame.display.set_caption(cfg.title)
        
        params = compute_render_params(level, cfg.window_width, cfg.window_height)
        logger.debug(
            'Render params: tile_size=%d offset=(%d,%d)',
            params.tile_size,
            params.offset_x,
            params.offset_y,
        )

        clock = pygame.time.Clock()
        running = True

        logger.info(
            'Pygame initialized (%dx%d @ %dfps)',
            cfg.window_width,
            cfg.window_height,
            cfg.fps,
        )
        
        while running:
            dt = clock.tick(cfg.fps) / 1000.0
            now_ticks = pygame.time.get_ticks()
            elapsed_s = (now_ticks - start_ticks) / 1000.0

            # Handle input/events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False  # ESC quits
                        continue

                    # Stoppa input när vi redan har WON/LOST
                    if state != GameState.RUNNING:
                        continue

                    moved = False
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        moved = try_move(level, player, dx=-1, dy=0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        moved = try_move(level, player, dx=1, dy=0)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        moved = try_move(level, player, dx=0, dy=-1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        moved = try_move(level, player, dx=0, dy=1)

                    if moved:
                        logger.debug('Player moved to (%d,%d)', player.x, player.y)
                        
            if state == GameState.RUNNING:
                for enemy in enemies:
                    enemy.update(dt, level)

            # --- Win/Lose checks (bara medan RUNNING) ---
            if state == GameState.RUNNING:
                # Win: player når exit
                if level.tile_at(player.x, player.y) == Tile.EXIT:
                    state = GameState.WON
                    logger.info('Result: WON (exit reached) in %.2fs', elapsed_s)
                    pygame.display.set_caption(f'{cfg.title} - WON')
                    state_end_ticks = now_ticks + RESULT_HOLD_MS
                    
                    if not report_written:
                        report_path = write_run_report(
                            project_root=project_root,
                            result=state.name,                 # 'WON'
                            duration_seconds=elapsed_s,
                            level_source=level_source,
                            seed=run_seed,
                            run_id=run_id,
                            score=None,
                            version=None,
                        )
                        logger.info('Run report saved: %s', report_path)
                        report_written = True

                # Lose: enemy collision (hook för senare)
                elif any((enemy.x == player.x and enemy.y == player.y) for enemy in enemies):
                    state = GameState.LOST
                    logger.info('Result: LOST (enemy collision) in %.2fs', elapsed_s)
                    pygame.display.set_caption(f'{cfg.title} - LOST')
                    state_end_ticks = now_ticks + RESULT_HOLD_MS
                    
                    if not report_written:
                        report_path = write_run_report(
                            project_root=project_root,
                            result=state.name,                 # 'LOST'
                            duration_seconds=elapsed_s,
                            level_source=level_source,
                            seed=run_seed,
                            run_id=run_id,
                            score=None,
                            version=None,
                        )
                        logger.info('Run report saved: %s', report_path)
                        report_written = True

                # Lose: timer
                elif elapsed_s >= TIME_LIMIT_SECONDS:
                    state = GameState.LOST
                    logger.info('Result: LOST (time limit %.0fs) in %.2fs', TIME_LIMIT_SECONDS, elapsed_s)
                    pygame.display.set_caption(f'{cfg.title} - LOST')
                    state_end_ticks = now_ticks + RESULT_HOLD_MS
                    
                    if not report_written:
                        report_path = write_run_report(
                            project_root=project_root,
                            result=state.name,                 # 'LOST'
                            duration_seconds=elapsed_s,
                            level_source=level_source,
                            seed=run_seed,
                            run_id=run_id,
                            score=None,
                            version=None,
                        )
                        logger.info('Run report saved: %s', report_path)
                        report_written = True

            # Render
            screen.fill((20, 20, 20))
            draw_level(screen, level, params)
            draw_enemies(screen, enemies, params)
            draw_player(screen, player, params)
            pygame.display.flip()

            # Auto-exit shortly after result
            if state_end_ticks is not None and pygame.time.get_ticks() >= state_end_ticks:
                running = False
                
        if state == GameState.RUNNING:
            elapsed_s = (pygame.time.get_ticks() - start_ticks) / 1000.0
            logger.info('Result: ABORTED (quit) in %.2fs', elapsed_s)
            
    finally:
        # Always clean up pygame, even if something crashes.
        pygame.quit()
        logger.info('Pygame quit cleanly')