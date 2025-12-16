# src/drunner_core/game.py

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    import logging
    from drunner.config import AppConfig
    
    
def run_game(cfg: 'AppConfig', logger: 'logging.Logger') -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((cfg.window_width, cfg.window_height))
        pygame.display.set_caption(cfg.title)
        
        clock = pygame.time.Clock()
        running = True
        
        logger.info('Pygame initialized (%dx%d @ %dfps)', cfg.window_width, cfg.window_height, cfg.fps)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                    
            # minimal render
            screen.fill((20, 20, 20))
            pygame.display.flip()
            
            clock.tick(cfg.fps)
            
    finally:
        pygame.quit()
        logger.info('Pygame quit cleanly')