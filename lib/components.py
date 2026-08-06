"""New v6 visual system: neon blueprint panels for portrait video."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional, Sequence, Tuple

from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    RIGHT,
    UP,
    Arrow,
    Circle,
    Dot,
    Line,
    Mobject,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
)

from lib.settings import SETTINGS, ProjectSettings
from lib.text import parse_highlights, wrap_text


@lru_cache(maxsize=8)
def _font(candidates: Tuple[str, ...]) -> str:
    try:
        from manimpango import list_fonts

        installed = set(list_fonts())
        for candidate in candidates:
            if candidate in installed:
                return candidate
    except Exception:
        pass
    return candidates[0]


def accent(name: str, settings: ProjectSettings = SETTINGS) -> str:
    palette = settings.palette
    values = {
        "cyan": palette.cyan,
        "blue": palette.blue,
        "purple": palette.purple,
        "yellow": palette.yellow,
        "coral": palette.coral,
        "green": palette.green,
        "muted": palette.muted,
    }
    return values.get(name.lower(), name)


class ThaiText(Text):
    def __init__(
        self,
        text: str,
        font_size: float = 28,
        color: Optional[str] = None,
        weight: str = NORMAL,
        *,
        mono: bool = False,
        max_width: Optional[float] = None,
        stroke_width: float = 0.8,
        stroke_color: Optional[str] = None,
        settings: ProjectSettings = SETTINGS,
        **kwargs,
    ) -> None:
        # ฟอนต์ mono (เช่น JetBrains Mono / Fira Code) ไม่มีชุดตัวอักษรไทย
        # ถ้าข้อความมีตัวอักษรไทยปนอยู่ ให้ใช้ฟอนต์ไทยปกติเสมอ แม้จะขอ mono=True มาก็ตาม
        # ป้องกันปัญหา tofu box (กล่องเลขฮ่) ที่เกิดกับ KeyCap / MemoryNode / SectionHeader ฯลฯ
        mono_effective = mono and all(ord(ch) < 128 for ch in text)
        candidates = settings.typography.mono_candidates if mono_effective else settings.typography.font_candidates
        super().__init__(
            text,
            font=_font(candidates),
            font_size=font_size,
            color=color or settings.palette.text,
            weight=weight,
            line_spacing=0.82,
        stroke_width=stroke_width,
        stroke_color=stroke_color or settings.palette.text,
            **kwargs,
        )
        if max_width is not None and self.width > max_width:
            self.scale_to_fit_width(max_width)


class BlueprintBackground(VGroup):
    def __init__(self, settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        base = Rectangle(
            width=settings.layout.frame_width,
            height=settings.layout.frame_height,
            stroke_width=0,
            fill_color=p.background,
            fill_opacity=1,
        )
        grid = VGroup()
        for x in (-3.0, -1.5, 0, 1.5, 3.0):
            grid.add(Line([x, -8, 0], [x, 8, 0], color=p.border, stroke_width=0.45, stroke_opacity=0.22))
        for y in (-6, -4, -2, 0, 2, 4, 6):
            grid.add(Line([-4.5, y, 0], [4.5, y, 0], color=p.border, stroke_width=0.45, stroke_opacity=0.18))
        halo = Circle(radius=3.2, stroke_color=p.purple, stroke_width=1.0, stroke_opacity=0.12).shift(UP * 3.6 + RIGHT * 2.2)
        super().__init__(base, grid, halo)
        self.set_z_index(-100, family=True)


class BrandBar(VGroup):
    def __init__(self, settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        dot = Dot(radius=0.09, color=p.cyan)
        title = ThaiText("BYTE MOTION", 18, p.text, BOLD, mono=True)
        group = VGroup(dot, title).arrange(RIGHT, buff=0.12)
        super().__init__(*group)


class SectionHeader(VGroup):
    def __init__(self, index: str, title: str, kicker: str, color: str = "cyan", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        badge = RoundedRectangle(width=0.86, height=0.42, corner_radius=0.18, stroke_width=0, fill_color=c, fill_opacity=1)
        badge_text = ThaiText(index, 17, p.background, BOLD, mono=True).move_to(badge)
        title_text = ThaiText(title, settings.typography.heading, p.text, BOLD, max_width=6.5)
        top = VGroup(VGroup(badge, badge_text), title_text).arrange(RIGHT, buff=0.20)
        kicker_text = ThaiText(kicker, settings.typography.small, p.muted, max_width=settings.layout.safe_width)
        group = VGroup(top, kicker_text).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        super().__init__(*group)
        self.badge = badge
        self.badge_text = badge_text
        self.title_text = title_text
        self.kicker_text = kicker_text


class NeonPanel(VGroup):
    def __init__(self, width: float, height: float, color: str = "cyan", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        shadow = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.22,
            stroke_width=0,
            fill_color="#000000",
            fill_opacity=0.20,
        ).shift(DOWN * 0.07 + RIGHT * 0.05)
        body = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.22,
            stroke_color=p.border,
            stroke_width=1.4,
            fill_color=p.surface,
            fill_opacity=0.98,
        )
        rail = RoundedRectangle(
            width=0.08,
            height=max(0.25, height - 0.28),
            corner_radius=0.04,
            stroke_width=0,
            fill_color=c,
            fill_opacity=1,
        ).move_to(body.get_left() + RIGHT * 0.16)
        super().__init__(shadow, body, rail)
        self.body = body
        self.rail = rail
        self.color = c


class StepCard(VGroup):
    def __init__(self, index: str, title: str, detail: str, color: str = "cyan", width: float = 7.0, height: float = 0.95, settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        panel = NeonPanel(width, height, color, settings)
        c = accent(color, settings)
        marker = Circle(radius=0.20, stroke_color=c, stroke_width=1.5, fill_color=p.surface_raised, fill_opacity=1)
        number = ThaiText(index, 15, c, BOLD, mono=True).move_to(marker)
        title_text = ThaiText(title, 22, p.text, BOLD, mono=True, max_width=2.85)
        detail_text = ThaiText(detail, 20, p.muted, max_width=3.35)
        left_group = VGroup(marker, title_text).arrange(RIGHT, buff=0.16)
        left_group.move_to(panel.body.get_left() + RIGHT * 1.85)
        detail_text.move_to(panel.body.get_right() + LEFT * 1.85)
        super().__init__(panel, marker, number, title_text, detail_text)
        self.panel = panel
        self.marker = marker
        self.number = number
        self.title_text = title_text
        self.detail_text = detail_text


class CodePanel(VGroup):
    def __init__(self, lines: Sequence[Tuple[str, str]], title: str = "code", width: float = 7.1, height: float = 2.4, color: str = "green", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        panel = NeonPanel(width, height, color, settings)
        top_line = Line(panel.body.get_left() + UP * (height / 2 - 0.48) + RIGHT * 0.2, panel.body.get_right() + UP * (height / 2 - 0.48) + LEFT * 0.2, color=p.border, stroke_width=1)
        dots = VGroup(*[Dot(radius=0.045, color=value) for value in (p.coral, p.yellow, p.green)]).arrange(RIGHT, buff=0.08)
        dots.move_to(panel.body.get_left() + RIGHT * 0.45 + UP * (height / 2 - 0.25))
        title_text = ThaiText(title, 16, p.muted, BOLD, mono=True).move_to(panel.body.get_top() + DOWN * 0.25)
        line_groups = VGroup()
        available = height - 0.72
        spacing = available / max(1, len(lines))
        for index, (prefix, code) in enumerate(lines):
            prefix_text = ThaiText(prefix, 18, p.muted, mono=True)
            code_text = ThaiText(code, 23, p.text, mono=True, max_width=5.8)
            row = VGroup(prefix_text, code_text).arrange(RIGHT, buff=0.18)
            y = panel.body.get_top()[1] - 0.72 - spacing * (index + 0.5)
            row.move_to([panel.body.get_left()[0] + 0.55 + row.width / 2, y, 0])
            line_groups.add(row)
        super().__init__(panel, top_line, dots, title_text, line_groups)
        self.panel = panel
        self.top_line = top_line
        self.dots = dots
        self.title_text = title_text
        self.line_groups = line_groups


class KeyCap(VGroup):
    def __init__(self, label: str, color: str = "cyan", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        body = RoundedRectangle(width=2.5, height=0.72, corner_radius=0.18, stroke_color=c, stroke_width=1.6, fill_color=p.surface_raised, fill_opacity=1)
        text = ThaiText(label, 24, p.text, BOLD, mono=True).move_to(body)
        super().__init__(body, text)
        self.body = body
        self.text = text


class DataOrb(VGroup):
    def __init__(self, label: str, color: str = "yellow", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        outer = Circle(radius=0.34, stroke_color=c, stroke_width=2.0, fill_color=p.surface_raised, fill_opacity=1)
        inner = Circle(radius=0.12, stroke_width=0, fill_color=c, fill_opacity=0.45)
        text = ThaiText(label, 15, p.text, BOLD, mono=True).next_to(outer, DOWN, buff=0.08)
        super().__init__(outer, inner, text)


class StackBoard(VGroup):
    def __init__(self, title: str, color: str, slots: int = 3, settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        panel = NeonPanel(3.25, 3.25, color, settings)
        title_text = ThaiText(title, 21, c, BOLD, mono=True).move_to(panel.body.get_top() + DOWN * 0.34)
        guides = VGroup()
        slot_centers = []
        for index in range(slots):
            y = panel.body.get_bottom()[1] + 0.52 + index * 0.72
            guide = RoundedRectangle(width=2.62, height=0.54, corner_radius=0.12, stroke_color=p.border, stroke_width=1, fill_opacity=0)
            guide.move_to([panel.body.get_center()[0], y, 0])
            guides.add(guide)
            slot_centers.append(guide.get_center())
        super().__init__(panel, title_text, guides)
        self.panel = panel
        self.title_text = title_text
        self.guides = guides
        self._slot_centers = slot_centers
        self.item_color = c

    def slot_center(self, index: int):
        return self._slot_centers[index]

    def make_item(self, label: str, settings: ProjectSettings = SETTINGS) -> VGroup:
        p = settings.palette
        body = RoundedRectangle(width=2.44, height=0.46, corner_radius=0.10, stroke_color=self.item_color, stroke_width=1.2, fill_color=p.surface_raised, fill_opacity=1)
        text = ThaiText(label, 17, p.text, BOLD, max_width=2.12).move_to(body)
        return VGroup(body, text)


class MemoryNode(VGroup):
    def __init__(self, label: str, value: str, color: str = "purple", settings: ProjectSettings = SETTINGS) -> None:
        p = settings.palette
        c = accent(color, settings)
        circle = Circle(radius=0.72, stroke_color=c, stroke_width=2, fill_color=p.surface_raised, fill_opacity=1)
        label_text = ThaiText(label, 16, c, BOLD, mono=True).next_to(circle, UP, buff=0.10)
        value_text = ThaiText(value, 26, p.text, BOLD, mono=True).move_to(circle)
        super().__init__(circle, label_text, value_text)
        self.circle = circle
        self.label_text = label_text
        self.value_text = value_text


class Caption(VGroup):
    def __init__(self, phrase: str, settings: ProjectSettings = SETTINGS) -> None:
        clean, highlights = parse_highlights(phrase)
        label = ThaiText(
            wrap_text(clean, 30, 2),
            settings.typography.caption,
            settings.palette.text,
            BOLD,
            max_width=6.9,
            t2c={keyword: settings.palette.yellow for keyword in highlights},
        )
        super().__init__(label)


def connector(start: Mobject, end: Mobject, color: str = "muted", settings: ProjectSettings = SETTINGS) -> Arrow:
    return Arrow(
        start.get_right(),
        end.get_left(),
        buff=0.12,
        color=accent(color, settings),
        stroke_width=2,
        max_tip_length_to_length_ratio=0.18,
    )