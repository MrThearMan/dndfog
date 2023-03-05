import pygame

from dndfog.draw.generic import color_slider, draw_rect_transparent, draw_text_centered
from dndfog.grid import grid_position
from dndfog.math import distance_between_points
from dndfog.toolbar import (
    INDICATOR_WIDTH,
    TOOLBAR_HEIGHT,
    TOOLBAR_MIDDLE,
    get_indicator_placing,
    get_placing_found_circles,
    get_placing_single_circle,
)
from dndfog.types import FogSize, MarkerSize, PieceSize, PlacingKey, ProgramState, Tool


def draw_toolbar(display: pygame.Surface, mouse_pos: tuple[int, int], state: ProgramState) -> None:
    if not state.show.toolbar:
        return

    width: int = display.get_size()[0]
    height: int = TOOLBAR_HEIGHT

    # Toolbar background
    draw_rect_transparent(
        display,
        dest=(0, 0),
        size=(width, height * 2),
        color=(111, 111, 111, 240),
        rect=(0, 0, width, height * 2),
    )

    draw_tool_buttons(display, height, mouse_pos, state.selected.tool)

    if state.selected.tool == Tool.piece:
        draw_piece_size_picker(display, mouse_pos, state.selected.piece_size)

    elif state.selected.tool == Tool.fog:
        offset = draw_fog_checkbox(display, mouse_pos, state.show.fog)
        draw_fog_size_picker(display, mouse_pos, state.selected.fog, offset=offset)

    elif state.selected.tool == Tool.grid:
        draw_grid_checkbox(display, mouse_pos, state.show.grid)

    elif state.selected.tool == Tool.mark:
        offset = draw_clear_markings_button(display, mouse_pos)
        offset = draw_marker_size_picker(display, mouse_pos, state.selected.marker_size, offset)
        draw_color_picker(display, state.selected.marker_color, PlacingKey.marker_color, offset)


def draw_tool_buttons(
    display: pygame.Surface,
    button_size: int,
    mouse_pos: tuple[int, int],
    selected_tool: Tool,
) -> None:
    item_pos = grid_position(mouse_pos, (0, 0), button_size)

    tool: Tool
    for position, tool in enumerate(Tool):
        if item_pos == (position, 0) or position == selected_tool:
            draw_rect_transparent(
                display,
                dest=(position * button_size, 0),
                size=(button_size, button_size),
                color=(101, 101, 101, 240),
                rect=(1, 0, button_size - 1, button_size - 1),
                border_bottom_left_radius=15,
                border_bottom_right_radius=15,
            )

        draw_text_centered(display, tool.name, (position * button_size, 0, button_size, button_size))


def draw_piece_size_picker(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    selected_size: PieceSize,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "size", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = 0, 0
    placing = get_placing_found_circles(PlacingKey.piece_size, offset=offset)
    for (center, radius), piece_size in zip(placing, PieceSize.values(), strict=True):
        dist = distance_between_points(center, mouse_pos)
        color = (66, 66, 66) if piece_size == selected_size or dist < radius else (101, 101, 101)
        pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_fog_checkbox(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    show_fog: bool,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "show", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = get_placing_single_circle(PlacingKey.fog_checkbox, offset=offset)
    dist = distance_between_points(center, mouse_pos)
    color = (66, 66, 66) if show_fog or dist < radius else (101, 101, 101)
    pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_fog_size_picker(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    selected_size: FogSize,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "size", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = 0, 0
    placing = get_placing_found_circles(PlacingKey.fog_size, offset=offset)
    for (center, radius), fog_size in zip(placing, FogSize.values(), strict=True):
        dist = distance_between_points(center, mouse_pos)
        color = (66, 66, 66) if fog_size == selected_size or dist < radius else (101, 101, 101)
        pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_grid_checkbox(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    show_grid: bool,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "show", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = get_placing_single_circle(PlacingKey.grid_checkbox, offset=offset)
    dist = distance_between_points(center, mouse_pos)
    color = (66, 66, 66) if show_grid or dist < radius else (101, 101, 101)
    pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_clear_markings_button(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "clear", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = get_placing_single_circle(PlacingKey.clear_markings, offset=offset)
    dist = distance_between_points(center, mouse_pos)
    color = (66, 66, 66) if dist < radius else (101, 101, 101)
    pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_marker_size_picker(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    selected_size: MarkerSize,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "size", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    placing = get_placing_found_circles(PlacingKey.marker_size, offset=offset)
    center, radius = 0, 0
    for (center, radius), marker_size in zip(placing, MarkerSize.values(), strict=True):
        dist = distance_between_points(center, mouse_pos)
        color = (66, 66, 66) if marker_size == selected_size or dist < radius else (101, 101, 101)
        pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_color_picker(
    display: pygame.Surface,
    selected_color: tuple[int, int, int],
    indicator_key: PlacingKey,
    offset: int = 0,
) -> int:
    offset = draw_text_centered(display, "color", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    offset += TOOLBAR_HEIGHT // 4

    # Add color picker
    size = (INDICATOR_WIDTH, TOOLBAR_HEIGHT // 5)
    image = color_slider(size)
    display.blit(image, (offset, TOOLBAR_MIDDLE - size[1] // 2))

    # Add indicator
    x, radius = get_indicator_placing(indicator_key, offset)
    pygame.draw.circle(display, color=selected_color, center=(x, TOOLBAR_MIDDLE), radius=radius - 1)

    return offset + size[0]
