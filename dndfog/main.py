import base64
import copy
import json
import os
import sys
from argparse import ArgumentParser
from itertools import cycle
from random import randint
from typing import NamedTuple, TypedDict

import pygame
import pywintypes
from win32con import OFN_ALLOWMULTISELECT, OFN_EXPLORER
from win32gui import GetOpenFileNameW, GetSaveFileNameW


class BackgroundImage(TypedDict):
    img: str
    size: tuple[int, int]
    mode: str
    zoom: tuple[int, int]


class PieceData(TypedDict):
    place: tuple[int, int]
    color: tuple[int, int, int]
    size: int
    show: bool


class SaveData(TypedDict):
    gridsize: int
    orig_gridsize: int
    removed_fog: list[tuple[int, int]]
    background: BackgroundImage
    pieces: list[PieceData]
    camera: tuple[int, int]
    map_offset: tuple[int, int]
    show_grid: bool
    show_fog: bool


class ImportData(NamedTuple):
    dnd_map: pygame.Surface
    orig_dnd_map: pygame.Surface
    gridsize: int
    orig_gridsize: int
    camera: tuple[int, int]
    map_offset: tuple[int, int]
    pieces: dict[tuple[int, int], PieceData]
    removed_fog: set[tuple[int, int]]
    colors: list[tuple[int, int, int]]
    show_grid: bool
    show_fog: bool


orig_colors = [
    (255, 0, 0),  # red
    (255, 255, 0),  # yellow
    (0, 0, 255),  # blue
    (0, 100, 0),  # green
    (0, 255, 255),  # cyan
    (255, 0, 255),  # magenta
    (255, 100, 0),  # orange
    (100, 0, 100),  # purple
    (0, 255, 0),  # light green
    (110, 38, 14),  # brown
    (255, 192, 203),  # pink
    (109, 113, 46),  # olive
    (220, 180, 255),  # lavender
    (253, 133, 105),  # peach
]


def open_file_dialog(
    title: str = None,
    directory: str = os.getcwd(),
    default_name: str = "",
    default_ext: str = "",
    ext: list[tuple[str, str]] = None,
    multiselect: bool = False,
) -> str | list[str] | None:
    """Open a file open dialog at a specified directory.
    :param title: Dialog title.
    :param directory: Directory to open file dialog in.
    :param default_name: Default file name.
    :param default_ext: Default file extension. Only letters, no dot.
    :param ext: List of available extension description + name tuples,
                e.g. [(JPEG Image, jpg), (PNG Image, png)].
    :param multiselect: Allow multiple files to be selected.
    :return: Path to a file to open if multiselect=False.
             List of the paths to files which should be opened if multiselect=True.
             None if file open dialog canceled.
    :raises IOError: File open dialog failed.
    """

    # https://programtalk.com/python-examples/win32gui.GetOpenFileNameW/

    flags = OFN_EXPLORER
    if multiselect:
        flags = flags | OFN_ALLOWMULTISELECT

    if ext is None:
        ext = "All Files\0*.*\0"
    else:
        ext = "".join([f"{name}\0*.{extension}\0" for name, extension in ext])

    try:
        file_path, _, _ = GetOpenFileNameW(
            InitialDir=directory,
            File=default_name,
            Flags=flags,
            Title=title,
            MaxFile=2**16,
            Filter=ext,
            DefExt=default_ext,
        )

        paths = file_path.split("\0")

        if len(paths) == 1:
            return paths[0]
        else:
            for i in range(1, len(paths)):
                paths[i] = os.path.join(paths[0], paths[i])
            paths.pop(0)

        return paths

    except pywintypes.error as e:  # noqa
        if e.winerror == 0:
            return None
        else:
            raise IOError() from e


def save_file_dialog(
    title: str = None,
    directory: str = os.getcwd(),
    default_name: str = "",
    default_ext: str = "",
    ext: list[tuple[str, str]] = None,
) -> str | None:
    """Open a file save dialog at a specified directory.
    :param title: Dialog title.
    :param directory: Directory to open file dialog in.
    :param default_name: Default file name.
    :param default_ext: Default file extension. Only letters, no dot.
    :param ext: List of available extension description + name tuples,
                e.g. [(JPEG Image, jpg), (PNG Image, png)].
    :return: Path file should be save to. None if file save dialog canceled.
    :raises IOError: File save dialog failed.
    """

    # https://programtalk.com/python-examples/win32gui.GetSaveFileNameW/

    if ext is None:
        ext = "All Files\0*.*\0"
    else:
        ext = "".join([f"{name}\0*.{extension}\0" for name, extension in ext])

    try:
        file_path, _, _ = GetSaveFileNameW(
            InitialDir=directory,
            File=default_name,
            Title=title,
            MaxFile=2**16,
            Filter=ext,
            DefExt=default_ext,
        )

        return file_path

    except pywintypes.error as e:
        if e.winerror == 0:
            return None
        else:
            raise IOError() from e


