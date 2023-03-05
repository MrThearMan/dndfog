from functools import cache
from typing import Any

import pygame

from dndfog.math import color_tuple_from_hsla
from dndfog.types import COLOR_MAP, font


def draw_rect_transparent(
    display: pygame.Surface,
    dest: tuple[int, int],
    size: tuple[int, int],
    color: tuple[int, int, int, int],
    rect: tuple[int, int, int, int],
    **kwargs: Any,
) -> None:
    temp = pygame.Surface(size, flags=pygame.SRCALPHA)
    pygame.draw.rect(temp, color=color, rect=rect, **kwargs)
    display.blit(temp, dest)


def draw_text_centered(
    display: pygame.Surface,
    text: str,
    rect: tuple[int, int, int, int],
    color=(222, 222, 222),
) -> int:
    """Draw text in the center of the given rectangle."""
    text_box = font.render(text, True, color)
    width, height = text_box.get_size()
    x = (rect[2] - width) // 2
    y = (rect[3] - height) // 2
    display.blit(text_box, (rect[0] + x, rect[1] + y))
    # Return the right edge of the text
    return rect[0] + x + width


@cache
def color_slider(size: tuple[int, int]) -> pygame.Surface:
    image = pygame.Surface(size)

    COLOR_MAP[0] = (0, 0, 0)
    COLOR_MAP[size[0] - 1] = (255, 255, 255)
    COLOR_MAP[size[0]] = (255, 255, 255)
    pygame.draw.rect(image, (0, 0, 0), (0, 0, 1, size[1]))
    pygame.draw.rect(image, (255, 255, 255), (size[0] - 1, 0, 1, size[1]))

    for i in range(1, size[0] - 1):
        color = color_tuple_from_hsla((int(360 * i / 300), 100, 50, 100))
        COLOR_MAP[i] = color
        pygame.draw.rect(image, color, (i, 0, 1, size[1]))

    return image
