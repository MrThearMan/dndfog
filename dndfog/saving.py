import base64
import gzip
import json
import os
from pathlib import Path
from typing import Optional

import pygame
import pywintypes
from win32con import OFN_ALLOWMULTISELECT, OFN_EXPLORER
from win32gui import GetOpenFileNameW, GetSaveFileNameW

from dndfog.types import (
    ORIG_COLORS,
    BackgroundImage,
    MarkerSize,
    MarkingData,
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


def load_map(map_file: str, state: ProgramState) -> None:
    extension = Path(map_file).suffix

    # Load data file
    if extension in [".json", ".dndfog"]:
        state.file = map_file
        open_data_file(state)
        return

    # Load background image
    elif extension in [".png", ".jpg", ".jpeg"]:
        state.map.image = pygame.image.load(map_file).convert_alpha()
        state.map.image.set_colorkey((255, 255, 255))
        state.map.original_image = state.map.image.copy()
        return

    raise RuntimeError("Unsupported file type.")


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
    data = state.to_json()
    with open(state.file, "w") as f:
        json.dump(data, f, indent=2)


def open_data_file(state: ProgramState) -> None:
    with open(state.file, "r") as f:
        data: SaveData = json.load(f)

    state.map.gridsize = int(data["map"]["gridsize"])
    state.map.removed_fog = set(data["map"]["removed_fog"])
    state.map.original_image = deserialize_map(data["map"]["image"])
    state.map.image = pygame.transform.scale(state.map.original_image, data["map"]["image"]["zoom"])
    state.map.camera = tuple(data["map"]["camera"])
    state.map.image_offset = tuple(data["map"]["image_offset"])
    state.map.pieces = {
        tuple(piece["place"]): PieceData(
            parent=tuple(piece["parent"]),
            place=tuple(piece["place"]),
            color=tuple(piece["color"]),
            size=PieceSize(int(piece["size"])),
            show=piece["show"],
        )
        for piece in data["map"]["pieces"]
    }
    state.map.markings = {
        tuple(marking["place"]): MarkingData(
            place=tuple(marking["place"]),
            color=tuple(marking["color"]),
            size=MarkerSize(int(marking["size"])),
        )
        for marking in data["map"]["markings"]
    }

    state.show.grid = data["show"]["grid"]
    state.show.fog = data["show"]["fog"]

    state.colors = [
        color for color in ORIG_COLORS if color not in {piece["color"] for piece in state.map.pieces.values()}
    ]


def serialize_map(surface: pygame.Surface) -> str:
    return base64.b64encode(
        gzip.compress(
            pygame.image.tostring(surface, "RGBA"),  # type: ignore
        ),
    ).decode()


def deserialize_map(data: BackgroundImage) -> pygame.Surface:
    return pygame.image.fromstring(
        gzip.decompress(base64.b64decode(data["img"])),
        data["size"],
        data["mode"],
    ).convert_alpha()


def get_default_filename(state: ProgramState) -> str:
    if state.file is None:
        return ""

    filename = state.file.rsplit("/", maxsplit=1)[-1]
    filename = filename.rsplit(".", maxsplit=1)[0]
    return filename
