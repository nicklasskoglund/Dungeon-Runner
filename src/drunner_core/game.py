# src/drunner_core/game.py

'''
Core game loop for Dungeon Runner.

Sets up pygame, opens a window, handles basic events, and renders a minimal frame.
'''

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    # Imported only for type hints (avoids runtime imports/circular dependencies).
    import logging
    from drunner.config import AppConfig
    
    
def run_game(cfg: 'AppConfig', logger: 'logging.Logger') -> None:
    '''
    Run the main pygame loop.

    Args:
        cfg: Game/app configuration (window size, FPS, title).
        logger: Application logger for lifecycle messages.
    '''
    pygame.init()
    try:
        # Create the window and set the title.
        screen = pygame.display.set_mode((cfg.window_width, cfg.window_height))
        pygame.display.set_caption(cfg.title)
        
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
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False     # ESC quits
                    
            # Minimal render (just a background fill).
            screen.fill((20, 20, 20))
            pygame.display.flip()
            
            # Cap the loop to the configured FPS.
            clock.tick(cfg.fps)
            
    finally:
        # Always clean up pygame, even if something crashes.
        pygame.quit()
        logger.info('Pygame quit cleanly')