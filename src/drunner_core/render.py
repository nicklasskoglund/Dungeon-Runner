# src/drunner_core/render.py

from __future__ import annotations

from dataclasses import dataclass

import pygame

from drunner_core.level import Level, Tile
from drunner_core.player import Player


@dataclass(frozen=True)
class RenderParams:
    """
    Rendering parameters for drawing a tile grid.
    """
    tile_size: int
    offset_x: int
    offset_y: int
    
    
def compute_render_params(level: Level, window_width: int, window_hight: int) -> RenderParams:
    """
    Compute tile size and offsets to fit the level inside the window and center it.
    """
    if level.width <= 0 or level.height <= 0:
        raise ValueError('Level has invalid dimensions.')
    
    tile_size = min(window_width // level.width, window_hight // level.height)
    tile_size = max(tile_size, 1)
    
    grid_px_w = level.width * tile_size
    grid_px_h = level.height * tile_size
    
    offset_x = (window_width - grid_px_w) // 2
    offset_y = (window_hight - grid_px_h) // 2
    
    return RenderParams(tile_size=tile_size, offset_x=offset_x, offset_y=offset_y)


def draw_level(surface: pygame.surface, level: Level, params: RenderParams) -> None:
    """
    Draw the level grid using filled rectangles.
    """
    # Basic palette (rects only; sprites come later if you want)
    colors: dict[Tile, tuple[int, int, int]] = {
        Tile.FLOOR: (40, 40, 40),
        Tile.WALL: (110, 110, 110),
        Tile.START: (40, 140, 40),
        Tile.EXIT: (140, 40, 40),
    }
    
    ts = params.tile_size
    ox = params.offset_x
    oy = params.offset_y
    
    for x, y, tile in level.iter_tiles():
        rect = pygame.Rect(ox + x * ts, oy + y * ts, ts, ts)
        color = colors.get(tile, (255, 0, 255)) # magenta = unknown tile
        pygame.draw.rect(surface, color, rect)
        
    # Subtle border around the grid (helps readability)
    border = pygame.Rect(ox, oy, level.width * ts, level.height * ts)
    pygame.draw.rect(surface, (20, 20, 20), border, width=2)
    
    
def draw_player(surface: pygame.Surface, player: Player, params: RenderParams) -> None:
    ts = params.tile_size
    ox = params.offset_x
    oy = params.offset_y
    
    pad = max(2, ts // 8)
    rect = pygame.Rect(
        ox + player.x * ts + pad,
        oy + player.y * ts + pad,
        ts - 2 * pad,
        ts - 2 * pad,
    )
    pygame.draw.rect(surface, (220, 220, 80), rect)