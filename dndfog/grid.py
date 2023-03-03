from dndfog.math import approx


def draw_position_on_grid(
    position: tuple[float, float],
    camera: tuple[int, int],
    gridsize: int,
    offset: tuple[float, float] = (0, 0),
) -> tuple[int, int]:
    return (
        int((position[0] * gridsize) - camera[0] - (offset[0] * gridsize)),
        int((position[1] * gridsize) - camera[1] - (offset[1] * gridsize)),
    )


def grid_position(
    position: tuple[int, int],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int]:
    return approx((position[0] + camera[0]) / gridsize), approx((position[1] + camera[1]) / gridsize)
