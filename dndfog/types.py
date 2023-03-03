import copy
from dataclasses import dataclass, field
from enum import Enum
from itertools import cycle
from typing import NamedTuple, Protocol, TypeAlias, TypedDict

import pygame

pygame.font.init()
font = pygame.font.SysFont("arial", 16)


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


class KeyEvent(Protocol):
    key: int
    mod: int
    unicode: str
    scancode: int
    type: int


class MouseButtonEvent(Protocol):
    pos: tuple[int, int]
    button: int
    touch: bool
    type: int


class MouseWheelEvent(Protocol):
    x: int
    y: int
    precise_x: float
    precise_y: float
    touch: bool
    flipped: bool
    type: int


Event: TypeAlias = KeyEvent | MouseButtonEvent | MouseWheelEvent


class Glow:
    def __init__(self, radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color):
        self._radius_range = radius_range
        self.inner_color = inner_color
        self.outer_color = outer_color
        self._glow_cycle = cycle([self._build_glow(radius_range, inner_color, outer_color)])

    @property
    def color(self) -> tuple[int, int, int, int]:
        return self.inner_color.r, self.inner_color.g, self.inner_color.b, self.inner_color.a

    @property
    def radius(self) -> int:
        return next(self).get_width() // 2

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
        for lerp_step, radius_step in zip(lerp_steps, radius_range, strict=True):
            lerped_color = outer_color.lerp(inner_color, lerp_step / len(radius_range))

            radii.append(radius_step)
            colors.append(lerped_color)

        glow_surface_size = 2 * radius_range.start, 2 * radius_range.start
        glow_surface_center = radius_range.start, radius_range.start
        # Glow circles are not solid so that blend mode works right and each band has 1 pixel overlap
        band_width = abs(radius_range.step) + 1

        glow = pygame.Surface(glow_surface_size, flags=pygame.SRCALPHA)

        # Draw glow in shrinking circles. Draw a circle first to a temp surface
        # and then blit that to the glow surface with its alpha value in RGBA-MAX blend mode.
        for i, (circle_color, circle_radius) in enumerate(zip(colors, radii, strict=True)):
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


class PieceSize(int, Enum):
    small = 1
    medium = 2
    large = 3
    giant = 4


class FogSize(int, Enum):
    small = 1
    medium = 2
    large = 3
    giant = 4


class PieceData(TypedDict):
    place: tuple[int, int]
    parent: tuple[int, int]
    color: tuple[int, int, int]
    size: PieceSize
    show: bool


Pieces: TypeAlias = dict[tuple[int, int], PieceData]


class BackgroundImage(TypedDict):
    img: str
    size: tuple[int, int]
    mode: str
    zoom: tuple[int, int]


class SaveData(TypedDict):
    gridsize: int
    removed_fog: list[tuple[int, int]]
    background: BackgroundImage
    pieces: list[PieceData]
    camera: tuple[int, int]
    map_offset: tuple[float, float]
    show_grid: bool
    show_fog: bool


class Tool(int, Enum):
    piece = 0
    fog = 1
    map = 2
    grid = 3

    @classmethod
    def values(cls):
        return cls._value2member_map_.keys()


@dataclass
class Show:
    grid: bool = False
    fog: bool = False
    toolbar: bool = False


@dataclass
class Selected:
    tool: Tool = Tool.piece
    size: PieceSize = PieceSize.small
    piece: tuple[int, int] | None = None
    fog: FogSize = FogSize.small


@dataclass
class MapData:
    image: pygame.Surface | None = None
    original_image: pygame.Surface | None = None
    image_offset: tuple[float, float] = (0, 0)
    pieces: Pieces = field(default_factory=dict)
    removed_fog: set[tuple[int, int]] = field(default_factory=set)
    fog_color: tuple[int, int, int] = (0xCC, 0xCC, 0xCC)
    grid_color: tuple[int, int, int] = (0xC5, 0xC5, 0xC5)
    camera: tuple[int, int] = (0, 0)
    gridsize: int = 36


@dataclass
class ProgramState:
    show: Show = field(default_factory=Show)
    selected: Selected = field(default_factory=Selected)
    colors: list[tuple[int, int, int]] = field(default_factory=orig_colors.copy)
    map: MapData = field(default_factory=MapData)


class LoopData(NamedTuple):
    mouse_pos: tuple[int, int]
    grid_pos: tuple[int, int]
    mouse_speed: tuple[int, int]
    pressed_modifiers: int
    pressed_buttons: tuple[bool, bool, bool]
