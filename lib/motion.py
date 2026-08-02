"""Motion primitives. Every function animates only the current beat."""

from __future__ import annotations

from manim import (
    AddTextLetterByLetter,
    Animation,
    AnimationGroup,
    Circumscribe,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    LEFT,
    RIGHT,
    Succession,
    VGroup,
    Write,
    smooth,
)

from lib.settings import SETTINGS


def write_text(target) -> Animation:
    """Draw glyph strokes; use for titles, headings, and labels."""
    return Write(target, rate_func=smooth)


def type_text(target) -> Animation:
    """Typing reveal reserved for code and terminal content."""
    return AddTextLetterByLetter(target, rate_func=smooth)


def reveal_header(header) -> Animation:
    return AnimationGroup(
        FadeIn(header.badge, shift=LEFT * 0.08, rate_func=smooth),
        Write(header.badge_text, rate_func=smooth),
        Write(header.title_text, rate_func=smooth),
        FadeIn(header.kicker_text, shift=DOWN * 0.05, rate_func=smooth),
        lag_ratio=0.08,
    )


def reveal_card(card) -> Animation:
    return AnimationGroup(
        FadeIn(card.panel, shift=DOWN * 0.06, rate_func=smooth),
        GrowFromCenter(card.marker),
        Write(card.number, rate_func=smooth),
        Write(card.title_text, rate_func=smooth),
        FadeIn(card.detail_text, shift=RIGHT * 0.05, rate_func=smooth),
        lag_ratio=0.07,
    )


def reveal_code(panel) -> Animation:
    shell = VGroup(panel.panel, panel.top_line, panel.dots)
    line_animations = []
    for row in panel.line_groups:
        text_parts = [part for part in row if part.family_members_with_points()]
        if text_parts:
            line_animations.append(LaggedStart(*[type_text(part) for part in text_parts], lag_ratio=0.08))
    return AnimationGroup(
        FadeIn(shell, shift=DOWN * 0.06, rate_func=smooth),
        Write(panel.title_text, rate_func=smooth),
        Succession(*line_animations),
        lag_ratio=0.10,
    )


def reveal_key(key) -> Animation:
    return AnimationGroup(
        FadeIn(key.body, scale=0.92, rate_func=smooth),
        Write(key.text, rate_func=smooth),
        lag_ratio=0.08,
    )


def reveal_stack(board) -> Animation:
    return AnimationGroup(
        FadeIn(board.panel, shift=DOWN * 0.06, rate_func=smooth),
        Write(board.title_text, rate_func=smooth),
        LaggedStart(*[Create(guide) for guide in board.guides], lag_ratio=0.12),
        lag_ratio=0.10,
    )


def reveal_memory(node) -> Animation:
    return AnimationGroup(
        GrowFromCenter(node.circle),
        Write(node.label_text, rate_func=smooth),
        Write(node.value_text, rate_func=smooth),
        lag_ratio=0.10,
    )


def reveal_orb(orb) -> Animation:
    return AnimationGroup(
        GrowFromCenter(VGroup(orb[0], orb[1])),
        FadeIn(orb[2], shift=DOWN * 0.04),
        lag_ratio=0.08,
    )


def focus(target, color=None) -> Animation:
    return Circumscribe(
        target,
        color=color or SETTINGS.palette.yellow,
        fade_out=True,
        time_width=0.35,
    )


def disappear(target, shift=None) -> Animation:
    return FadeOut(target, shift=shift, rate_func=smooth)
