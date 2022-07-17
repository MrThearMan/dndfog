from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable

import pygame
import pygame.freetype


pygame.freetype.init()


__all__ = [
    "FPS",
    "exectime",
    "true_fps",
]


class FPS:
    def __init__(self, decimals: int = None):
        self.decimals = decimals
        self.font = pygame.freetype.SysFont("Arial", 20, bold=True)

        self.display_caption: str = x[0] if len((x := pygame.display.get_caption())) > 0 else ""

        self.frame_start_time = perf_counter()
        self.frame_end_time = perf_counter()
        self.frame_times: list[float] = []

        self.current = 0
        self.min = float("inf")
        self.max = 0

        self.__setup = True

    def __str__(self) -> str:
        return str(round(self.current))

    def __iter__(self) -> "FPS":
        return self

    def __next__(self) -> float:
        if self.__setup:
            self.__setup = False
            self.frame_start_time = perf_counter()

        self.frame_end_time = perf_counter()

        self.frame_times.append(self.frame_end_time - self.frame_start_time)
        self.frame_times[:] = self.frame_times[-20:]

        try:
            self.current = round(len(self.frame_times) / sum(self.frame_times), self.decimals)  # noqa

            if self.current < self.min:
                self.min = self.current
            if self.current > self.max:
                self.max = self.current

        except ZeroDivisionError:
            self.current = float("inf")

        return self.current

    def start(self) -> None:
        self.frame_start_time = perf_counter()

    end = __next__
    stop = __next__

    def blit(self, screen: "pygame.Surface") -> None:
        self.font.render_to(screen, (3, 3), "Cur. " + str(self.current), fgcolor=(0, 0, 255))
        self.font.render_to(screen, (3, 23), "Min. " + str(self.min), fgcolor=(255, 0, 0))
        self.font.render_to(screen, (3, 43), "Max. " + str(self.max), fgcolor=(0, 255, 0))

    def to_display_caption(self, *, show_min: bool = False, show_max: bool = False, **kwargs: Any) -> None:
        default = f"{self.display_caption} - fps: {self.current}"
        if show_min:
            default += f" - min: {self.min}"
        if show_max:
            default += f" - max: {self.max}"
        default += "".join([f" - {key}: {value}" for key, value in kwargs.items()])
        pygame.display.set_caption(default)

    def reset(self) -> None:
        self.frame_times = []

        self.current = 0
        self.min = float("inf")
        self.max = 0

    @contextmanager
    def track(self, *, show_min: bool = False, show_max: bool = False, **kwargs: Any):
        """Track fps in the display caption by using this as the context manager for pygame.time.Clock.tick()."""
        self.stop()
        self.to_display_caption(show_min=show_min, show_max=show_max, **kwargs)
        yield
        self.start()


true_fps = FPS()


def exectime(function: Callable[..., Any]):
    """Time the execution of a function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Wrap the function execution."""
        start = perf_counter()
        value = function(*args, **kwargs)
        print(perf_counter() - start)
        return value

    return wrapper
