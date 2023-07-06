import sys

import pygame

from dndfog.camera import move_camera, zoom_camera
from dndfog.fog import add_fog, remove_fog
from dndfog.grid import grid_position
from dndfog.map import move_map, zoom_map
from dndfog.markings import add_markings, move_markings, remove_markings
from dndfog.piece import add_piece, move_piece, remove_piece
from dndfog.saving import get_default_filename, open_data_file, open_file_dialog, save_data_file, save_file_dialog
from dndfog.toolbar import (
    TOOLBAR_HEIGHT,
    select_button,
    select_checkbox,
    select_indicator,
    select_size_tool,
    set_indicator,
)
from dndfog.types import (
    COLOR_MAP,
    Event,
    KeyEvent,
    LoopData,
    MouseButtonEvent,
    MouseWheelEvent,
    PlacingKey,
    ProgramState,
    Tool,
)


def handle_event(event: Event, loop: LoopData, state: ProgramState) -> None:  # noqa: C901
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    elif event.type == pygame.KEYDOWN:
        handle_key_down(event, loop, state)

    elif event.type == pygame.MOUSEWHEEL:
        handle_mouse_wheel(event, loop, state)

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == pygame.BUTTON_LEFT:
            handle_left_mouse_button_down(event, loop, state)
        elif event.button == pygame.BUTTON_RIGHT:
            handle_right_mouse_button_down(event, loop, state)

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == pygame.BUTTON_LEFT:
            handle_left_mouse_button_up(event, loop, state)
        elif event.button == pygame.BUTTON_RIGHT:
            handle_right_mouse_button_up(event, loop, state)

    elif loop.pressed_buttons[0]:
        handle_hold_left_mouse_button(event, loop, state)

    elif loop.pressed_buttons[1]:
        handle_middle_mouse_button_held(event, loop, state)

    elif loop.pressed_buttons[2]:
        handle_right_mouse_button_held(event, loop, state)


def handle_key_down(event: KeyEvent, loop: LoopData, state: ProgramState) -> None:
    # Save data
    if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
        if event.mod & pygame.KMOD_SHIFT or state.file is None:
            filename = get_default_filename(state)

            file = save_file_dialog(
                title="Save Map",
                ext=[
                    ("DND fog file", "dndfog"),
                    ("Json file", "json"),
                ],
                default_name=filename,
                default_ext="dndfog",
            )
            if file:
                state.file = file
                save_data_file(state)
        else:
            save_data_file(state)

    # Load data
    elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_o:
        path = open_file_dialog(
            title="Open Map",
            ext=[
                ("DND fog file", "dndfog"),
                ("Json file", "json"),
            ],
            default_ext="dndfog",
        )
        if path:
            state.file = path
            open_data_file(state)

    # Hide/Show toolbar
    elif event.key == pygame.K_TAB:
        state.show.toolbar = not state.show.toolbar

    # Hide/Show grid
    elif event.key == pygame.K_F1:
        state.show.grid = not state.show.grid

    # Hide/Show fog
    elif event.key == pygame.K_F2:
        state.show.fog = not state.show.fog

    # Tool quickselect (1-9)
    elif (tool_index := event.key - pygame.K_1) in Tool.values():
        state.selected.tool = Tool(tool_index)


def handle_mouse_wheel(event: MouseWheelEvent, loop: LoopData, state: ProgramState) -> None:
    # Zoom map
    old_gridsize = state.map.gridsize
    if state.map.gridsize + event.y > 0:
        state.map.gridsize = state.map.gridsize + event.y
        old_camera = state.map.camera

        state.map.camera = zoom_camera(
            camera=state.map.camera,
            mouse_position=loop.mouse_pos,
            new_gridsize=state.map.gridsize,
            old_gridsize=old_gridsize,
        )

        move_markings(old_camera, state)

        if state.selected.tool != Tool.grid:
            state.map.image = zoom_map(
                image=state.map.image,
                original_image=state.map.original_image,
                old_gridsize=old_gridsize,
                new_gridsize=state.map.gridsize,
            )


