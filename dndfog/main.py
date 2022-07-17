import copy
import os
import sys
from argparse import ArgumentParser
from itertools import cycle
from pathlib import Path
from random import randint

import pygame

from dndfog.fps import true_fps


class Glow:
    def __init__(self, radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color):
        self._radius_range = radius_range
        self._inner_color = inner_color
        self._outer_color = outer_color
        self._glow_cycle = cycle([self._build_glow(radius_range, inner_color, outer_color)])

    @classmethod
    def uniform(cls, radius: int, color) -> "Glow":
        if not isinstance(color, pygame.Color):
            color = pygame.Color(*color)

        outer_color = copy.deepcopy(color)
        outer_color.a = 0

        return cls(range(radius, 0, -1), color, outer_color)

    def __iter__(self) -> "Glow":
        return self

    def __next__(self) -> pygame.Surface:
        return next(self._glow_cycle)

    @staticmethod
    def _build_glow(radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color) -> pygame.Surface:
        colors, radii = [], []

        lerp_steps = range(1, len(radius_range) + 1)

        # create colors for glow from the largest circle's color to the smallest
        for lerp_step, radius_step in zip(lerp_steps, radius_range):
            lerped_color = outer_color.lerp(inner_color, lerp_step / len(radius_range))

            radii.append(radius_step)
            colors.append(lerped_color)

        glow_surface_size = 2 * radius_range.start, 2 * radius_range.start
        glow_surface_center = radius_range.start, radius_range.start
        # Glow circles are not solid so that blend mode works right and each band has 1 pixel overlap
        band_width = abs(radius_range.step) + 1

        glow = pygame.Surface(glow_surface_size, flags=pygame.SRCALPHA)

        # Draw glow in shrinking circles. Draw a circle first to a temp surface
        # and then blit that to the glow surface with it's alpha value in RGBA-MAX blend mode.
        for i, (circle_color, circle_radius) in enumerate(zip(colors, radii)):
            temp_surface = pygame.Surface(glow_surface_size, flags=pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                circle_color,
                glow_surface_center,
                circle_radius,
                band_width if i != len(colors) - 1 else 0,
            )
            temp_surface.set_alpha(circle_color.a)

            glow.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)

        return glow


def approx(value: int | float, /) -> int:
    return int(value) if value > 0 else int(value - 1)


