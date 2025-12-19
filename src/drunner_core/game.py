# src/drunner_core/game.py

'''
Core game loop for Dungeon Runner.

Sets up pygame, opens a window, handles basic events, and renders a minimal frame.
'''

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from drunner_core.level import Level
from drunner_core.level_io import load_level
from drunner_core.render import compute_render_params, draw_level, draw_player
from drunner_core.game_helpers import find_spawn
from drunner_core.movement import try_move
from drunner_core.player import Player

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

    pygame.init()
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
            # Handle input/events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False  # ESC quits
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

            # Minimal render (just a background fill).
            screen.fill((20, 20, 20))
            draw_level(screen, level, params)
            draw_player(screen, player, params)
            pygame.display.flip()

            # Cap the loop to the configured FPS.
            clock.tick(cfg.fps)
            
    finally:
        # Always clean up pygame, even if something crashes.
        pygame.quit()
        logger.info('Pygame quit cleanly')