def handle_left_mouse_button_down(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:  # noqa: C901
    # Select a tool from the toolbar
    if state.show.toolbar and 0 <= loop.mouse_pos[1] < TOOLBAR_HEIGHT:
        item_clicked, _ = grid_position(loop.mouse_pos, (0, 0), TOOLBAR_HEIGHT)
        try:
            state.selected.tool = Tool(item_clicked)
        except ValueError:
            pass

    # Use an option from the toolbar
    elif state.show.toolbar and TOOLBAR_HEIGHT <= loop.mouse_pos[1] < TOOLBAR_HEIGHT * 2:
        if state.selected.tool == Tool.piece:
            state.selected.piece_size = select_size_tool(loop.mouse_pos, state.selected.piece_size)

        elif state.selected.tool == Tool.fog:
            state.show.fog = select_checkbox(PlacingKey.fog_checkbox, loop.mouse_pos, state.show.fog)
            state.selected.fog = select_size_tool(loop.mouse_pos, state.selected.fog)

        elif state.selected.tool == Tool.grid:
            state.show.grid = select_checkbox(PlacingKey.grid_checkbox, loop.mouse_pos, state.show.grid)

        elif state.selected.tool == Tool.mark:
            if select_button(PlacingKey.clear_markings, loop.mouse_pos):
                state.map.markings = {}
            state.selected.marker_size = select_size_tool(loop.mouse_pos, state.selected.marker_size)
            if select_indicator(PlacingKey.marker_color, loop.mouse_pos):
                state.selected.indicator = PlacingKey.marker_color

    # Move piece
    elif state.selected.tool == Tool.piece:
        if loop.grid_pos in state.map.pieces:
            state.selected.piece = loop.grid_pos

    # Add fog
    elif state.selected.tool == Tool.fog:
        add_fog(state.map.removed_fog, loop.mouse_pos, state.map.camera, state.map.gridsize, state.selected.fog)

    # Add markings
    elif state.selected.tool == Tool.mark:
        add_markings(loop.mouse_pos, state)


def handle_right_mouse_button_down(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    # Add or remove piece
    if state.selected.tool == Tool.piece:
        if loop.grid_pos in state.map.pieces:
            remove_piece(loop.grid_pos, state.map.pieces, state.colors)
        else:
            add_piece(loop.grid_pos, state.map.pieces, state.colors, state.selected.piece_size)

    # Remove fog
    elif state.selected.tool == Tool.fog:
        remove_fog(state.map.removed_fog, loop.mouse_pos, state.map.camera, state.map.gridsize, state.selected.fog)

    # Remove markings
    elif state.selected.tool == Tool.mark:
        remove_markings(loop.mouse_pos, state)


def handle_left_mouse_button_up(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    state.selected.piece = None
    state.map.last_marking = None
    state.selected.indicator = None


def handle_right_mouse_button_up(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    pass


def handle_hold_left_mouse_button(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    if state.selected.tool == Tool.piece:
        if state.selected.piece is not None:
            state.selected.piece = move_piece(state.selected.piece, loop.grid_pos, state.map.pieces)

    elif state.selected.tool == Tool.fog:
        add_fog(state.map.removed_fog, loop.mouse_pos, state.map.camera, state.map.gridsize, state.selected.fog)

    elif state.selected.tool == Tool.map:
        state.map.image_offset = move_map(state.map.image_offset, state.map.gridsize, loop.mouse_speed)

    elif state.selected.tool == Tool.mark:
        if state.map.last_marking is not None:  # don't pass any possible hold events after mouse up
            add_markings(loop.mouse_pos, state)
        elif state.selected.indicator == PlacingKey.marker_color:
            pos = set_indicator(PlacingKey.marker_color, loop.mouse_pos[0])
            state.selected.marker_color = COLOR_MAP[pos]


def handle_middle_mouse_button_held(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    # Move camera
    state.map.camera = move_camera(state.map.camera, loop.mouse_speed)


def handle_right_mouse_button_held(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    if state.selected.tool == Tool.fog:
        remove_fog(state.map.removed_fog, loop.mouse_pos, state.map.camera, state.map.gridsize, state.selected.fog)

    elif state.selected.tool == Tool.mark:
        remove_markings(loop.mouse_pos, state)
