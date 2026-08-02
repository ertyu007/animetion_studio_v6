"""Static validation that runs before Manim rendering."""

from __future__ import annotations

import ast
import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from content.models import Episode
from lib.text import markup_is_balanced


VOICE_NAME = re.compile(r"^[a-z]{2}-[A-Z]{2}-[A-Za-z]+Neural$")


@dataclass(frozen=True)
class Issue:
    level: str
    message: str


def validate_episode(episode: Episode, root: Path) -> Tuple[Issue, ...]:
    issues: list[Issue] = []
    scene_path = (root / episode.scene_file).resolve()
    try:
        scene_path.relative_to(root.resolve())
    except ValueError:
        issues.append(Issue("ERROR", f"scene path escapes project root: {episode.scene_file}"))
        return tuple(issues)
    if not scene_path.is_file():
        issues.append(Issue("ERROR", f"scene file does not exist: {episode.scene_file}"))
        return tuple(issues)
    try:
        source = scene_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError) as exc:
        issues.append(Issue("ERROR", f"cannot parse {episode.scene_file}: {exc}"))
        return tuple(issues)

    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    if episode.scene_class not in classes:
        issues.append(Issue("ERROR", f"scene class {episode.scene_class!r} missing from {episode.scene_file}"))

    forbidden = {
        "VisualPlan": "legacy VisualPlan is forbidden in v6",
        "get_run_time": "manual get_run_time timing is forbidden in v6",
        "prepare_for_reveal": "opacity pre-hide workaround is forbidden in v6",
        "narration_beats": "legacy prebuilt narration timeline is forbidden in v6",
    }
    for token, message in forbidden.items():
        if token in source:
            issues.append(Issue("ERROR", f"{episode.scene_file}: {message}"))
    if "play_cue(" not in source:
        issues.append(Issue("ERROR", f"{episode.scene_file}: no play_cue() calls found"))

    seen: set[str] = set()
    for cue in episode.cues:
        if cue.key in seen:
            issues.append(Issue("ERROR", f"duplicate cue key: {cue.key}"))
        seen.add(cue.key)
        if not cue.text.strip():
            issues.append(Issue("ERROR", f"empty narration text: {cue.key}"))
        if not VOICE_NAME.match(cue.voice.name):
            issues.append(Issue("ERROR", f"invalid voice name in {cue.key}: {cue.voice.name}"))
        for phrase in cue.subtitle_beats:
            if not markup_is_balanced(phrase):
                issues.append(Issue("ERROR", f"invalid subtitle markup in {cue.key}: {phrase}"))
    return tuple(issues)


def dependency_issues() -> Tuple[Issue, ...]:
    issues: list[Issue] = []
    for module, label in (("manim", "Manim"), ("edge_tts", "Edge TTS"), ("mutagen", "Mutagen")):
        if importlib.util.find_spec(module) is None:
            issues.append(Issue("WARN", f"{label} is not installed in this environment"))
    return tuple(issues)


def validate_many(episodes: Iterable[Episode], root: Path) -> Tuple[Issue, ...]:
    issues: list[Issue] = []
    for episode in episodes:
        issues.extend(validate_episode(episode, root))
    issues.extend(dependency_issues())
    return tuple(issues)
