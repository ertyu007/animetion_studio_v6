"""Content models with no Manim dependency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from lib.narration import NarrationCue


@dataclass(frozen=True)
class Episode:
    key: str
    title: str
    scene_file: str
    scene_class: str
    cues: Tuple[NarrationCue, ...]
    tags: Tuple[str, ...] = ()

    def cue(self, key: str) -> NarrationCue:
        for cue in self.cues:
            if cue.key == key:
                return cue
        raise KeyError(f"unknown cue: {key}")

    @property
    def cue_keys(self) -> Sequence[str]:
        return tuple(cue.key for cue in self.cues)
