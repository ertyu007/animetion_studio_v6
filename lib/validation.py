"""Static validation that runs before Manim rendering."""

from __future__ import annotations

import ast
import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

from content.models import Episode
from lib.text import markup_is_balanced


VOICE_NAME = re.compile(r"^[a-z]{2}-[A-Z]{2}-[A-Za-z]+Neural$")

MAX_SUBTITLE_CHARS = 35
MAX_NARRATION_CHARS = 120
ENGLISH_WORD = re.compile(r"[A-Za-z]{4,}")
ENGLISH_ALLOWLIST: frozenset = frozenset()


def _cue_key_from_call(call: ast.Call) -> Optional[str]:
    """Return the cue key for ``SCRIPT.cue("key")`` or ``None``."""
    if (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "cue"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "SCRIPT"
        and call.args
        and isinstance(call.args[0], ast.Constant)
        and isinstance(call.args[0].value, str)
    ):
        return call.args[0].value
    return None


def _function_bindings(function: ast.FunctionDef) -> Dict[str, str]:
    """Map local variable name -> cue key inside one function scope."""
    bindings: Dict[str, str] = {}
    for node in ast.walk(function):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                key = _cue_key_from_call(node.value)
                if key is not None:
                    bindings[target.id] = key
    return bindings


def _scene_functions(tree: ast.AST) -> Tuple[ast.FunctionDef, ...]:
    return tuple(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))


def _caption_subscript_index(call: ast.Call) -> Optional[int]:
    """Return the integer index of ``caption=cue.subtitle_beats[N]`` if any."""
    for keyword in call.keywords:
        if keyword.arg != "caption" or not isinstance(keyword.value, ast.Subscript):
            continue
        value = keyword.value
        if (
            isinstance(value.value, ast.Attribute)
            and value.value.attr == "subtitle_beats"
            and isinstance(value.slice, ast.Constant)
            and isinstance(value.slice.value, int)
        ):
            return value.slice.value
    return None


def _beat_weight(call: ast.Call) -> Optional[float]:
    for keyword in call.keywords:
        if keyword.arg != "weight":
            continue
        value = keyword.value
        try:
            if isinstance(value, ast.Constant):
                return float(value.value)
            if isinstance(value, ast.UnaryOp) and isinstance(value.op, (ast.USub, ast.UAdd)):
                if isinstance(value.operand, ast.Constant):
                    number = float(value.operand.value)
                    return -number if isinstance(value.op, ast.USub) else number
        except (TypeError, ValueError):
            return None
    return None


def _play_cue_sites(tree: ast.AST):
    """Yield (cue_key_or_None, beat_count, max_caption_index, weight_issues).

    Each play_cue call is resolved with the cue bindings of its own enclosing
    function, so reusing a variable name like ``cue`` across sections stays correct.
    """
    for function in _scene_functions(tree):
        bindings = _function_bindings(function)
        for node in ast.walk(function):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "play_cue"
                and node.args
            ):
                continue
            first = node.args[0]
            cue_key = bindings.get(first.id) if isinstance(first, ast.Name) else None
            beats = node.args[1] if len(node.args) > 1 else None
            beat_count: Optional[int] = None
            max_caption_index = -1
            weight_issues: list[str] = []
            if isinstance(beats, (ast.Tuple, ast.List)):
                beat_count = len(beats.elts)
                for element in beats.elts:
                    if not isinstance(element, ast.Call):
                        continue
                    index = _caption_subscript_index(element)
                    if index is not None:
                        max_caption_index = max(max_caption_index, index)
                    weight = _beat_weight(element)
                    if weight is not None and weight <= 0:
                        weight_issues.append(str(weight))
            yield (cue_key, beat_count, max_caption_index, weight_issues)


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
        if len(cue.text.strip()) > MAX_NARRATION_CHARS:
            issues.append(
                Issue(
                    "ERROR",
                    f"narration too long ({len(cue.text.strip())} > {MAX_NARRATION_CHARS} chars) in {cue.key}: "
                    f"break it into breathing chunks",
                )
            )
        bare = sorted(set(ENGLISH_WORD.findall(cue.text)) - ENGLISH_ALLOWLIST)
        if bare:
            issues.append(
                Issue(
                    "ERROR",
                    f"bare English term(s) in {cue.key} narration need Thai reading (คำอ่าน): {', '.join(bare)}",
                )
            )
        for phrase in cue.subtitle_beats:
            if not markup_is_balanced(phrase):
                issues.append(Issue("ERROR", f"invalid subtitle markup in {cue.key}: {phrase}"))
            if len(phrase) > MAX_SUBTITLE_CHARS:
                issues.append(
                    Issue(
                        "ERROR",
                        f"subtitle too long ({len(phrase)} > {MAX_SUBTITLE_CHARS} chars) in {cue.key}: {phrase!r}",
                    )
                )
        if cue.min_duration <= 0:
            issues.append(Issue("ERROR", f"cue min_duration must be positive: {cue.key}"))

    cue_map = {cue.key: cue for cue in episode.cues}
    used_keys: set[str] = set()
    bound_keys: set[str] = set()
    for function in _scene_functions(tree):
        bound_keys.update(_function_bindings(function).values())
    for cue_key, beat_count, max_caption_index, weight_issues in _play_cue_sites(tree):
        if cue_key is None:
            continue
        used_keys.add(cue_key)
        if weight_issues:
            issues.append(
                Issue("ERROR", f"{episode.scene_file}: cue {cue_key!r} has non-positive beat weight(s): {', '.join(weight_issues)}")
            )
        cue = cue_map.get(cue_key)
        if cue is None:
            continue
        subtitles = cue.subtitle_beats
        if beat_count is not None and subtitles and beat_count != len(subtitles):
            issues.append(
                Issue(
                    "ERROR",
                    f"{episode.scene_file}: cue {cue_key!r} has {beat_count} beat(s) but {len(subtitles)} subtitle_beats",
                )
            )
        if max_caption_index >= 0 and max_caption_index >= len(subtitles):
            issues.append(
                Issue(
                    "ERROR",
                    f"{episode.scene_file}: cue {cue_key!r} caption index {max_caption_index} out of range "
                    f"(only {len(subtitles)} subtitle_beats)",
                )
            )

    for key in bound_keys:
        if key not in cue_map:
            issues.append(Issue("ERROR", f"unknown cue key {key!r} in {episode.scene_file}"))

    for cue in episode.cues:
        if cue.key not in used_keys:
            issues.append(Issue("ERROR", f"cue {cue.key!r} is never played in {episode.scene_file}"))

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "build_stage"
            and node.args
        ):
            issues.append(
                Issue(
                    "ERROR",
                    f"{episode.scene_file}: build_stage() no longer takes a section count (progress dots were removed)",
                )
            )
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
