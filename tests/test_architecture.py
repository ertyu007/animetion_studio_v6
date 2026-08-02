from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_scene_base_has_no_manual_runtime_introspection() -> None:
    source = (ROOT / "lib" / "scene_base.py").read_text(encoding="utf-8")
    assert "get_run_time" not in source
    assert "prepare_animation" not in source
    assert "VisualPlan" not in source


def test_scenes_use_deferred_beats() -> None:
    for path in (ROOT / "scenes").glob("*.py"):
        if path.name == "__init__.py":
            continue
        source = path.read_text(encoding="utf-8")
        assert "play_cue(" in source
        assert "beat(lambda" in source


def test_legacy_spoiler_workarounds_are_absent() -> None:
    paths = [ROOT / "lib" / "scene_base.py", ROOT / "lib" / "motion.py"]
    paths.extend(path for path in (ROOT / "scenes").glob("*.py") if path.name != "__init__.py")
    runtime_source = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "prepare_for_reveal" not in runtime_source
    assert "narration_beats" not in runtime_source