class Glow:
    def __init__(self, radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color):
        self._radius_range = radius_range
        self._inner_color = inner_color
        self._outer_color = outer_color
        self._glow_cycle = cycle([self._build_glow(radius_range, inner_color, outer_color)])

    @classmethod
    def uniform(cls, radius: int, color) -> "Glow":
        if not isinstance(color, pygame.Color):
            color = pygame.Color(*color)

        outer_color = copy.deepcopy(color)
        outer_color.a = 0

        return cls(range(radius, 0, -1), color, outer_color)

    def __iter__(self) -> "Glow":
        return self

    def __next__(self) -> pygame.Surface:
        return next(self._glow_cycle)

    @staticmethod
    def _build_glow(radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color) -> pygame.Surface:
        colors, radii = [], []

        lerp_steps = range(1, len(radius_range) + 1)

        # create colors for glow from the largest circle's color to the smallest
        for lerp_step, radius_step in zip(lerp_steps, radius_range):
            lerped_color = outer_color.lerp(inner_color, lerp_step / len(radius_range))

            radii.append(radius_step)
            colors.append(lerped_color)

        glow_surface_size = 2 * radius_range.start, 2 * radius_range.start
        glow_surface_center = radius_range.start, radius_range.start
        # Glow circles are not solid so that blend mode works right and each band has 1 pixel overlap
        band_width = abs(radius_range.step) + 1

        glow = pygame.Surface(glow_surface_size, flags=pygame.SRCALPHA)

        # Draw glow in shrinking circles. Draw a circle first to a temp surface
        # and then blit that to the glow surface with it's alpha value in RGBA-MAX blend mode.
        for i, (circle_color, circle_radius) in enumerate(zip(colors, radii)):
            temp_surface = pygame.Surface(glow_surface_size, flags=pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                circle_color,
                glow_surface_center,
                circle_radius,
                band_width if i != len(colors) - 1 else 0,
            )
            temp_surface.set_alpha(circle_color.a)

            glow.blit(temp_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)

        return glow


def approx(value: int | float, /) -> int:
    return int(value) if value > 0 else int(value - 1)


def draw_position(
    pos: tuple[int | float, int | float],
    camera: tuple[int, int],
    gridsize: int,
    offset: tuple[int, int] = (0, 0),
) -> tuple[int, int]:
    return (pos[0] * gridsize) - camera[0] - offset[0], (pos[1] * gridsize) - camera[1] - offset[1]


def grid_position(
    pos: tuple[int, int],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[int, int]:
    return approx((pos[0] + camera[0]) / gridsize), approx((pos[1] + camera[1]) / gridsize)


def zoom_at_mouse_pos(
    mouse_position: tuple[int, int],
    camera: tuple[int, int],
    old_gridsize: int,
    new_gridsize: int,
) -> tuple[int, int]:

    absolute_mouse_position = mouse_position[0] + camera[0], mouse_position[1] + camera[1]

    old_grid_place = absolute_mouse_position[0] / old_gridsize, absolute_mouse_position[1] / old_gridsize
    new_grid_place = absolute_mouse_position[0] / new_gridsize, absolute_mouse_position[1] / new_gridsize

    camera_delta = (
        round((new_grid_place[0] - old_grid_place[0]) * new_gridsize),
        round((new_grid_place[1] - old_grid_place[1]) * new_gridsize),
    )

    return camera_delta


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


def save_data_file(
    orig_dnd_map: pygame.Surface,
    gridsize: int,
    orig_gridsize: int,
    camera: tuple[int, int],
    zoom: tuple[int, int],
    map_offset: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    removed_fog: set[tuple[int, int]],
    show_grid: bool,
    show_fog: bool,
) -> None:
    savepath = save_file_dialog(
        title="Save Map",
        ext=[("Json file", "json")],
        default_ext="json",
    )
    if savepath:
        data = SaveData(
            gridsize=gridsize,
            orig_gridsize=orig_gridsize,
            removed_fog=list(removed_fog),
            background=BackgroundImage(
                img=serialize_map(orig_dnd_map),
                size=orig_dnd_map.get_size(),
                mode="RGBA",
                zoom=zoom,
            ),
            pieces=list(pieces.values()),
            camera=camera,
            map_offset=map_offset,
            show_grid=show_grid,
            show_fog=show_fog,
        )

        with open(savepath, "w") as f:
            json.dump(data, f, indent=2)


def open_data_file(openpath: str) -> ImportData:
    with open(openpath, "r") as f:
        data = json.load(f)

    gridsize = int(data["gridsize"])
    orig_gridsize = int(data["orig_gridsize"])
    removed_fog = set((x, y) for x, y in data["removed_fog"])
    pieces = {
        tuple(piece["place"]): PieceData(
            place=tuple(piece["place"]),
            color=tuple(piece["color"]),
            size=int(piece["size"]),
            show=piece["show"],
        )
        for piece in data["pieces"]
    }
    orig_dnd_map = deserialize_map(data)
    dnd_map = pygame.transform.scale(orig_dnd_map, data["background"]["zoom"])
    camera = tuple(data["camera"])
    map_offset = tuple(data["map_offset"])
    colors = [color for color in orig_colors if color not in {piece["color"] for piece in pieces.values()}]
    show_grid = data["show_grid"]
    show_fog = data["show_fog"]

    return ImportData(
        dnd_map=dnd_map,
        orig_dnd_map=orig_dnd_map,
        gridsize=gridsize,
        orig_gridsize=orig_gridsize,
        camera=camera,
        map_offset=map_offset,
        pieces=pieces,
        removed_fog=removed_fog,
        colors=colors,
        show_grid=show_grid,
        show_fog=show_fog,
    )


def serialize_map(surface: pygame.Surface) -> str:
    return base64.b64encode(pygame.image.tostring(surface, "RGBA")).decode()


def deserialize_map(data: dict) -> pygame.Surface:
    return pygame.image.fromstring(
        base64.b64decode(data["background"]["img"]),
        data["background"]["size"],
        data["background"]["mode"],
    ).convert_alpha()


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
                    place=add_place,
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
        place = piece_data["place"]
        size = piece_data["size"]
        color = piece_data["color"]

        for x in range(size):
            for y in range(size):
                pieces.pop((place[0] + x, place[1] + y), None)
                if color in orig_colors and color not in colors:
                    colors.insert(0, color)


def move_piece(
    current_place: tuple[int, int],
    piece_to_move: PieceData,
    mouse_pos: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    camera: tuple[int, int],
    gridsize: int,
) -> tuple[tuple[int, int], PieceData]:
    piece_place = piece_to_move["place"]
    piece_size = piece_to_move["size"]
    next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
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
                place=(piece_place[0] + movement[0], piece_place[1] + movement[1]),
                color=piece_to_move["color"],
                size=piece_size,
                show=(self_pos[0] == piece_place[0] and self_pos[1] == piece_place[1]),
            )

        moving = next_place, pieces[next_place]

    return moving


