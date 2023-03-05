from typing import overload

from dndfog.math import distance_between_points
from dndfog.types import FogSize, MarkerSize, PieceSize, PlacingKey

TOOLBAR_HEIGHT: int = 50
TOOLBAR_MIDDLE: int = TOOLBAR_HEIGHT + TOOLBAR_HEIGHT // 2
INDICATOR_WIDTH: int = 300

_TOOL_OFFSET_CACHE: dict[PlacingKey, int] = {}
_INDICATOR_CACHE: dict[PlacingKey, int] = {}


def get_or_set_offset_cache(key: PlacingKey, offset: int | None) -> int:
    if offset is not None:
        _TOOL_OFFSET_CACHE[key] = offset
        return offset
    return _TOOL_OFFSET_CACHE[key]


# Placing functions


def get_placing_found_circles(key: PlacingKey, offset: int | None = None) -> list[tuple[tuple[int, int], int]]:
    """Four circle centers and radii."""
    result: list[tuple[tuple[int, int], int]] = []
    offset = get_or_set_offset_cache(key, offset)
    x = offset + (TOOLBAR_HEIGHT // 5) - (TOOLBAR_HEIGHT // 20)
    for i in range(4):
        radius = (TOOLBAR_HEIGHT // 5) + ((TOOLBAR_HEIGHT // 20) * i)
        x += radius + (TOOLBAR_HEIGHT // 20)
        result.append(((x, int(TOOLBAR_HEIGHT * 1.5)), radius))
        x += radius + (TOOLBAR_HEIGHT // 20)

    return result


def get_placing_single_circle(key: PlacingKey, offset: int | None = None) -> tuple[tuple[int, int], int]:
    """Single circle center and radius."""
    offset = get_or_set_offset_cache(key, offset)
    return (offset + (TOOLBAR_HEIGHT // 5) * 2, int(TOOLBAR_HEIGHT * 1.5)), TOOLBAR_HEIGHT // 5


def set_indicator(key: PlacingKey, mouse_x: int) -> int:
    offset = get_or_set_offset_cache(key, None)
    x = max(min(mouse_x - offset, INDICATOR_WIDTH), 0)
    _INDICATOR_CACHE[key] = x
    return _INDICATOR_CACHE[key]


def get_indicator_placing(key: PlacingKey, offset: int | None = None) -> tuple[int, int]:
    offset = get_or_set_offset_cache(key, offset)
    return _INDICATOR_CACHE.setdefault(key, 0) + offset, TOOLBAR_HEIGHT // 6


# Tools selections


_SIZE_KEY_MAP = {
    PieceSize: PlacingKey.piece_size,
    FogSize: PlacingKey.fog_size,
    MarkerSize: PlacingKey.marker_size,
}


@overload
def select_size_tool(mouse_pos: tuple[int, int], selected_size: PieceSize) -> PieceSize:
    pass


@overload
def select_size_tool(mouse_pos: tuple[int, int], selected_size: FogSize) -> FogSize:
    pass


@overload
def select_size_tool(mouse_pos: tuple[int, int], selected_size: MarkerSize) -> MarkerSize:
    pass


def select_size_tool(mouse_pos, selected_size):
    enum_type = type(selected_size)
    cache_key = _SIZE_KEY_MAP[enum_type]
    placing = get_placing_found_circles(cache_key)
    for (center, radius), size in zip(placing, enum_type.values(), strict=True):
        dist = distance_between_points(center, mouse_pos)
        if dist < radius:
            return enum_type(size)
    return selected_size


def select_checkbox(key: PlacingKey, mouse_pos: tuple[int, int], show: bool):
    center, radius = get_placing_single_circle(key)
    dist = distance_between_points(center, mouse_pos)
    if dist < radius:
        return not show
    return show


def select_button(key: PlacingKey, mouse_pos: tuple[int, int]) -> bool:
    center, radius = get_placing_single_circle(key)
    dist = distance_between_points(center, mouse_pos)
    if dist < radius:
        return True
    return False


def select_indicator(key: PlacingKey, mouse_pos: tuple[int, int]) -> bool:
    x, radius = get_indicator_placing(key)
    dist = distance_between_points((x, TOOLBAR_MIDDLE), mouse_pos)
    if dist < radius:
        return True
    return False
