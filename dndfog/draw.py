import copy
import os
import sys
from math import sqrt
from random import randint

import pygame

from dndfog.saving import open_data_file, open_file_dialog, save_data_file
from dndfog.types import AreaOfEffectData, Glow, PieceData, orig_colors
from dndfog.utils import draw_position, grid_position, zoom_at_mouse_pos


def draw_grid(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
    color: tuple[int, int, int] = (0xC5, 0xC5, 0xC5),
) -> None:
    width, height = display.get_size()

    start_x, start_y, end_x, end_y = get_visible_area_limits(display, camera, gridsize)

    for x in range(start_x, end_x, gridsize):
        pygame.draw.line(display, color, (x - camera[0], 0), (x - camera[0], height), 2)

    for y in range(start_y, end_y, gridsize):
        pygame.draw.line(display, color, (0, y - camera[1]), (width, y - camera[1]), 2)


def draw_fog(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
    removed: set[tuple[int, int]],
    fog_color: tuple[int, int, int],
) -> None:
    start_x, start_y, end_x, end_y = get_visible_area_limits(display, camera, gridsize)
    start_x, start_y, end_x, end_y = start_x // gridsize, start_y // gridsize, end_x // gridsize, end_y // gridsize

    inner_color = pygame.Color(*fog_color)
    outer_color = copy.deepcopy(inner_color)
    outer_color.a = 0

    glow = Glow(
        radius_range=range(gridsize, gridsize // 2, -1),
        inner_color=inner_color,
        outer_color=outer_color,
    )

    for x in range(start_x, end_x, 1):
        for y in range(start_y, end_y, 1):
            if (x, y) in removed:
                continue
            display.blit(next(glow), draw_position((x - 0.5, y - 0.5), camera, gridsize))


def get_visible_area_limits(
    display: pygame.Surface,
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int, int, int]:
    width, height = display.get_size()
    start_x = ((camera[0] + gridsize - 1) // gridsize) * gridsize - 1
    start_y = ((camera[1] + gridsize - 1) // gridsize) * gridsize - 1
    end_x = start_x + width + gridsize
    end_y = start_y + height + gridsize
    return start_x, start_y, end_x, end_y


def draw_pieces(
    display: pygame.Surface,
    pieces: dict[tuple[int, int], PieceData],
    camera: tuple[int, int],
    gridsize: int,
) -> None:
    for (x, y), piece_data in pieces.items():
        if not piece_data["show"]:
            continue

        color = piece_data["color"]
        size = piece_data["size"]
        pygame.draw.circle(
            display,
            color=color,
            center=draw_position((x + (0.5 * size), y + (0.5 * size)), camera, gridsize),
            radius=(7 * (gridsize * size)) // 16,
        )


def draw_aoes(
    display: pygame.Surface,
    aoes: dict[tuple[float, float], AreaOfEffectData],
    camera: tuple[int, int],
    gridsize: int,
) -> None:
    for (x, y), aoe_data in aoes.items():
        glow = next(aoe_data["glow"])
        size = glow.get_size()
        gsx, gsy = (size[0] / gridsize) / 2, (size[1] / gridsize) / 2

        dest = draw_position((x - gsx, y - gsy), camera, gridsize)

        display.blit(glow, dest)


def add_piece(
    add_place: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    colors: list[tuple[int, int, int]],
    selected_size: int,
) -> None:
    no_overlap_with_other_pieces = not any(
        (add_place[0] + x, add_place[1] + y) in pieces for x in range(selected_size) for y in range(selected_size)
    )
    if no_overlap_with_other_pieces:
        color = (
            # Prefedined Color
            colors.pop(0)
            if len(colors) > 0
            # Random Color
            else (randint(0, 255), randint(0, 255), randint(0, 255))
        )

        for x in range(selected_size):
            for y in range(selected_size):
                pieces[(add_place[0] + x, add_place[1] + y)] = PieceData(
                    parent=add_place,
                    place=(add_place[0] + x, add_place[1] + y),
                    color=color,
                    size=selected_size,
                    show=(x == 0 and y == 0),
                )


def remove_piece(
    next_place: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    colors: list[tuple[int, int, int]],
) -> None:
    piece_data: PieceData | None = pieces.get(next_place, None)
    if piece_data is not None:
        place = piece_data["parent"]
        size = piece_data["size"]
        color = piece_data["color"]

        for x in range(size):
            for y in range(size):
                pieces.pop((place[0] + x, place[1] + y), None)
                if color in orig_colors and color not in colors:
                    colors.insert(0, color)


def move_piece(
    current_place: tuple[int, int],
    next_place: tuple[int, int],
    piece_to_move: PieceData,
    pieces: dict[tuple[int, int], PieceData],
) -> tuple[tuple[int, int], PieceData]:
    piece_place = piece_to_move["parent"]
    piece_size = piece_to_move["size"]

    movement = (next_place[0] - current_place[0], next_place[1] - current_place[1])
    current_self_positions = {
        (piece_place[0] + x, piece_place[1] + y) for x in range(piece_size) for y in range(piece_size)
    }
    next_self_positions = {(x + movement[0], y + movement[1]) for x, y in current_self_positions}
    no_overlap_with_other_pieces = not any(
        pos in pieces for pos in next_self_positions if pos not in current_self_positions
    )

    moving = current_place, piece_to_move

    if next_place != current_place and no_overlap_with_other_pieces:
        # Remove own positions
        for self_pos in current_self_positions:
            pieces.pop(self_pos, None)

        # Add own positions back
        for self_pos in current_self_positions:
            pieces[(self_pos[0] + movement[0], self_pos[1] + movement[1])] = PieceData(
                parent=(piece_place[0] + movement[0], piece_place[1] + movement[1]),
                place=(self_pos[0] + movement[0], self_pos[1] + movement[1]),
                color=piece_to_move["color"],
                size=piece_size,
                show=(self_pos[0] == piece_place[0] and self_pos[1] == piece_place[1]),
            )

        moving = next_place, pieces[next_place]

    return moving


def add_aoe(
    mouse_pos: tuple[int, int],
    aoes: dict[tuple[float, float], AreaOfEffectData],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[tuple[float, float], AreaOfEffectData] | None:
    aoe_pos = round((mouse_pos[0] + camera[0]) / gridsize, 2), round((mouse_pos[1] + camera[1]) / gridsize, 2)
    color = pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255), 100)
    radius = gridsize // 2
    aoes[aoe_pos] = AreaOfEffectData(
        origin=aoe_pos,
        glow=Glow(
            radius_range=range(radius, radius - 1, -1),
            inner_color=color,
            outer_color=color,
        ),
    )
    return aoe_pos, aoes[aoe_pos]


def make_aoe(
    origin: tuple[float, float],
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    aoe: AreaOfEffectData,
    aoes: dict[tuple[float, float], AreaOfEffectData],
    gridsize: int,
) -> tuple[tuple[float, float], AreaOfEffectData] | None:
    aoe_pos = aoe["origin"]
    making_aoe = aoe_pos, aoe
    dist = int(
        sqrt(
            (((origin[0] * gridsize) - (mouse_pos[0] + camera[0])) ** 2)
            + (((origin[1] * gridsize) - (mouse_pos[1] + camera[1])) ** 2)
        )
    )
    radius = max(dist, gridsize // 2)

    if radius != 0:
        aoes[aoe_pos] = AreaOfEffectData(
            origin=aoe_pos,
            glow=Glow(
                radius_range=range(radius, radius - 1, -1),
                inner_color=aoe["glow"].inner_color,
                outer_color=aoe["glow"].outer_color,
            ),
        )
        making_aoe = aoe_pos, aoes[aoe_pos]

    return making_aoe


def remove_aoe(
    mouse_pos: tuple[int, int],
    camera: tuple[int, int],
    aoes: dict[tuple[float, float], AreaOfEffectData],
    gridsize: int,
) -> None:
    to_remove: set[tuple[float, float]] = set()
    for origin, aoe_data in aoes.items():
        radius = aoe_data["glow"].radius
        dist = sqrt(
            (((origin[0] * gridsize) - (mouse_pos[0] + camera[0])) ** 2)
            + (((origin[1] * gridsize) - (mouse_pos[1] + camera[1])) ** 2)
        )

        if dist <= radius:
            to_remove.add(origin)

    for origin in to_remove:
        aoes.pop(origin, None)


def scale_camera(
    camera: tuple[int, int],
    mouse_pos: tuple[int, int],
    gridsize: int,
    old_gridsize: int,
) -> tuple[int, int]:
    camera_delta = zoom_at_mouse_pos(mouse_pos, camera, old_gridsize, gridsize)
    camera = camera[0] - camera_delta[0], camera[1] - camera_delta[1]
    return camera


def scale_aoes(
    aoes: dict[tuple[float, float], AreaOfEffectData],
    new_gridsize: int,
    old_gridsize: int,
) -> None:
    for place, aoe in aoes.items():
        cur_radius = aoes[place]["glow"].radius
        rel_grid_radius = round(cur_radius / old_gridsize, 2)
        new_radius = max(int(rel_grid_radius * new_gridsize), max(new_gridsize // 2, 1))

        aoes[place]["glow"] = Glow(
            radius_range=range(new_radius, new_radius - 1, -1),
            inner_color=aoe["glow"].inner_color,
            outer_color=aoe["glow"].outer_color,
        )


def scale_map(
    current_map_size: tuple[int, int],
    new_gridsize: int,
    old_gridsize: int,
    orig_dnd_map: pygame.Surface,
) -> pygame.Surface:
    cur_x, cur_y = current_map_size
    rel_x, rel_y = cur_x / old_gridsize, cur_y / old_gridsize
    new_x, new_y = max(round(rel_x * new_gridsize), 1), max(round(rel_y * new_gridsize), 1)
    dnd_map = pygame.transform.scale(orig_dnd_map, (new_x, new_y))
    return dnd_map


def main(map_file: str, gridsize: int) -> None:  # noqa: C901
    # Init
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    pygame.display.set_caption("DND fog")
    clock = pygame.time.Clock()
    frame_rate: int = 60

    # Settings
    double_click = 0
    colors = orig_colors.copy()
    modifiers = {pygame.KMOD_ALT, pygame.KMOD_CTRL, pygame.KMOD_SHIFT}
    moving_piece: tuple[tuple[int, int], PieceData] | None = None
    making_aoe: tuple[tuple[int, int], AreaOfEffectData] | None = None
    fog_color = (0xCC, 0xCC, 0xCC)
    selected_size = 1

    # Screen setup
    display_size = (1200, 800)
    flags = pygame.SRCALPHA | pygame.RESIZABLE  # | pygame.NOFRAME
    display = pygame.display.set_mode(display_size, flags=flags)

    # Map data
    orig_gridsize = gridsize
    removed_fog: set[tuple[int, int]] = set()
    pieces: dict[tuple[int, int], PieceData] = {}
    aoes: dict[tuple[float, float], AreaOfEffectData] = {}
    camera: tuple[int, int] = (0, 0)
    show_grid = False
    show_fog = False

    # Load data
    if map_file[-5:] == ".json":
        import_data = open_data_file(map_file)
        dnd_map = import_data.dnd_map
        orig_dnd_map = import_data.orig_dnd_map
        gridsize = import_data.gridsize
        orig_gridsize = import_data.orig_gridsize
        camera = import_data.camera
        map_offset = import_data.map_offset
        pieces = import_data.pieces
        aoes = import_data.aoes
        removed_fog = import_data.removed_fog
        colors = import_data.colors
        show_grid = import_data.show_grid
        show_fog = import_data.show_fog

    # Load background image
    else:
        dnd_map = pygame.image.load(map_file).convert_alpha()
        dnd_map.set_colorkey((255, 255, 255))
        orig_dnd_map = dnd_map.copy()
        map_offset = (0, 0)

    while True:
        double_click = double_click - 1 if double_click > 0 else 0

        mouse_pos = pygame.mouse.get_pos()
        pressed_modifiers = pygame.key.get_mods()
        pressed_buttons = pygame.mouse.get_pressed()
        mouse_speed = pygame.mouse.get_rel()

        for event in pygame.event.get():
            # Quit
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Save data
                if pressed_modifiers & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    save_data_file(
                        orig_dnd_map=orig_dnd_map,
                        gridsize=gridsize,
                        orig_gridsize=orig_gridsize,
                        camera=camera,
                        zoom=dnd_map.get_size(),
                        map_offset=map_offset,
                        pieces=pieces,
                        aoes=aoes,
                        removed_fog=removed_fog,
                        show_grid=show_grid,
                        show_fog=show_fog,
                    )

                # Load data
                if pressed_modifiers & pygame.KMOD_CTRL and event.key == pygame.K_o:
                    openpath = open_file_dialog(
                        title="Open Map",
                        ext=[("Json file", "json")],
                        default_ext="json",
                    )
                    if openpath:
                        import_data = open_data_file(openpath)
                        dnd_map = import_data.dnd_map
                        orig_dnd_map = import_data.orig_dnd_map
                        gridsize = import_data.gridsize
                        orig_gridsize = import_data.orig_gridsize
                        camera = import_data.camera
                        map_offset = import_data.map_offset
                        pieces = import_data.pieces
                        aoes = import_data.aoes
                        removed_fog = import_data.removed_fog
                        colors = import_data.colors
                        show_grid = import_data.show_grid
                        show_fog = import_data.show_fog

                # Hide/Show grid
                if event.key == pygame.K_F1:
                    show_grid = not show_grid

                # Hide/Show fog
                if event.key == pygame.K_F12:
                    show_fog = not show_fog

                # Select size (5x5)
                if event.key == pygame.K_1:
                    selected_size = 1

                # Select size (10x10)
                if event.key == pygame.K_2:
                    selected_size = 2

                # Select size (15x15)
                if event.key == pygame.K_3:
                    selected_size = 3

                # Select size (20x20)
                if event.key == pygame.K_4:
                    selected_size = 4

            # Zoom map
            if event.type == pygame.MOUSEWHEEL:
                old_gridsize = gridsize
                if gridsize + event.y > 0:
                    gridsize = gridsize + event.y
                    scale_aoes(aoes, gridsize, old_gridsize)
                    camera = scale_camera(camera, mouse_pos, gridsize, old_gridsize)
                    if not pressed_modifiers & pygame.KMOD_ALT:
                        dnd_map = scale_map(dnd_map.get_size(), gridsize, old_gridsize, orig_dnd_map)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start moving a piece
                if event.button == pygame.BUTTON_LEFT and not any(pressed_modifiers & mod for mod in modifiers):
                    next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
                    if next_place in pieces:
                        moving_piece = next_place, pieces[next_place]

                if event.button == pygame.BUTTON_RIGHT:
                    next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                    if double_click:
                        double_click = 0
                        making_aoe = None
                        moving_piece = None

                        # Remove aoe
                        if pressed_modifiers & pygame.KMOD_CTRL and pressed_modifiers & pygame.KMOD_SHIFT:
                            remove_aoe(mouse_pos, camera, aoes, gridsize)

                        # Remove piece
                        else:
                            remove_piece(next_place, pieces, colors)

                    # Add area of effect
                    elif pressed_modifiers & pygame.KMOD_CTRL and not pressed_modifiers & pygame.KMOD_SHIFT:
                        making_aoe = add_aoe(mouse_pos, aoes, camera, gridsize)

                    # Add a piece
                    elif not any(pressed_modifiers & mod for mod in modifiers):
                        add_piece(next_place, pieces, colors, selected_size)
                        double_click = 15

                    else:
                        double_click = 15

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop moving a piece
                if event.button == pygame.BUTTON_LEFT:
                    moving_piece = None

                # Stop making an aoe
                if event.button == pygame.BUTTON_RIGHT:
                    making_aoe = None

            # Left mouse button
            if pressed_buttons[0]:
                next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                # Moving a piece
                if moving_piece is not None:
                    moving_piece = move_piece(moving_piece[0], next_place, moving_piece[1], pieces)

                else:
                    # Move map
                    if pressed_modifiers & pygame.KMOD_ALT:
                        map_offset = (
                            max(min(round(map_offset[0] - (mouse_speed[0] / gridsize), 2), 1.1), -0.1),
                            max(min(round(map_offset[1] - (mouse_speed[1] / gridsize), 2), 1.1), -0.1),
                        )

                    # Add and remove fog
                    if pressed_modifiers & pygame.KMOD_CTRL:
                        if pressed_modifiers & pygame.KMOD_SHIFT:
                            removed_fog.discard(next_place)
                        else:
                            removed_fog.add(next_place)

            # Middle mouse button
            if pressed_buttons[1]:
                # Move camera
                camera = camera[0] - mouse_speed[0], camera[1] - mouse_speed[1]

            # Right mouse button
            if pressed_buttons[2]:
                # Making an area of effect
                if making_aoe is not None:
                    making_aoe = make_aoe(making_aoe[0], mouse_pos, camera, making_aoe[1], aoes, gridsize)

        display.fill(fog_color)

        display.blit(dnd_map, draw_position((0, 0), camera, gridsize, offset=map_offset))

        draw_aoes(display, aoes, camera, gridsize)

        if show_grid:
            draw_grid(display, camera, gridsize)

        draw_pieces(display, pieces, camera, gridsize)

        if show_fog:
            draw_fog(display, camera, gridsize, removed_fog, fog_color)

        pygame.display.flip()
        clock.tick(frame_rate)
