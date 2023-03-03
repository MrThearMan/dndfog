import sys

import pygame

from dndfog.camera import move_camera, zoom_camera
from dndfog.fog import add_fog, remove_fog
from dndfog.grid import grid_position
from dndfog.map import move_map, zoom_map
from dndfog.piece import add_piece, move_piece, remove_piece
from dndfog.saving import open_data_file, open_file_dialog, save_data_file
from dndfog.toolbar import TOOLBAR_HEIGHT, select_fog_checkbox, select_fog_size, select_grid_checkbox, select_piece_size
from dndfog.types import Event, KeyEvent, LoopData, MouseButtonEvent, MouseWheelEvent, ProgramState, Tool


def handle_event(event: Event, loop: LoopData, state: ProgramState) -> None:
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
        save_data_file(state=state)

    # Load data
    elif event.mod & pygame.KMOD_CTRL and event.key == pygame.K_o:
        openpath = open_file_dialog(title="Open Map", ext=[("Json file", "json")], default_ext="json")
        if openpath:
            open_data_file(openpath, state)

    # Hide/Show toolbar
    elif event.key == pygame.K_TAB:
        state.show.toolbar = not state.show.toolbar

    # Hide/Show grid
    elif event.key == pygame.K_F1:
        state.show.grid = not state.show.grid

    # Hide/Show fog
    elif event.key == pygame.K_F12:
        state.show.fog = not state.show.fog

    # Tool quickselect (1-9)
    elif (tool_index := event.key - pygame.K_1) in Tool.values():
        state.selected.tool = Tool(tool_index)


def handle_mouse_wheel(event: MouseWheelEvent, loop: LoopData, state: ProgramState) -> None:
    # Zoom map
    old_gridsize = state.map.gridsize
    if state.map.gridsize + event.y > 0:
        state.map.gridsize = state.map.gridsize + event.y
        state.map.camera = zoom_camera(
            camera=state.map.camera,
            mouse_position=loop.mouse_pos,
            new_gridsize=state.map.gridsize,
            old_gridsize=old_gridsize,
        )
        if not loop.pressed_modifiers & pygame.KMOD_ALT:
            state.map.image = zoom_map(
                image=state.map.image,
                original_image=state.map.original_image,
                old_gridsize=old_gridsize,
                new_gridsize=state.map.gridsize,
            )


def handle_left_mouse_button_down(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
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
            state.selected.size = select_piece_size(loop.mouse_pos, state.selected.size)
        elif state.selected.tool == Tool.fog:
            state.show.fog = select_fog_checkbox(loop.mouse_pos, state.show.fog)
            state.selected.fog = select_fog_size(loop.mouse_pos, state.selected.fog)
        elif state.selected.tool == Tool.grid:
            state.show.grid = select_grid_checkbox(loop.mouse_pos, state.show.grid)

    # Move piece
    elif state.selected.tool == Tool.piece:
        if loop.grid_pos in state.map.pieces:
            state.selected.piece = loop.grid_pos


def handle_right_mouse_button_down(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    if state.selected.tool == Tool.piece:
        if loop.grid_pos in state.map.pieces:
            remove_piece(loop.grid_pos, state.map.pieces, state.colors)
        else:
            add_piece(loop.grid_pos, state.map.pieces, state.colors, state.selected.size)


def handle_left_mouse_button_up(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    # Stop moving a piece
    state.selected.piece = None


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


def handle_middle_mouse_button_held(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    # Move camera
    state.map.camera = move_camera(state.map.camera, loop.mouse_speed)


def handle_right_mouse_button_held(event: MouseButtonEvent, loop: LoopData, state: ProgramState) -> None:
    if state.selected.tool == Tool.fog:
        remove_fog(state.map.removed_fog, loop.mouse_pos, state.map.camera, state.map.gridsize, state.selected.fog)
