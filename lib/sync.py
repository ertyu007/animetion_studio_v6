"""Pure timing allocation; intentionally independent from Manim."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class CueSchedule:
    lead: float
    beats: Tuple[float, ...]
    exit: float
    tail: float

    @property
    def total(self) -> float:
        return self.lead + sum(self.beats) + self.exit + self.tail


def allocate_beats(weights: Iterable[float], total: float, minimum: float = 0.18) -> Tuple[float, ...]:
    values = tuple(float(value) for value in weights)
    if total < 0 or minimum < 0:
        raise ValueError("total and minimum must be non-negative")
    if any(value <= 0 for value in values):
        raise ValueError("beat weights must be positive")
    if not values:
        return ()
    count = len(values)
    if total <= minimum * count:
        weight_sum = sum(values)
        return tuple(total * value / weight_sum for value in values)
    remainder = total - (minimum * count)
    weight_sum = sum(values)
    return tuple(minimum + remainder * value / weight_sum for value in values)


def make_schedule(
    weights: Iterable[float],
    total: float,
    *,
    lead: float = 0.08,
    exit: float = 0.26,
    tail: float = 0.06,
    minimum_beat: float = 0.18,
    has_cleanup: bool = True,
) -> CueSchedule:
    if total <= 0:
        raise ValueError("total must be positive")
    fixed = lead + tail + (exit if has_cleanup else 0.0)
    if fixed > total:
        scale = total / fixed if fixed else 0.0
        lead *= scale
        tail *= scale
        exit = exit * scale if has_cleanup else 0.0
    else:
        exit = exit if has_cleanup else 0.0
    beat_budget = max(0.0, total - lead - tail - exit)
    beats = allocate_beats(weights, beat_budget, minimum_beat)
    return CueSchedule(lead, beats, exit, tail)