def main(map_file: str, gridsize: int) -> None:
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
    moving: tuple[tuple[int, int], PieceData] | None = None
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
    camera = (0, 0)
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
                    camera_delta = zoom_at_mouse_pos(mouse_pos, camera, old_gridsize, gridsize)
                    camera = camera[0] - camera_delta[0], camera[1] - camera_delta[1]
                    scale = gridsize / orig_gridsize
                    dnd_map_size = orig_dnd_map.get_size()
                    dnd_map = pygame.transform.scale(orig_dnd_map, (dnd_map_size[0] * scale, dnd_map_size[1] * scale))

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start moving a piece
                if event.button == pygame.BUTTON_LEFT and not any(pressed_modifiers & mod for mod in modifiers):
                    next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)
                    if next_place in pieces:
                        moving = next_place, pieces[next_place]

                if event.button == pygame.BUTTON_RIGHT:
                    next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                    # Remove piece
                    if double_click:
                        remove_piece(next_place, pieces, colors)

                    # Add a piece
                    else:
                        add_piece(next_place, pieces, colors, selected_size)
                        double_click = 15

            if event.type == pygame.MOUSEBUTTONUP:
                # Stop moving a piece
                if event.button == pygame.BUTTON_LEFT:
                    moving = None

            # Left mouse button
            if pressed_buttons[0]:

                # Moving a piece
                if moving is not None:
                    moving = move_piece(moving[0], moving[1], mouse_pos, pieces, camera, gridsize)

                else:
                    # Move map
                    if pressed_modifiers & pygame.KMOD_ALT:
                        map_offset = map_offset[0] - mouse_speed[0], map_offset[1] - mouse_speed[1]

                    # Add and remove fog
                    if pressed_modifiers & pygame.KMOD_CTRL:
                        next_place = grid_position((mouse_pos[0], mouse_pos[1]), camera, gridsize)

                        if pressed_modifiers & pygame.KMOD_SHIFT:
                            removed_fog.discard(next_place)
                        else:
                            removed_fog.add(next_place)

            # Middle mouse button
            if pressed_buttons[1]:
                # Move camera
                camera = camera[0] - mouse_speed[0], camera[1] - mouse_speed[1]

        display.fill(fog_color)

        display.blit(dnd_map, draw_position((0, 0), camera, gridsize, offset=map_offset))

        if show_grid:
            draw_grid(display, camera, gridsize)

        draw_pieces(display, pieces, camera, gridsize)

        if show_fog:
            draw_fog(display, camera, gridsize, removed_fog, fog_color)

        pygame.display.flip()
        clock.tick(frame_rate)


def start() -> None:
    parser = ArgumentParser()
    parser.add_argument("--file", default=None)
    parser.add_argument("--gridsize", default=36)
    args = parser.parse_args()

    if args.file is not None:
        start_file = str(args.file)
    else:
        start_file = open_file_dialog(
            title="Select a background map, or a json data file",
            ext=[("PNG file", "png"), ("JPG file", "jpg"), ("JSON file", "json")],
        )

    if not start_file:
        raise SystemExit("No file selected.")

    main(start_file, int(args.gridsize))


if __name__ == "__main__":
    start()
