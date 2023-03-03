import copy

import pygame

from dndfog.camera import get_visible_area_limits
from dndfog.grid import draw_position_on_grid
from dndfog.types import Glow, MapData


def draw_map(display: pygame.Surface, map_data: MapData) -> None:
    display.blit(
        map_data.image,
        draw_position_on_grid((0, 0), map_data.camera, map_data.gridsize, offset=map_data.image_offset),
    )


def draw_grid(display: pygame.Surface, map_data: MapData) -> None:
    width, height = display.get_size()

    start_x, start_y, end_x, end_y = get_visible_area_limits(display, map_data.camera, map_data.gridsize)

    for x in range(start_x, end_x, map_data.gridsize):
        pygame.draw.line(display, map_data.grid_color, (x - map_data.camera[0], 0), (x - map_data.camera[0], height), 2)

    for y in range(start_y, end_y, map_data.gridsize):
        pygame.draw.line(display, map_data.grid_color, (0, y - map_data.camera[1]), (width, y - map_data.camera[1]), 2)


def draw_pieces(display: pygame.Surface, map_data: MapData) -> None:
    for (x, y), piece_data in map_data.pieces.items():
        if not piece_data["show"]:
            continue

        color = piece_data["color"]
        size = int(piece_data["size"])
        pygame.draw.circle(
            display,
            color=color,
            center=draw_position_on_grid((x + (0.5 * size), y + (0.5 * size)), map_data.camera, map_data.gridsize),
            radius=(7 * (map_data.gridsize * size)) // 16,
        )


def draw_fog(display: pygame.Surface, map_data: MapData) -> None:
    start_x, start_y, end_x, end_y = get_visible_area_limits(display, map_data.camera, map_data.gridsize)
    start_x, start_y, end_x, end_y = (
        start_x // map_data.gridsize,
        start_y // map_data.gridsize,
        end_x // map_data.gridsize,
        end_y // map_data.gridsize,
    )

    inner_color = pygame.Color(*map_data.fog_color)
    outer_color = copy.deepcopy(inner_color)
    outer_color.a = 0

    glow = Glow(
        radius_range=range(map_data.gridsize, map_data.gridsize // 2, -1),
        inner_color=inner_color,
        outer_color=outer_color,
    )

    for x in range(start_x, end_x, 1):
        for y in range(start_y, end_y, 1):
            if (x, y) in map_data.removed_fog:
                continue
            display.blit(next(glow), draw_position_on_grid((x - 0.5, y - 0.5), map_data.camera, map_data.gridsize))
