import pygame


def zoom_camera(
    camera: tuple[int, int],
    mouse_position: tuple[int, int],
    new_gridsize: int,
    old_gridsize: int,
) -> tuple[int, int]:
    camera_delta = zoom_at_mouse_pos(mouse_position, camera, old_gridsize, new_gridsize)
    return camera[0] - camera_delta[0], camera[1] - camera_delta[1]


def move_camera(
    camera: tuple[int, int],
    mouse_speed: tuple[int, int],
) -> tuple[int, int]:
    return camera[0] - mouse_speed[0], camera[1] - mouse_speed[1]


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


def zoom_at_mouse_pos(
    mouse_position: tuple[int, int],
    camera: tuple[int, int],
    old_gridsize: int,
    new_gridsize: int,
) -> tuple[int, int]:
    absolute_mouse_position = mouse_position[0] + camera[0], mouse_position[1] + camera[1]

    old_grid_place = absolute_mouse_position[0] / old_gridsize, absolute_mouse_position[1] / old_gridsize
    new_grid_place = absolute_mouse_position[0] / new_gridsize, absolute_mouse_position[1] / new_gridsize

    return (
        round((new_grid_place[0] - old_grid_place[0]) * new_gridsize),
        round((new_grid_place[1] - old_grid_place[1]) * new_gridsize),
    )
