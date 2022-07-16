import os
import sys
from pathlib import Path

import pygame


def zoom_at_mouse_pos(
    display_size: tuple[int, int],
    mouse_position: tuple[int, int],
    gridsize: int,
    change: int,
) -> tuple[tuple[int, int], tuple[int, int]]:

    new_size = gridsize + change
    mouse_centered = display_size[0] - mouse_position[0], display_size[1] - mouse_position[1]

    camera_delta = (0, 0)

    return new_size, camera_delta


def draw_grid(display: pygame.Surface, gridsize: int, camera: tuple[int, int] = (0, 0)) -> None:

    width, height = display.get_size()

    start_x = ((round(camera[0]) + gridsize - 1) // gridsize) * gridsize - 1
    start_y = ((round(camera[1]) + gridsize - 1) // gridsize) * gridsize - 1
    end_x = start_x + width + gridsize
    end_y = start_y + height + gridsize

    for x in range(start_x, end_x, gridsize):
        pygame.draw.line(display, (0xC5, 0xC5, 0xC5), (x - camera[0], 0), (x - camera[0], height), 2)

    for y in range(start_y, end_y, gridsize):
        pygame.draw.line(display, (0xC5, 0xC5, 0xC5), (0, y - camera[1]), (width, y - camera[1]), 2)


def main():
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    clock = pygame.time.Clock()
    frame_rate: int = 60
    root_dir = Path(__file__).parent.parent
    gridsize = 20

    grid_pos = (0, 0)

    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode((1500, 800), flags=flags)

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
                gridsize, camera_delta = zoom_at_mouse_pos(display.get_size(), mouse_pos, gridsize, change=event.y)
                grid_pos = grid_pos[0] + camera_delta[0], grid_pos[1] + camera_delta[1]

            if pressed_buttons[1]:
                grid_pos = grid_pos[0] - mouse_speed[0], grid_pos[1] - mouse_speed[1]

        display.fill((0xCC, 0xCC, 0xCC))
        pygame.draw.rect(display, (255, 0, 0), (100, 100, 10, 10))
        draw_grid(display, gridsize, grid_pos)

        clock.tick(frame_rate)
        pygame.display.flip()


if __name__ == "__main__":
    main()
