import copy
import os
import sys
from pathlib import Path

import pygame

from dndfog.fps import true_fps
from dndfog.glow import Glow


def approx(value: int | float, /) -> int:
    return int(value) if value > 0 else int(value - 1)


def draw_position(
    pos: tuple[int | float, int | float],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int]:
    return (pos[0] * gridsize) - camera[0], (pos[1] * gridsize) - camera[1]


def grid_position(pos: tuple[int, int], camera: tuple[int, int], gridsize: int) -> tuple[int, int]:
    return approx((pos[0] + camera[0]) / gridsize), approx((pos[1] + camera[1]) / gridsize)


def zoom_at_mouse_pos(
    mouse_position: tuple[int, int],
    camera: tuple[int, int],
    old_gridsize: int,
    new_gridsize: int,
) -> tuple[int, int]:

    absolute_mouse_position = mouse_position[0] + camera[0], mouse_position[1] + camera[1]

    old_grid_place = absolute_mouse_position[0] / old_gridsize, absolute_mouse_position[1] / old_gridsize
    new_grid_place = absolute_mouse_position[0] / new_gridsize, absolute_mouse_position[1] / new_gridsize

    camera_delta = (
        round((new_grid_place[0] - old_grid_place[0]) * new_gridsize),
        round((new_grid_place[1] - old_grid_place[1]) * new_gridsize),
    )

    return camera_delta


def draw_grid(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
    color: tuple[int, int, int] = (0xC5, 0xC5, 0xC5),
) -> None:

    width, height = display.get_size()

    start_x, start_y, end_x, end_y = get_visible_area_limits(display, camera, gridsize)

    for x in range(start_x, end_x, gridsize):
        pygame.draw.line(display, color, (x - camera[0], 0), (x - camera[0], height), 2)

    for y in range(start_y, end_y, gridsize):
        pygame.draw.line(display, color, (0, y - camera[1]), (width, y - camera[1]), 2)


def draw_fog(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
    removed: set[tuple[int, int]],
    color: tuple[int, int, int] = (0xC5, 0xC5, 0xC5),
) -> None:

    start_x, start_y, end_x, end_y = get_visible_area_limits(display, camera, gridsize)
    start_x, start_y, end_x, end_y = start_x // gridsize, start_y // gridsize, end_x // gridsize, end_y // gridsize

    inner_color = pygame.Color(*color)
    outer_color = copy.deepcopy(inner_color)
    outer_color.a = 0

    glow = Glow(
        radius_range=range(gridsize, gridsize // 2, -1),
        inner_color=inner_color,
        outer_color=outer_color,
    )

    for x in range(start_x, end_x, 1):
        for y in range(start_y, end_y, 1):
            if (x, y) in removed:
                continue

            display.blit(next(glow), draw_position((x - 0.5, y - 0.5), camera, gridsize))
            # pygame.draw.circle(
            #     display,
            #     color,
            #     draw_position((x + 0.5, y + 0.5), camera, gridsize),
            #     gridsize * 0.8,
            # )


def get_visible_area_limits(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int, int, int]:
    width, height = display.get_size()
    start_x = ((camera[0] + gridsize - 1) // gridsize) * gridsize - 1
    start_y = ((camera[1] + gridsize - 1) // gridsize) * gridsize - 1
    end_x = start_x + width + gridsize
    end_y = start_y + height + gridsize
    return start_x, start_y, end_x, end_y


def main():
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.display.set_caption("DND fog")
    true_fps.display_caption = "DND fog"
    clock = pygame.time.Clock()
    frame_rate: int = 60
    root_dir = Path(__file__).parent.parent
    gridsize = 40

    removed: set[tuple[int, int]] = set()

    camera = (0, 0)

    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode((800, 800), flags=flags)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        pressed_keys = pygame.key.get_pressed()
        pressed_modifiers = pygame.key.get_mods()
        pressed_buttons = pygame.mouse.get_pressed()
        mouse_speed = pygame.mouse.get_rel()

        for event in pygame.event.get():

            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEWHEEL:
                old_gridsize = gridsize
                if gridsize + event.y > 0:
                    gridsize = gridsize + event.y
                    camera_delta = zoom_at_mouse_pos(mouse_pos, camera, old_gridsize, gridsize)
                    camera = camera[0] - camera_delta[0], camera[1] - camera_delta[1]

            if pressed_buttons[0]:
                pos = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
                poss = [
                    pos,
                    grid_position((mouse_pos[0] + (gridsize * 0.5), mouse_pos[1]), camera, gridsize),
                    grid_position((mouse_pos[0], mouse_pos[1] + (gridsize * 0.5)), camera, gridsize),
                    grid_position((mouse_pos[0] - (gridsize * 0.5), mouse_pos[1]), camera, gridsize),
                    grid_position((mouse_pos[0], mouse_pos[1] - (gridsize * 0.5)), camera, gridsize),
                ]

                for p in poss:
                    if pressed_modifiers & pygame.KMOD_CTRL:
                        removed.discard(pos)
                    else:
                        removed.add(p)

            if pressed_buttons[1]:
                camera = camera[0] - mouse_speed[0], camera[1] - mouse_speed[1]

        display.fill((0xCC, 0xCC, 0xCC))
        draw_grid(display, camera, gridsize)

        draw_fog(display, camera, gridsize, removed)

        pygame.display.flip()

        with true_fps.track():
            clock.tick(frame_rate)


if __name__ == "__main__":
    main()
