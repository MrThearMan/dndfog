from math import sqrt
from random import randint
from typing import TypedDict

import pygame

from dndfog.types import Glow


class AreaOfEffectData(TypedDict):
    origin: tuple[float, float]
    glow: Glow


def add_aoe(
    mouse_pos: tuple[int, int],
    aoes: dict[tuple[float, float], AreaOfEffectData],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[tuple[float, float], AreaOfEffectData] | None:
    aoe_pos = round((mouse_pos[0] + camera[0]) / gridsize, 2), round((mouse_pos[1] + camera[1]) / gridsize, 2)
    color = pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255), 100)
    radius = gridsize // 2
    aoes[aoe_pos] = AreaOfEffectData(
        origin=aoe_pos,
        glow=Glow(
            radius_range=range(radius, radius - 1, -1),
            inner_color=color,
            outer_color=color,
        ),
    )
    return aoe_pos, aoes[aoe_pos]


def make_aoe(
    origin: tuple[float, float],
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    aoe: AreaOfEffectData,
    aoes: dict[tuple[float, float], AreaOfEffectData],
    gridsize: int,
) -> tuple[tuple[float, float], AreaOfEffectData] | None:
    aoe_pos = aoe["origin"]
    making_aoe = aoe_pos, aoe
    dist = int(
        sqrt(
            (((origin[0] * gridsize) - (mouse_pos[0] + camera[0])) ** 2)
            + (((origin[1] * gridsize) - (mouse_pos[1] + camera[1])) ** 2)
        )
    )
    radius = max(dist, gridsize // 2)

    if radius != 0:
        aoes[aoe_pos] = AreaOfEffectData(
            origin=aoe_pos,
            glow=Glow(
                radius_range=range(radius, radius - 1, -1),
                inner_color=aoe["glow"].inner_color,
                outer_color=aoe["glow"].outer_color,
            ),
        )
        making_aoe = aoe_pos, aoes[aoe_pos]

    return making_aoe


def remove_aoe(
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    aoes: dict[tuple[float, float], AreaOfEffectData],
    gridsize: int,
) -> None:
    to_remove: set[tuple[float, float]] = set()
    for origin, aoe_data in aoes.items():
        radius = aoe_data["glow"].radius
        dist = sqrt(
            (((origin[0] * gridsize) - (mouse_pos[0] + camera[0])) ** 2)
            + (((origin[1] * gridsize) - (mouse_pos[1] + camera[1])) ** 2)
        )

        if dist <= radius:
            to_remove.add(origin)

    for origin in to_remove:
        aoes.pop(origin, None)


def scale_aoes(
    aoes: dict[tuple[float, float], AreaOfEffectData],
    new_gridsize: int,
    old_gridsize: int,
) -> None:
    for place, aoe in aoes.items():
        cur_radius = aoes[place]["glow"].radius
        rel_grid_radius = round(cur_radius / old_gridsize, 2)
        new_radius = max(int(rel_grid_radius * new_gridsize), max(new_gridsize // 2, 1))

        aoes[place]["glow"] = Glow(
            radius_range=range(new_radius, new_radius - 1, -1),
            inner_color=aoe["glow"].inner_color,
            outer_color=aoe["glow"].outer_color,
        )


class AreaOfEffectSaveData(TypedDict):
    origin: tuple[float, float]
    radius: int
    color: tuple[int, int, int, int]
