from pathlib import Path

from lib.components import CodePanel
from lib.motion import reveal_code


def test_reveal_code_skips_empty_text_parts() -> None:
    panel = CodePanel([("", "Hello World"), ("+", "Hello")])

    reveal_code(panel)


def test_motion_uses_manim_vectors_for_shift() -> None:
    motion_path = Path(__import__("lib.motion", fromlist=["__file__"]).__file__)

    assert "shift=[" not in motion_path.read_text(encoding="utf-8")
