import os
import sys
from pathlib import Path

import pygame


def zoom_at_mouse_pos(
    mouse_position: tuple[int, int],
    grid_pos: tuple[int, int],
    old_gridsize: int,
    new_gridsize: int,
) -> tuple[int, int]:

    absolute_mouse_position = mouse_position[0] + grid_pos[0], mouse_position[1] + grid_pos[1]

    old_grid_place = absolute_mouse_position[0] / old_gridsize, absolute_mouse_position[1] / old_gridsize
    new_grid_place = absolute_mouse_position[0] / new_gridsize, absolute_mouse_position[1] / new_gridsize

    camera_delta = (
        round((new_grid_place[0] - old_grid_place[0]) * new_gridsize),
        round((new_grid_place[1] - old_grid_place[1]) * new_gridsize),
    )

    return camera_delta


def draw_grid(
    display: pygame.Surface,
    gridsize: int,
    camera: tuple[int, int],
    color: tuple[int, int, int] = (0xC5, 0xC5, 0xC5),
) -> None:

    width, height = display.get_size()

    start_x = ((camera[0] + gridsize - 1) // gridsize) * gridsize - 1
    start_y = ((camera[1] + gridsize - 1) // gridsize) * gridsize - 1
    end_x = start_x + width + gridsize
    end_y = start_y + height + gridsize

    for x in range(start_x, end_x, gridsize):
        pygame.draw.line(display, color, (x - camera[0], 0), (x - camera[0], height), 2)

    for y in range(start_y, end_y, gridsize):
        pygame.draw.line(display, color, (0, y - camera[1]), (width, y - camera[1]), 2)


def main():
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    clock = pygame.time.Clock()
    frame_rate: int = 60
    root_dir = Path(__file__).parent.parent
    gridsize = 20

    grid_pos = (0, 0)

    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode((800, 800), flags=flags)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        pressed_keys = pygame.key.get_pressed()
        pressed_buttons = pygame.mouse.get_pressed()
        mouse_speed = pygame.mouse.get_rel()

        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEWHEEL:
                old_gridsize = gridsize
                gridsize = gridsize + event.y
                camera_delta = zoom_at_mouse_pos(mouse_pos, grid_pos, old_gridsize, gridsize)
                grid_pos = grid_pos[0] - camera_delta[0], grid_pos[1] - camera_delta[1]

            if pressed_buttons[1]:
                grid_pos = grid_pos[0] - mouse_speed[0], grid_pos[1] - mouse_speed[1]

        display.fill((0xCC, 0xCC, 0xCC))
        draw_grid(display, gridsize, grid_pos)

        clock.tick(frame_rate)
        pygame.display.flip()


if __name__ == "__main__":
    main()
