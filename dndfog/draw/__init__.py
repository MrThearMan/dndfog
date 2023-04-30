import pygame

from dndfog.draw.map import draw_fog, draw_grid, draw_map, draw_markings, draw_pieces
from dndfog.draw.toolbar import draw_toolbar
from dndfog.types import LoopData, ProgramState


def draw(display: pygame.Surface, loop: LoopData, state: ProgramState) -> None:
    # Fill background
    display.fill(state.map.fog_color)

    draw_map(display, state.map)

    if state.show.grid:
        draw_grid(display, state.map)

    draw_pieces(display, state.map)

    if state.show.fog:
        draw_fog(display, state.map)

    draw_markings(display, state.map)

    draw_toolbar(display, loop.mouse_pos, state)

    pygame.display.flip()
