from __future__ import annotations

import copy
import math
import random
import shelve
from dbm import error as DBMError
from itertools import cycle
from os import PathLike
from pickle import HIGHEST_PROTOCOL

import pygame


__all__ = ["Glow"]


class Glow:
    """Surface with a glow made from circles of shrinking size
    and color lerped from one color to another until transparent.
    """

    def __init__(self, radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color):
        """Create a new glow.

        :param radius_range: Range of radii for the circles in the glow, from largest/outermost
                             to smallest/innermost radius. Use step to make banding.
        :param inner_color: Glow inner color.
        :param outer_color: Glow outer color.
        :return: New glow.
        :rtype: Glow
        """

        self._radius_range = radius_range
        self._inner_color = inner_color
        self._outer_color = outer_color
        self._glow_cycle = cycle([self._build_glow(radius_range, inner_color, outer_color)])

    @classmethod
    def uniform(cls, radius: int, color) -> Glow:
        """Smooth, uniform glow. To set Glow intensity, set a smaller color alpha value.

        :param radius: Glow radius.
        :param color: Glow color.
        :return: New uniform glow.
        """

        if not isinstance(color, pygame.Color):
            color = pygame.Color(*color)

        outer_color = copy.deepcopy(color)
        outer_color.a = 0

        return cls(range(radius, 0, -1), color, outer_color)

    @classmethod
    def banded(cls, radius: int, color, bands: int, min_radius: int = 0) -> Glow:
        """Glow that weakens in steps, or bands. To set Glow intensity, set a smaller color alpha value.

        :param radius: Glow radius
        :param color: Glow color.
        :param bands: Number of bands in the glow. Actual number may be smaller due to rounding errors.
        :param min_radius: Smallest glow circle radius.
        :return: New banded glow.
        """

        if not isinstance(color, pygame.Color):
            color = pygame.Color(*color)

        outer_color = copy.deepcopy(color)
        outer_color.a = 0
        radius_range = range(radius, min_radius, -max(int(math.ceil((radius - min_radius) / bands)), 1))

        return cls(radius_range, color, outer_color)

    @classmethod
    def uniform_gradient(cls, radius: int, inner_color, outer_color) -> Glow:
        """Smooth, uniform glow from one color to another. To set Glow intensity, set a smaller outer color alpha value.

        :param radius: Glow radius.
        :param inner_color: Glow inner color.
        :param outer_color: Glow outer color.
        :return: New uniform glow.
        :rtype: Glow
        """

        if not isinstance(inner_color, pygame.Color):
            inner_color = pygame.Color(*inner_color)

        if not isinstance(outer_color, pygame.Color):
            outer_color = pygame.Color(*outer_color)

        if outer_color is None:
            outer_color = copy.deepcopy(inner_color)

        outer_color.a = 0

        return cls(range(radius, 0, -1), inner_color, outer_color)

    @classmethod
    def banded_gradient(
        cls,
        radius: int,
        inner_color,
        outer_color,
        bands: int,
        min_radius: int = 0,
    ) -> "Glow":
        """Glow that weakens in steps, or bands. To set Glow intensity, set a smaller outer color alpha value.

        :param radius: Glow radius
        :param inner_color: Glow inner color.
        :param outer_color: Glow outer color.
        :param bands: Number of bands in the glow. Actual number may be smaller due to rounding errors.
        :param min_radius: Smallest glow circle radius.
        :return: New banded glow.
        """

        if not isinstance(inner_color, pygame.Color):
            inner_color = pygame.Color(*inner_color)

        if not isinstance(outer_color, pygame.Color):
            outer_color = pygame.Color(*outer_color)

        outer_color.a = 0
        radius_range = range(radius, min_radius, -max(int(math.ceil((radius - min_radius) / bands)), 1))

        return cls(radius_range, inner_color, outer_color)

    @classmethod
    def from_file(cls, filename: str | bytes | PathLike) -> "Glow":
        """Load glow from shelve file.

        :param filename: Name of the file to load glow from. No extension!
        :return: Loaded glow.
        :raises FileNotFoundError: 1. DBM DIR and/or DAT file not found.
                                   2. File is not a shelve-file.
                                   3. Shelve file doesn't have appropriate keys.
                                   4. File saved using a different pickling protocol.
        """

        try:
            with shelve.open(filename, protocol=HIGHEST_PROTOCOL) as f:
                radius_range = f["radius_range"]
                inner_color = f["inner_color"]
                outer_color = f["outer_color"]
                glow_cycle = f["flicker_buffer"]
        except DBMError:
            raise FileNotFoundError(
                f"Error while loading data from '{filename}'. "
                f"DBM DIR and/or DAT file not found, "
                f"file might not be a shelve file, "
                f"file might not contain the appropriate keys, or"
                f"file might be saved using a different pickling protocol."
            )

        glow_cycle = cycle([pygame.image.fromstring(*flicker_buffer) for flicker_buffer in glow_cycle])
        new = cls(radius_range, inner_color, outer_color)
        new._glow_cycle = glow_cycle

        return new

    def to_file(self, filename: str) -> None:
        """Write glow data to a shelve file.

        :param filename: File to save to.
        """

        first: pygame.Surface = next(self)
        flicker_buffer = [(pygame.image.tostring(first, "RGBA"), first.get_size(), "RGBA")]

        while (glow := next(self)) != first:
            flicker_buffer.append((pygame.image.tostring(glow, "RGBA"), glow.get_size(), "RGBA"))

        with shelve.open(filename, protocol=HIGHEST_PROTOCOL) as f:
            f["radius_range"] = self._radius_range
            f["inner_color"] = self._inner_color
            f["outer_color"] = self._outer_color
            f["flicker_buffer"] = flicker_buffer

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}.uniform(radius: int, color: pygame.Color)\n"
            f"{type(self).__name__}.banded(radius: int, color: pygame.Color, bands: int, min_radius: int = 0)\n"
            f"{type(self).__name__}.uniform_gradient(radius: int, inner_color: pygame.Color, outer_color: pygame.Color)\n"
            f"{type(self).__name__}.banded_gradient(radius: int, inner_color: pygame.Color, outer_color: pygame.Color, bands: int, min_radius: int = 0)\n"
            f"{type(self).__name__}.from_file(filename: str)\n"
        )

    def __str__(self) -> str:
        if (
            self._inner_color.r == self._outer_color.r
            and self._inner_color.g == self._outer_color.g
            and self._inner_color.b == self._outer_color.b
        ):
            return f"{type(self).__name__} of radius {self.radius} and color {self._inner_color}"
        else:
            return f"{type(self).__name__} of radius {self.radius} and inner color {self._inner_color} and outer color {self._outer_color}"

    def __hash__(self) -> int:
        """Make a hash of the glow.

        :return: Hash of the glow.
        """

        inner_rgba = self._inner_color.r, self._inner_color.g, self._inner_color.b, self._inner_color.a
        outer_rgba = self._outer_color.r, self._outer_color.g, self._outer_color.b, self._outer_color.a
        len_glow = len(self)

        return hash((self._radius_range, inner_rgba, outer_rgba, len_glow))

    def __call__(self) -> pygame.Surface:
        return next(self._glow_cycle)

    def __iter__(self) -> Glow:
        return self

    def __next__(self) -> pygame.Surface:
        return next(self._glow_cycle)

    def __len__(self) -> int:
        """Calculate the length of the flicker cycle.

        Note that after calculation flicker cycle will be advanced by one.

        :return: Length of the flicker cycle
        """

        first = next(self)
        length = 1

        while next(self) != first:
            length += 1

        return length

    def __getstate__(self) -> dict:
        """Get the state of the glow for piclking.

        :return: Dict of glow properties.
        """

        first: pygame.Surface = next(self)
        flicker_buffer = [(pygame.image.tostring(first, "RGBA"), first.get_size(), "RGBA")]

        while (glow := next(self)) != first:
            flicker_buffer.append((pygame.image.tostring(glow, "RGBA"), glow.get_size(), "RGBA"))

        state = {
            "radius_range": self._radius_range,
            "inner_color": self._inner_color,
            "outer_color": self._outer_color,
            "flicker_buffer": flicker_buffer,
        }

        return state

    def __setstate__(self, state: dict) -> None:
        """Set the state of the glow in unpickling.

        :param state: State as a dictionary defined in "__getstate__"
        """

        self._radius_range: range = state["radius_range"]
        self._inner_color: pygame.Color = state["inner_color"]
        self._outer_color: pygame.Color = state["outer_color"]
        self._glow_cycle = cycle(
            [pygame.image.fromstring(*flicker_buffer) for flicker_buffer in state["flicker_buffer"]]
        )

    @property
    def radius(self):
        """Get glow radius. Note that this does not work when flicker is set.

        :return: Glow radius
        :rtype: int
        """

        return self._radius_range.start

    @radius.setter
    def radius(self, value):
        """Set glow radius and rebuild glow. Don't set frequently, heavy hit on performance!

        :param value: New radius.
        :type value: int
        """

        self._radius_range = range(value, self._radius_range.stop, self._step_for_radius(value))
        self._glow_cycle = cycle([self._build_glow(self._radius_range, self._inner_color, self._outer_color)])

    @property
    def bands(self) -> int:
        """How many colorbands are used to make glow. Note that this does not work when flicker is set.

        :return: Number of bands.
        :rtype: int
        """

        return len(self._radius_range)

    @property
    def flicker(self) -> cycle:
        """Get the flicker iterable object.

        :return: Flicker itarable.
        """

        return self._glow_cycle

    def set_flicker(self, speed: int, delta: int, lerp_step: bool = False):
        """Set a sinusoidal flickering effect to the particle.

        For complex flickers it is prefered to save the glow to a shelve file using "Glow.to_file(filename)"
        and loading it with Glow.from_file(filename), since flicker construction time can be a few seconds.

        :param speed: Speed at which the filckering occurs. One cycle time = speed / framerate. 1 is slowest possible.
        :param delta: How much the radius of the glow changes +/- from the current radius.
                      Must be less than (radius_range.start - radius_range.stop) or glow will disappear for a part of the cycle.
        :param lerp_step: Change radius_range step in order to maintain glow cicles' ratio to each other.
                          By default, the step is kept constant and min_radius is increased in order to maintain same number of bands.
                          Lerp step method is better suited for uniform glows, since it can make the glow's inner circles appear
                          stuttery for low speeds and small glow sizes for banded glows.

        """

        flicker_list = []
        flicker_radii_cycle = [
            round((math.sin(math.radians(x)) + (self.radius / delta)) * delta) for x in range(0, 360, speed)
        ]

        for radius in flicker_radii_cycle:
            if lerp_step:  # for uniform glow
                radius_range = range(radius, self._radius_range.stop, self._step_for_radius(radius))
            else:  # for banded glow
                radius_range = range(radius, max(radius - self._radius_range.start, 0), self._radius_range.step)

            flicker_list.append(self._build_glow(radius_range, self._inner_color, self._outer_color))

        self._glow_cycle = cycle(flicker_list)

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Draw the glow on screen.

        :param screen: Screen to draw glow in.
        :param x: Glow center x coordinate.
        :param y: Glow center y coordinate.
        """

        glow = next(self)
        screen.blit(glow, (x - glow.get_width() // 2, y - glow.get_height() // 2))

    def copy(self, randomize: bool = False) -> "Glow":
        """Make a copy of the glow.

        :param randomize: Randomize the phase of the glow's flicker. Otherwise copy will be synched to the original.
        :return: New glow.
        """

        new = copy.deepcopy(self)
        if randomize:
            [next(new) for _ in range(random.randint(1, 180))]
        return new

    @staticmethod
    def _build_glow(radius_range: range, inner_color: pygame.Color, outer_color: pygame.Color) -> pygame.Surface:
        """Build glow from arguments.

        :param radius_range: Range of radii for the circles in the glow. From smallest glow circle to largest.
                             Use step in range function to make banding.
        :param inner_color: Glow inner color.
        :param outer_color: Glow outer color.
        :return: Glow surface.
        """

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

    def _step_for_radius(self, radius: int) -> int:
        """Calculate new radius range step in order to maintain similar amount of bands.

        :param radius: New radius to set the glow.
        :return: New step size. Note that step is negative.
        """

        return -max(int(math.ceil((radius - self._radius_range.stop) / len(self._radius_range))), 1)
