import base64
import gzip
import json
import os
from typing import Optional

import pygame
import pywintypes
from win32con import OFN_ALLOWMULTISELECT, OFN_EXPLORER
from win32gui import GetOpenFileNameW, GetSaveFileNameW

from dndfog.types import (
    ORIG_COLORS,
    BackgroundImage,
    PieceData,
    PieceSize,
    ProgramState,
    SaveData,
)

__all__ = [
    "open_file_dialog",
    "save_file_dialog",
    "open_data_file",
    "save_data_file",
]


def load_map(start_file: str, state: ProgramState) -> None:
    # Load data file
    if start_file[-5:] == ".json":
        open_data_file(start_file, state)

    # Load background image
    else:
        state.map.image = pygame.image.load(start_file).convert_alpha()
        state.map.image.set_colorkey((255, 255, 255))
        state.map.original_image = state.map.image.copy()


def open_file_dialog(
    title: str = None,
    directory: Optional[str] = None,
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

    if directory is None:
        directory = os.getcwd()

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
    directory: Optional[str] = None,
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

    if directory is None:
        directory = os.getcwd()

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

    except pywintypes.error as e:  # noqa
        if e.winerror == 0:
            return None
        else:
            raise IOError() from e


def save_data_file(state: ProgramState) -> None:
    savepath = save_file_dialog(title="Save Map", ext=[("Json file", "json")], default_ext="json")
    if savepath:
        data = SaveData(
            gridsize=state.map.gridsize,
            removed_fog=list(state.map.removed_fog),
            background=BackgroundImage(
                img=serialize_map(state.map.original_image),
                size=state.map.original_image.get_size(),
                mode="RGBA",
                zoom=state.map.image.get_size(),
            ),
            pieces=list(state.map.pieces.values()),
            camera=state.map.camera,
            map_offset=state.map.image_offset,
            show_grid=state.show.grid,
            show_fog=state.show.fog,
        )

        with open(savepath, "w") as f:
            json.dump(data, f, indent=2)


def open_data_file(openpath: str, state: ProgramState) -> None:
    with open(openpath, "r") as f:
        data: SaveData = json.load(f)

    state.map.gridsize = int(data["gridsize"])
    state.map.removed_fog = {(x, y) for x, y in data["removed_fog"]}
    state.map.pieces = {
        tuple(piece["place"]): PieceData(
            parent=tuple(piece["parent"]),
            place=tuple(piece["place"]),
            color=tuple(piece["color"]),
            size=PieceSize(int(piece["size"])),
            show=piece["show"],
        )
        for piece in data["pieces"]
    }
    state.map.original_image = deserialize_map(data)
    state.map.image = pygame.transform.scale(state.map.original_image, data["background"]["zoom"])
    state.map.camera = tuple(data["camera"])
    state.map.image_offset = tuple(data["map_offset"])
    state.colors = [
        color for color in ORIG_COLORS if color not in {piece["color"] for piece in state.map.pieces.values()}
    ]
    state.show.grid = data["show_grid"]
    state.show.fog = data["show_fog"]


def serialize_map(surface: pygame.Surface) -> str:
    return base64.b64encode(
        gzip.compress(
            pygame.image.tostring(surface, "RGBA"),  # type: ignore
        ),
    ).decode()


def deserialize_map(data: dict) -> pygame.Surface:
    return pygame.image.fromstring(
        gzip.decompress(base64.b64decode(data["background"]["img"])),  # type: ignore
        data["background"]["size"],
        data["background"]["mode"],
    ).convert_alpha()
