__all__ = [
    "draw_position",
    "grid_position",
    "zoom_at_mouse_pos",
]


def approx(value: int | float, /) -> int:
    return int(value) if value > 0 else int(value - 1)


def draw_position(
    pos: tuple[int | float, int | float],
    camera: tuple[int, int],
    gridsize: int,
    offset: tuple[float, float] = (0, 0),
) -> tuple[int, int]:
    return (
        int((pos[0] * gridsize) - camera[0] - (offset[0] * gridsize)),
        int((pos[1] * gridsize) - camera[1] - (offset[1] * gridsize)),
    )


def grid_position(
    pos: tuple[int, int],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int]:
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
