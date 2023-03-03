from enum import Enum

from dndfog.math import distance_between_points
from dndfog.types import FogSize, PieceSize

TOOLBAR_HEIGHT: int = 50


class TBCacheKey(str, Enum):
    grid_checkbox = "grid_checkbox"
    fog_checkbox = "fog_checkbox"
    fog_size = "fog_size"
    piece_size = "piece_size"


_TOOL_OFFSET_CACHE: dict[TBCacheKey, int] = {}


def get_or_set_offset_cache(key: TBCacheKey, offset: int | None) -> int:
    if offset is not None:
        _TOOL_OFFSET_CACHE[key] = offset
    else:
        offset = _TOOL_OFFSET_CACHE[key]
    return offset


# Size tool


def get_size_tool_placing(key: TBCacheKey, offset: int | None = None) -> list[tuple[tuple[int, int], int]]:
    """Size tool centers and radii."""
    result: list[tuple[tuple[int, int], int]] = []
    offset = get_or_set_offset_cache(key, offset)
    x = offset + (TOOLBAR_HEIGHT // 5) - (TOOLBAR_HEIGHT // 20)
    for i in range(4):
        radius = (TOOLBAR_HEIGHT // 5) + ((TOOLBAR_HEIGHT // 20) * i)
        x += radius + (TOOLBAR_HEIGHT // 20)
        result.append(((x, int(TOOLBAR_HEIGHT * 1.5)), radius))
        x += radius + (TOOLBAR_HEIGHT // 20)

    return result


def select_piece_size(mouse_pos: tuple[int, int], selected_size: PieceSize) -> PieceSize:
    for i, (center, radius) in enumerate(get_size_tool_placing(TBCacheKey.piece_size)):
        dist = distance_between_points(center, mouse_pos)
        if dist < radius:
            return PieceSize(i + 1)
    return selected_size


def select_fog_size(mouse_pos: tuple[int, int], selected_size: FogSize) -> FogSize:
    for i, (center, radius) in enumerate(get_size_tool_placing(TBCacheKey.fog_size)):
        dist = distance_between_points(center, mouse_pos)
        if dist < radius:
            return FogSize(i + 1)
    return selected_size


# Checkbox tool


def get_checkbox_tool_placing(key: TBCacheKey, offset: int | None = None) -> tuple[tuple[int, int], int]:
    """Checkbox center and radius."""
    offset = get_or_set_offset_cache(key, offset)
    return (offset + (TOOLBAR_HEIGHT // 5) * 2, int(TOOLBAR_HEIGHT * 1.5)), TOOLBAR_HEIGHT // 5


def select_grid_checkbox(mouse_pos: tuple[int, int], show_grid: bool):
    center, radius = get_checkbox_tool_placing(TBCacheKey.grid_checkbox)
    dist = distance_between_points(center, mouse_pos)
    if dist < radius:
        return not show_grid
    return show_grid


def select_fog_checkbox(mouse_pos: tuple[int, int], show_fog: bool) -> bool:
    center, radius = get_checkbox_tool_placing(TBCacheKey.fog_checkbox)
    dist = distance_between_points(center, mouse_pos)
    if dist < radius:
        return not show_fog
    return show_fog
