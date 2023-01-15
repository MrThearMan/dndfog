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
    AreaOfEffectData,
    AreaOfEffectSaveData,
    BackgroundImage,
    Glow,
    ImportData,
    PieceData,
    SaveData,
    orig_colors,
)

__all__ = [
    "open_file_dialog",
    "save_file_dialog",
    "open_data_file",
    "save_data_file",
]


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


def save_data_file(
    orig_dnd_map: pygame.Surface,
    gridsize: int,
    orig_gridsize: int,
    camera: tuple[int, int],
    zoom: tuple[int, int],
    map_offset: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    aoes: dict[tuple[float, float], AreaOfEffectData],
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
            aoes=[
                AreaOfEffectSaveData(
                    origin=aoe["origin"],
                    radius=aoe["glow"].radius,
                    color=aoe["glow"].color,
                )
                for aoe in aoes.values()
            ],
            camera=camera,
            map_offset=map_offset,
            show_grid=show_grid,
            show_fog=show_fog,
        )

        with open(savepath, "w") as f:
            json.dump(data, f, indent=2)


def open_data_file(openpath: str) -> ImportData:
    with open(openpath, "r") as f:
        data: SaveData = json.load(f)

    gridsize = int(data["gridsize"])
    orig_gridsize = int(data["orig_gridsize"])
    removed_fog = {(x, y) for x, y in data["removed_fog"]}
    pieces = {
        tuple(piece["place"]): PieceData(
            parent=tuple(piece["parent"]),
            place=tuple(piece["place"]),
            color=tuple(piece["color"]),
            size=int(piece["size"]),
            show=piece["show"],
        )
        for piece in data["pieces"]
    }
    aoes = {
        tuple(aoe["origin"]): AreaOfEffectData(
            origin=tuple(aoe["origin"]),
            glow=Glow(
                radius_range=range(aoe["radius"], aoe["radius"] - 1, -1),
                inner_color=pygame.Color(*aoe["color"]),
                outer_color=pygame.Color(*aoe["color"]),
            ),
        )
        for aoe in data["aoes"] or {}
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
        aoes=aoes,
        removed_fog=removed_fog,
        colors=colors,
        show_grid=show_grid,
        show_fog=show_fog,
    )


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