def draw_position(
    pos: tuple[int | float, int | float],
    camera: tuple[int, int],
    gridsize: int,
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int]:
    return (pos[0] * gridsize) - camera[0] - offset[0], (pos[1] * gridsize) - camera[1] - offset[1]


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
    # Init
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.display.set_caption("DND fog")
    true_fps.display_caption = "DND fog"
    clock = pygame.time.Clock()
    frame_rate: int = 60
    modifiers = {pygame.KMOD_ALT, pygame.KMOD_CTRL, pygame.KMOD_SHIFT}

    colors = [
        (255, 0, 0),  # red
        (255, 255, 0),  # yellow
        (0, 0, 255),  # blue
        (0, 100, 0),  # green
        (0, 255, 255),  # cyan
        (255, 0, 255),  # magenta
        (255, 100, 0),  # orange
        (100, 0, 100),  # purple
        (0, 255, 0),  # light green
        (110, 38, 14),  # brown
        (255, 192, 203),  # pink
        (109, 113, 46),  # olive
        (220, 180, 255),  # lavender
        (253, 133, 105),  # peach
    ]
    orig_colors = colors.copy()

    # Screen setup
    display_size = (800, 800)
    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode(display_size, flags=flags)

    # Map setup
    root_dir = Path(__file__).parent.parent
    dnd_map = pygame.image.load(root_dir / "test-map.png").convert_alpha()
    dnd_map.set_colorkey((255, 255, 255))
    dnd_map_size = dnd_map.get_size()
    orig_dnd_map = dnd_map.copy()
    map_offset = (0, 0)

    # Settings
    gridsize = orig_gridsize = 165
    fog_color = (0xCC, 0xCC, 0xCC)
    removed_fog: set[tuple[int, int]] = set()
    pieces: dict[tuple[int, int], tuple[int, int, int]] = {}
    moving: tuple[tuple[int, int], tuple[int, int, int]] | None = None
    camera = (0, 0)
    double_click = 0
    show_grid = True
    show_fog = True

    while True:
        double_click = double_click - 1 if double_click > 0 else 0

        mouse_pos = pygame.mouse.get_pos()
        # pressed_keys = pygame.key.get_pressed()
        pressed_modifiers = pygame.key.get_mods()
        pressed_buttons = pygame.mouse.get_pressed()
        mouse_speed = pygame.mouse.get_rel()

        for event in pygame.event.get():

            # Quit
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Hide/Show grid
                if event.key == pygame.K_g:
                    show_grid = not show_grid
                # Hide/Show fog
                if event.key == pygame.K_1:
                    show_fog = not show_fog

            # Zoom
            if event.type == pygame.MOUSEWHEEL:
                old_gridsize = gridsize
                if gridsize + event.y > 0:
                    gridsize = gridsize + event.y
                    camera_delta = zoom_at_mouse_pos(mouse_pos, camera, old_gridsize, gridsize)
                    camera = camera[0] - camera_delta[0], camera[1] - camera_delta[1]

                    scale = gridsize / orig_gridsize

                    # If ATL pressed, only change the grid size
                    if not (pressed_modifiers & pygame.KMOD_ALT):
                        dnd_map = pygame.transform.scale(
                            orig_dnd_map, (dnd_map_size[0] * scale, dnd_map_size[1] * scale)
                        )

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start moving a piece
                if event.button == pygame.BUTTON_LEFT and not any(pressed_modifiers & mod for mod in modifiers):
                    pos = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
                    if pos in pieces:
                        moving = pos, pieces[pos]

                if event.button == pygame.BUTTON_RIGHT:
                    pos = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                    # Remove piece
                    if double_click:
                        color = pieces.pop(pos, None)
                        if color in orig_colors:
                            colors.insert(0, color)

                    # Add a piece
                    else:
                        if pos not in pieces:
                            # Predefined color
                            if len(colors) > 0:
                                pieces[pos] = colors.pop(0)

                            # Random color
                            else:
                                pieces[pos] = (randint(0, 255), randint(0, 255), randint(0, 255))

                        double_click = 15

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop moving a piece
                if event.button == pygame.BUTTON_LEFT:
                    moving = None

            # Left mouse button
            if pressed_buttons[0]:

                # Moving a piece
                if moving is not None:
                    pos = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
                    if pos != moving[0] and pos not in pieces:
                        pieces.pop(moving[0], None)
                        pieces[pos] = moving[1]
                        moving = pos, moving[1]

                else:
                    # Move map
                    if pressed_modifiers & pygame.KMOD_ALT:
                        map_offset = map_offset[0] - mouse_speed[0], map_offset[1] - mouse_speed[1]

                    # Add and remove fog
                    if pressed_modifiers & pygame.KMOD_CTRL:
                        pos = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                        if pressed_modifiers & pygame.KMOD_SHIFT:
                            removed_fog.discard(pos)
                        else:
                            removed_fog.add(pos)

            # Middle mouse button
            if pressed_buttons[1]:
                # Move camera
                camera = camera[0] - mouse_speed[0], camera[1] - mouse_speed[1]

        display.fill(fog_color)

        display.blit(dnd_map, draw_position((0, 0), camera, gridsize, offset=map_offset))

        if show_grid:
            draw_grid(display, camera, gridsize)

        for (x, y), color in pieces.items():
            pygame.draw.circle(
                display,
                color,
                draw_position((x + 0.5, y + 0.5), camera, gridsize),
                (7 * gridsize) // 16,
            )

        if show_fog:
            draw_fog(display, camera, gridsize, removed_fog)

        pygame.display.flip()

        with true_fps.track():
            clock.tick(frame_rate)


if __name__ == "__main__":
    # parser = ArgumentParser()
    # parser.add_argument("file")
    #
    # args = parser.parse_args()
    #
    # print(args)

    main()
