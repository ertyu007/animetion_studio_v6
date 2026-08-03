"""Central visual and timing settings for Animetion Studio v6."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class Palette:
    background: str = "#080B14"
    background_soft: str = "#0D1322"
    surface: str = "#121A2A"
    surface_raised: str = "#18243A"
    border: str = "#2A3955"
    text: str = "#F5F7FB"
    muted: str = "#C9D2E7"
    cyan: str = "#5DE4C7"
    blue: str = "#60A5FA"
    purple: str = "#A78BFA"
    yellow: str = "#F6C453"
    coral: str = "#FB7185"
    green: str = "#6EE7A8"


@dataclass(frozen=True)
class Typography:
    font_candidates: Tuple[str, ...] = (
        "Noto Sans Thai",
        "Leelawadee UI",
        "Tahoma",
        "Arial",
    )
    mono_candidates: Tuple[str, ...] = (
        "JetBrains Mono",
        "Cascadia Code",
        "Consolas",
    )
    display: float = 58
    heading: float = 34
    body: float = 26
    small: float = 20
    caption: float = 25


@dataclass(frozen=True)
class Layout:
    frame_width: float = 9.0
    frame_height: float = 16.0
    safe_width: float = 7.8
    safe_top: float = 6.55
    safe_bottom: float = -6.30
    caption_y: float = -4.00
    header_y: float = 2.21


@dataclass(frozen=True)
class Timing:
    cue_lead: float = 0.08
    cue_tail: float = 0.06
    section_exit: float = 0.26
    minimum_beat: float = 0.18
    caption_fade: float = 0.12


@dataclass(frozen=True)
class ProjectSettings:
    palette: Palette = field(default_factory=Palette)
    typography: Typography = field(default_factory=Typography)
    layout: Layout = field(default_factory=Layout)
    timing: Timing = field(default_factory=Timing)


SETTINGS = ProjectSettings()
