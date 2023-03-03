import pygame

from dndfog.draw.generic import draw_rect_transparent, draw_text_centered
from dndfog.grid import grid_position
from dndfog.math import distance_between_points
from dndfog.toolbar import TOOLBAR_HEIGHT, TBCacheKey, get_checkbox_tool_placing, get_size_tool_placing
from dndfog.types import FogSize, PieceSize, ProgramState, Tool


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
        draw_size_picker(display, mouse_pos, state.selected.size)

    elif state.selected.tool == Tool.fog:
        offset = draw_fog_checkbox(display, mouse_pos, state.show.fog)
        draw_fog_size_picker(display, mouse_pos, state.selected.fog, offset=offset)

    elif state.selected.tool == Tool.grid:
        draw_grid_checkbox(display, mouse_pos, state.show.grid)


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


def draw_size_picker(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    selected_size: PieceSize,
    offset: int = 0,
) -> int:
    edge = draw_text_centered(display, "size", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = 0, 0
    for i, (center, radius) in enumerate(get_size_tool_placing(TBCacheKey.piece_size, offset=edge)):
        dist = distance_between_points(center, mouse_pos)
        color = (66, 66, 66) if PieceSize(i + 1) == selected_size or dist < radius else (101, 101, 101)
        pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_fog_checkbox(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    show_fog: bool,
    offset: int = 0,
) -> int:
    edge = draw_text_centered(display, "show", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = get_checkbox_tool_placing(TBCacheKey.fog_checkbox, offset=edge)
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
    edge = draw_text_centered(display, "size", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = 0, 0
    for i, (center, radius) in enumerate(get_size_tool_placing(TBCacheKey.fog_size, offset=edge)):
        dist = distance_between_points(center, mouse_pos)
        color = (66, 66, 66) if FogSize(i + 1) == selected_size or dist < radius else (101, 101, 101)
        pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def draw_grid_checkbox(
    display: pygame.Surface,
    mouse_pos: tuple[int, int],
    show_grid: bool,
    offset: int = 0,
) -> int:
    edge = draw_text_centered(display, "show", rect=(offset, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT, TOOLBAR_HEIGHT))
    center, radius = get_checkbox_tool_placing(TBCacheKey.grid_checkbox, offset=edge)
    dist = distance_between_points(center, mouse_pos)
    color = (66, 66, 66) if show_grid or dist < radius else (101, 101, 101)
    pygame.draw.circle(display, color, center, radius=radius)
    return center[0] + radius


def __draw_color_picker(display: pygame.Surface) -> None:
    pos = 10
    width = 300
    height = 10
    image = pygame.Surface((width, height))
    for i in range(width):
        color = pygame.Color(0)
        color.hsla = (int(360 * i / width), 100, 50, 100)
        pygame.draw.rect(image, color, (i, 0, 1, height))

    display.blit(image, (pos, 70))
