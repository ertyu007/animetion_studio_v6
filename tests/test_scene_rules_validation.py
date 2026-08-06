"""Tests for scene/content consistency rules caught by static validation."""

from pathlib import Path

from content.models import Episode
from lib.narration import NarrationCue
from lib.validation import validate_episode


SCENE_TEMPLATE = """\
from lib.scene_base import NarratedScene
from lib.timeline import beat
from content.demo import SCRIPT


class DemoV1(NarratedScene):
    def construct(self) -> None:
        self.build_stage()
        self.show_main()

    def show_main(self) -> None:
        cue = SCRIPT.cue("{cue_key}")
        self.play_cue(
            cue,
            (
                beat(lambda: None, weight=1.0, caption=cue.subtitle_beats[0]),
                {extra_beat}
            ),
        )
"""


def make_cue(key: str, subtitles=("first",), min_duration: float = 1.2) -> NarrationCue:
    return NarrationCue(key=key, text="ข้อความบรรยาย", subtitle_beats=subtitles, min_duration=min_duration)


def validate(tmp_path: Path, scene_source: str, cues) -> list:
    (tmp_path / "scene.py").write_text(scene_source, encoding="utf-8")
    episode = Episode(
        key="demo",
        title="Demo",
        scene_file="scene.py",
        scene_class="DemoV1",
        cues=tuple(cues),
    )
    return [issue for issue in validate_episode(episode, tmp_path) if issue.level == "ERROR"]


def error_messages(issues) -> list:
    return [issue.message for issue in issues]


def test_valid_scene_passes(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    assert validate(tmp_path, source, (make_cue("main"),)) == []


def test_unknown_cue_key_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="nope", extra_beat="")
    messages = error_messages(validate(tmp_path, source, (make_cue("main"),)))
    assert any("unknown cue key 'nope'" in message for message in messages)


def test_beat_count_mismatch_reported(tmp_path: Path) -> None:
    extra = "beat(lambda: None, weight=1.0, caption=cue.subtitle_beats[0]),"
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat=extra)
    messages = error_messages(validate(tmp_path, source, (make_cue("main", ("first",)),)))
    assert any("has 2 beat(s) but 1 subtitle_beats" in message for message in messages)


def test_caption_index_out_of_range_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = make_cue("main", ("only-one",))
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert not any("caption index" in message for message in messages)

    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = NarrationCue(
        key="main",
        text="ข้อความ",
        subtitle_beats=(),
    )
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert any("caption index 0 out of range" in message for message in messages)


def test_never_played_cue_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    messages = error_messages(validate(tmp_path, source, (make_cue("main"), make_cue("extra"))))
    assert any("never played" in message for message in messages)


def test_build_stage_with_count_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="").replace("self.build_stage()", "self.build_stage(3)")
    messages = error_messages(validate(tmp_path, source, (make_cue("main"),)))
    assert any("build_stage() no longer takes a section count" in message for message in messages)


def test_subtitle_too_long_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    messages = error_messages(validate(tmp_path, source, (make_cue("main", ("x" * 40,)),)))
    assert any("subtitle too long" in message for message in messages)


def test_non_positive_min_duration_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    messages = error_messages(validate(tmp_path, source, (make_cue("main", min_duration=0.0),)))
    assert any("min_duration must be positive" in message for message in messages)


def test_non_positive_beat_weight_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    source = source.replace("weight=1.0", "weight=-1.0")
    messages = error_messages(validate(tmp_path, source, (make_cue("main"),)))
    assert any("non-positive beat weight" in message for message in messages)


def test_bare_english_term_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = NarrationCue(key="main", text="ใช้คำสั่ง digitalWrite แล้ว", subtitle_beats=("x",))
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert any("bare English term(s)" in message and "digitalWrite" in message for message in messages)


def test_short_english_acronym_allowed(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = NarrationCue(key="main", text="แอลอีดี กับ LED ใช้งานได้", subtitle_beats=("x",))
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert not any("bare English term(s)" in message for message in messages)


def test_narration_too_long_reported(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = NarrationCue(key="main", text="ย" * 121, subtitle_beats=("x",))
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert any("narration too long" in message for message in messages)


def test_narration_at_limit_allowed(tmp_path: Path) -> None:
    source = SCENE_TEMPLATE.format(cue_key="main", extra_beat="")
    cue = NarrationCue(key="main", text="ย" * 120, subtitle_beats=("x",))
    messages = error_messages(validate(tmp_path, source, (cue,)))
    assert not any("narration too long" in message for message in messages)
