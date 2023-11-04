from typing import Any, Generator

from dndfog.types import MarkingData, Markings, ProgramState


def add_markings(mouse_pos: tuple[int, int], state: ProgramState) -> None:
    position = (mouse_pos[0] + state.map.camera[0], mouse_pos[1] + state.map.camera[1])

    for marking in interpolate_line(position, state.map.last_marking):
        state.map.markings[marking] = MarkingData(
            place=marking,
            size=state.selected.marker_size,
            color=state.selected.marker_color,
        )

    state.map.last_marking = position


def remove_markings(mouse_pos: tuple[int, int], state: ProgramState) -> None:
    size = state.selected.marker_size.value * 10
    low = 0 - size // 2
    high = size - size // 2
    for x in range(low, high):
        for y in range(low, high):
            position = (mouse_pos[0] + state.map.camera[0] + x, mouse_pos[1] + state.map.camera[1] + y)
            state.map.markings.pop(position, None)


def move_markings(old_camera: tuple[int, int], state: ProgramState) -> None:
    dx = state.map.camera[0] - old_camera[0]
    dy = state.map.camera[1] - old_camera[1]
    new_markings: Markings = {}
    for marking, data in state.map.markings.items():
        data["place"] = (marking[0] + dx, marking[1] + dy)
        new_markings[data["place"]] = data
    state.map.markings = new_markings


def interpolate_line(
    point_1: tuple[int, int],
    point_2: tuple[int, int] | None,
) -> Generator[tuple[int, int], Any, None]:
    """Interpolate a line with points using Bresenham's line algorithm."""
    point_2 = point_2 if point_2 is not None else point_1

    if abs(point_2[1] - point_1[1]) < abs(point_2[0] - point_1[0]):
        if point_1[0] > point_2[0]:
            yield from _interpolate_low(point_2, point_1)
        yield from _interpolate_low(point_1, point_2)

    if point_1[1] > point_2[1]:
        yield from _interpolate_high(point_2, point_1)
    yield from _interpolate_high(point_1, point_2)


def _interpolate_high(point_1: tuple[int, int], point_2: tuple[int, int]) -> Generator[tuple[int, int], Any, None]:
    dx = point_2[0] - point_1[0]
    dy = point_2[1] - point_1[1]
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    dist = (2 * dx) - dy
    x = point_1[0]

    for y in range(point_1[1], point_2[1] + 1):
        yield x, y
        if dist > 0:
            x = x + xi
            dist = dist + (2 * (dx - dy))
        else:
            dist = dist + 2 * dx


def _interpolate_low(point_1: tuple[int, int], point_2: tuple[int, int]) -> Generator[tuple[int, int], Any, None]:
    dx = point_2[0] - point_1[0]
    dy = point_2[1] - point_1[1]
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    dist = (2 * dy) - dx
    y = point_1[1]

    for x in range(point_1[0], point_2[0] + 1):
        yield x, y
        if dist > 0:
            y = y + yi
            dist = dist + (2 * (dy - dx))
        else:
            dist = dist + 2 * dy
