import os

import pygame

from dndfog.draw import draw
from dndfog.event_handlers import handle_event
from dndfog.grid import grid_position
from dndfog.saving import load_map
from dndfog.types import LoopData, ProgramState


def run(map_file: str) -> None:
    # Init
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.display.set_caption("DND fog")
    clock = pygame.time.Clock()
    frame_rate: int = 60

    # Screen setup
    display_size = (1200, 800)
    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode(display_size, flags=flags)

    state = ProgramState()
    load_map(map_file, state)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        loop = LoopData(
            mouse_pos=mouse_pos,
            grid_pos=grid_position(mouse_pos, state.map.camera, state.map.gridsize),
            mouse_speed=pygame.mouse.get_rel(),
            pressed_modifiers=pygame.key.get_mods(),
            pressed_buttons=pygame.mouse.get_pressed(),
        )

        for event in pygame.event.get():
            handle_event(event, loop, state)

        draw(display, loop, state)
        clock.tick(frame_rate)
