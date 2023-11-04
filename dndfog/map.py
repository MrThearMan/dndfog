import pygame


def zoom_map(
    image: pygame.Surface,
    original_image: pygame.Surface,
    old_gridsize: int,
    new_gridsize: int,
) -> pygame.Surface:
    cur_x, cur_y = image.get_size()
    rel_x, rel_y = cur_x / old_gridsize, cur_y / old_gridsize
    new_x, new_y = max(round(rel_x * new_gridsize), 1), max(round(rel_y * new_gridsize), 1)
    return pygame.transform.scale(original_image, (new_x, new_y))


def move_map(
    image_offset: tuple[float, float],
    gridsize: int,
    mouse_speed: tuple[int, int],
) -> tuple[float, float]:
    return (
        round(image_offset[0] - (mouse_speed[0] / gridsize), 2),
        round(image_offset[1] - (mouse_speed[1] / gridsize), 2),
    )
