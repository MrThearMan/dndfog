import pygame


def approx(value: float, /) -> int:
    return int(value) if value > 0 else int(value - 1)


def distance_between_points(point_1: tuple[int, int], point_2: tuple[int, int]) -> float:
    return ((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2) ** 0.5


def color_tuple_from_hsla(hsla: tuple[int, int, int, int]) -> tuple[int, int, int]:
    color = pygame.Color(0)
    color.hsla = hsla
    return color.r, color.g, color.b
