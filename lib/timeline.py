"""Deferred animation beats; factories prevent future objects being set up early."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol, Union


class AnimationLike(Protocol):
    pass


AnimationFactory = Callable[[], Optional[AnimationLike]]


@dataclass(frozen=True)
class CueBeat:
    build: AnimationFactory
    weight: float = 1.0
    caption: str = ""
    name: str = "beat"

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError("beat weight must be positive")


def beat(
    factory: AnimationFactory,
    *,
    weight: float = 1.0,
    caption: str = "",
    name: str = "beat",
) -> CueBeat:
    return CueBeat(factory, weight, caption, name)


def pause(*, weight: float = 1.0, caption: str = "", name: str = "pause") -> CueBeat:
    return CueBeat(lambda: None, weight, caption, name)
