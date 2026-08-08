"""Scene สำหรับตอน pointer_deref."""

from __future__ import annotations

from manim import (
    AnimationGroup,
    DOWN,
    FadeIn,
    RoundedRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    YELLOW,
)

from content.pointer_deref import SCRIPT
from lib.scene_base import NarratedScene
from lib.timeline import beat


class PointerDerefV1(NarratedScene):
    """อธิบาย pointer_deref"""

    def construct(self) -> None:
        self.build_stage()
        self.show_hook()
        self.show_concept()
        self.show_example()
        self.show_summary()
        self.show_cta()

    def make_text(self, text: str, *, size: int = 42, color=WHITE, weight: str = "NORMAL") -> Text:
        return Text(text, font_size=size, color=color, weight=weight)

    def make_panel(self, width: float = 6.6, height: float = 1.8, *, title: str | None = None) -> VGroup:
        box = RoundedRectangle(width=width, height=height, corner_radius=0.18, stroke_width=2.5, color=YELLOW, fill_opacity=0.08)
        group = VGroup(box)
        if title:
            header = self.make_text(title, size=26, color=YELLOW, weight="BOLD")
            header.next_to(box.get_top(), DOWN, buff=0.2)
            group.add(header)
        return group

    def show_hook(self) -> None:
        cue = SCRIPT.cue("hook")
        title = self.make_text("เปิดเรื่อง", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="เปิดเรื่อง")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: FadeIn(panel), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )

    def show_concept(self) -> None:
        cue = SCRIPT.cue("concept")
        title = self.make_text("แนวคิด", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="แนวคิด")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: FadeIn(panel), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )

    def show_example(self) -> None:
        cue = SCRIPT.cue("example")
        title = self.make_text("ตัวอย่าง", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="ตัวอย่าง")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: FadeIn(panel), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )

    def show_summary(self) -> None:
        cue = SCRIPT.cue("summary")
        title = self.make_text("สรุป", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="สรุป")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: FadeIn(panel), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )

    def show_cta(self) -> None:
        cue = SCRIPT.cue("cta")
        title = self.make_text("ติดตาม", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="ติดตาม")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: FadeIn(panel), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )

