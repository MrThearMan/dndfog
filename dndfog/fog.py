from dndfog.grid import grid_position
from dndfog.types import FogSize


def add_fog(
    removed_fog: set[tuple[int, int]],
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    gridsize: int,
    selected_fog: FogSize,
) -> None:
    start_x = mouse_pos[0] - (gridsize // 2 * (selected_fog.value - 1))
    start_y = mouse_pos[1] - (gridsize // 2 * (selected_fog.value - 1))

    for x in range(selected_fog.value):
        for y in range(selected_fog.value):
            pos = grid_position((start_x + (x * gridsize), start_y + (y * gridsize)), camera, gridsize)
            removed_fog.discard(pos)


def remove_fog(
    removed_fog: set[tuple[int, int]],
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    gridsize: int,
    selected_fog: FogSize,
) -> None:
    start_x = mouse_pos[0] - (gridsize // 2 * (selected_fog.value - 1))
    start_y = mouse_pos[1] - (gridsize // 2 * (selected_fog.value - 1))

    for x in range(selected_fog.value):
        for y in range(selected_fog.value):
            pos = grid_position((start_x + (x * gridsize), start_y + (y * gridsize)), camera, gridsize)
            removed_fog.add(pos)
