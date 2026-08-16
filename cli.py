"""Command line interface for Animetion Studio v6."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from content.registry import EPISODES, get_episode
from lib.copilot import DEFAULT_HOST, DEFAULT_MODEL, CopilotError, generate_episode
from lib.narration import EdgeTTSRenderer
from lib.validation import validate_many


ROOT = Path(__file__).resolve().parent


def selected_episodes(key: str):
    return tuple(EPISODES.values()) if key == "all" else (get_episode(key),)


def command_list(_args: argparse.Namespace) -> int:
    for key, episode in EPISODES.items():
        print(f"{key:18} {episode.title}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    issues = validate_many(selected_episodes(args.episode), ROOT)
    errors = 0
    for issue in issues:
        print(f"[{issue.level}] {issue.message}")
        errors += issue.level == "ERROR"
    if not issues:
        print("[OK] no validation issues")
    elif not errors:
        print("[OK] validation passed with environment warnings")
    return 1 if errors else 0


def command_audio(args: argparse.Namespace) -> int:
    renderer = EdgeTTSRenderer(mode="auto")
    failed = 0
    for episode in selected_episodes(args.episode):
        print(f"\n[{episode.key}]")
        for cue in episode.cues:
            result = renderer.render(cue, force=args.force)
            if result.error:
                failed += 1
                print(f"  ERROR {cue.key}: {result.error}")
            else:
                state = "NEW" if result.generated else "CACHE"
                print(f"  {state:5} {cue.key:24} {result.duration:6.2f}s")
    return 1 if failed else 0


def command_status(args: argparse.Namespace) -> int:
    """Report narration-cache readiness without generating any audio."""

    renderer = EdgeTTSRenderer(mode="cache")
    missing = 0
    ready_duration = 0.0
    estimated_missing_duration = 0.0
    for episode in selected_episodes(args.episode):
        print(f"\n[{episode.key}] {episode.title}")
        for cue in episode.cues:
            media_path = renderer.media_path(cue)
            duration = renderer.probe_duration(media_path)
            if duration > 0:
                ready_duration += max(duration, cue.min_duration)
                print(f"  CACHE   {cue.key:24} {duration:6.2f}s")
            else:
                missing += 1
                estimate = renderer.estimate_duration(cue)
                estimated_missing_duration += estimate
                print(f"  MISSING {cue.key:24} ~{estimate:5.2f}s")
    print(
        f"\n[SUMMARY] cached {ready_duration:.2f}s; "
        f"missing {missing} cue(s), estimated {estimated_missing_duration:.2f}s"
    )
    return 1 if args.strict and missing else 0


def render_command(episode_key: str, preset: str, preview: bool) -> int:
    episode = get_episode(episode_key)
    if preset == "preview":
        resolution, fps = "360,640", "24"
    elif preset == "draft":
        resolution, fps = "540,960", "30"
    else:
        resolution, fps = "1080,1920", "60"
    command = [
        sys.executable,
        "-m",
        "manim",
        "-r",
        resolution,
        "--fps",
        fps,
        "--format",
        "mp4",
    ]
    if preview:
        command.append("-p")
    command.extend([episode.scene_file, episode.scene_class])
    print("[RENDER]", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def command_preview(args: argparse.Namespace) -> int:
    return render_command(args.episode, "preview", True)


def command_render(args: argparse.Namespace) -> int:
    return render_command(args.episode, args.preset, False)


def command_clean(args: argparse.Namespace) -> int:
    targets = []
    if args.target in {"media", "all"}:
        targets.extend((ROOT / ".build", ROOT / "media"))
    if args.target in {"narration", "all"}:
        targets.append(ROOT / ".cache" / "narration")
    for target in targets:
        if target.exists():
            shutil.rmtree(target)
            print(f"[REMOVED] {target.relative_to(ROOT)}")
        else:
            print(f"[SKIP] {target.relative_to(ROOT)} does not exist")
    return 0


def _camel_case(key: str) -> str:
    """snake_case -> CamelCase (e.g. cpp_hello_world -> CppHelloWorld)."""
    return "".join(part[:1].upper() + part[1:] for part in key.split("_") if part)


def _slugify(key: str) -> str:
    """Return a safe episode key: lowercase letters, digits, underscore only."""
    slug = re.sub(r"[^a-z0-9_]+", "_", key.lower()).strip("_")
    if not slug:
        raise ValueError("episode key must contain at least one letter/digit")
    return re.sub(r"_+", "_", slug)


def command_scaffold(args: argparse.Namespace) -> int:
    """Generate a fresh episode skeleton: content/, scenes/ + registry entry."""
    key = _slugify(args.episode)
    if key in EPISODES:
        print(f"[ERROR] episode {key!r} already exists")
        return 1
    class_name = _camel_case(key) + "V1"
    scene_name = f"{key}_scene"
    title = args.title or key.replace("_", " ").title()

    content_path = ROOT / "content" / f"{key}.py"
    scene_path = ROOT / "scenes" / f"{scene_name}.py"
    for path in (content_path, scene_path):
        if path.exists():
            print(f"[ERROR] {path.relative_to(ROOT)} already exists")
            return 1

    content_path.write_text(_scaffold_content(key, title), encoding="utf-8")
    scene_path.write_text(_scaffold_scene(key, class_name, scene_name), encoding="utf-8")
    _registry_add(key)
    print(f"[OK] scaffolded episode {key!r} ({title})")
    print(f"  created {content_path.relative_to(ROOT)}")
    print(f"  created {scene_path.relative_to(ROOT)}")
    print(f"  registered in content/registry.py")
    print(f"\nNext steps:")
    print(f"  1. Edit content/{key}.py  — narration + subtitle_beats (<=35 chars)")
    print(f"  2. Edit scenes/{scene_name}.py — visuals per cue")
    print(f"  3. python cli.py validate {key}")
    print(f"  4. python cli.py audio {key}")
    print(f"  5. python cli.py preview {key}")
    return 0


def _content_from_cues(key: str, title: str, tags, cues) -> str:
    """Build a content script from a list of {key, text, subtitle_beats} dicts."""
    # NOTE: title is LLM-controlled, so it must be repr-escaped (like the other
    # fields) before being interpolated into generated Python source; a raw
    # embed could otherwise inject arbitrary code into the file that is imported.
    lines = [
        f'"""บทบรรยายและ cue สำหรับตอน {title!r}."""',
        "",
        "from __future__ import annotations",
        "",
        "from content.models import Episode",
        "from lib.narration import NarrationCue",
        "",
        "",
        "SCRIPT = Episode(",
        f'    key="{key}",',
        f"    title={title!r},",
        f'    scene_file="scenes/{key}_scene.py",',
        f'    scene_class="{_camel_case(key)}V1",',
        f"    tags={tuple(tags)!r},",
        "    cues=(",
    ]
    for cue in cues:
        lines.append("        NarrationCue(")
        lines.append(f'            key="{cue["key"]}",')
        lines.append(f"            text={cue['text']!r},")
        lines.append(f"            subtitle_beats={tuple(cue['subtitle_beats'])!r},")
        lines.append("        ),")
    lines.append("    ),")
    lines.append(")")
    return "\n".join(lines) + "\n"


def _scene_from_cues(key: str, class_name: str, cues) -> str:
    """Build a scene file whose beat count matches each cue's subtitle_beats."""
    sections = {
        "hook": "เปิดเรื่อง",
        "concept": "แนวคิด",
        "example": "ตัวอย่าง",
        "summary": "สรุป",
        "cta": "ติดตาม",
    }
    methods = []
    calls = []
    for cue in cues:
        cue_key = cue["key"]
        label = sections.get(cue_key, cue_key)
        beat_count = max(1, len(cue["subtitle_beats"]))
        beats = []
        for i in range(beat_count):
            caption = f", caption=cue.subtitle_beats[{i}]" if i < len(cue["subtitle_beats"]) else ""
            weight = "0.8" if i == 0 else "1.0"
            anim = "Write(title)" if i == 0 else "FadeIn(panel)"
            beats.append(f"                beat(lambda: {anim}, weight={weight}{caption}),")
        methods.append(f"""    def show_{cue_key}(self) -> None:
        cue = SCRIPT.cue("{cue_key}")
        title = self.make_text("{label}", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="{label}")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
{chr(10).join(beats)}
            ),
            cleanup=group,
        )
""")
        calls.append(f"        self.show_{cue_key}()\n")
    return f'''"""Scene สำหรับตอน {key}."""

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

from content.{key} import SCRIPT
from lib.scene_base import NarratedScene
from lib.timeline import beat


class {class_name}(NarratedScene):
    """อธิบาย {key}"""

    def construct(self) -> None:
        self.build_stage()
{"".join(calls)}
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

{chr(10).join(methods)}
'''


def _normalize_cues(raw_cues) -> list:
    """Normalize LLM cue list to a fixed 5-cue structure that passes validation."""
    wanted = ("hook", "concept", "example", "summary", "cta")
    labels = {"hook": "เปิดเรื่อง", "concept": "แนวคิด", "example": "ตัวอย่าง", "summary": "สรุป", "cta": "ติดตาม"}
    by_key = {}
    for cue in raw_cues or []:
        if isinstance(cue, dict) and cue.get("key"):
            by_key[str(cue["key"])] = cue
    normalized = []
    for key in wanted:
        cue = by_key.get(key, {})
        label = labels[key]
        text = str(cue.get("text", "")).strip().replace("*", "").strip()
        if not text:
            text = f"(ยังไม่ได้เขียนเนื้อหาช่วง{label})"
        if len(text) > 120:
            text = text[:117].rstrip() + "..."
        beats = [str(b).strip() for b in cue.get("subtitle_beats", []) if str(b).strip()]
        beats = [b[:35] if len(b) > 35 else b for b in beats]
        if not beats:
            beats = [f"เริ่มช่วง{label}", f"สรุปช่วง{label}"]
        normalized.append({"key": key, "text": text, "subtitle_beats": beats})
    return normalized


def command_copilot(args: argparse.Namespace) -> int:
    """Generate an episode skeleton from a topic via local Ollama."""
    key = _slugify(args.episode)
    if key in EPISODES:
        print(f"[ERROR] episode {key!r} already exists")
        return 1
    topic = " ".join(args.topic)
    print(f"[COPILOT] generating episode {key!r} for topic: {topic!r}")
    print(f"  model={args.model} host={args.host}")
    try:
        data = generate_episode(
            topic,
            model=args.model,
            host=args.host,
            extra_instruction=args.instruction or "",
        )
    except CopilotError as exc:
        print(f"[ERROR] {exc}")
        return 1

    title = args.title or str(data.get("title") or key.replace("_", " ").title())
    if len(title) > 80:
        title = title[:77].rstrip() + "..."
    tags = [str(t) for t in data.get("tags", [])][:5] or ("#CodingThailand", "#เขียนโปรแกรม")
    cues = _normalize_cues(data.get("cues"))
    class_name = _camel_case(key) + "V1"

    content_path = ROOT / "content" / f"{key}.py"
    scene_path = ROOT / "scenes" / f"{key}_scene.py"
    content_path.write_text(_content_from_cues(key, title, tags, cues), encoding="utf-8")
    scene_path.write_text(_scene_from_cues(key, class_name, cues), encoding="utf-8")
    _registry_add(key)
    print(f"[OK] generated {key!r} ({title}) from LLM")
    print(f"  created {content_path.relative_to(ROOT)}")
    print(f"  created {scene_path.relative_to(ROOT)}")
    print(f"  registered in content/registry.py")

    import importlib
    import content.registry as registry_module
    importlib.reload(registry_module)
    episode = registry_module.EPISODES[key]
    errors = [issue for issue in validate_many((episode,), ROOT) if issue.level == "ERROR"]
    if errors:
        print(f"\n[WARN] generated episode has {len(errors)} validation error(s) to fix:")
        for issue in errors:
            print(f"  [{issue.level}] {issue.message}")
        return 1
    print("\n[OK] generated episode passes validation")
    return 0


def _scaffold_content(key: str, title: str) -> str:
    """Build the narration script for a new episode."""
    return f'''"""บทบรรยายและ cue สำหรับตอน {title}."""

from __future__ import annotations

from content.models import Episode
from lib.narration import NarrationCue


SCRIPT = Episode(
    key="{key}",
    title="{title}",
    scene_file="scenes/{key}_scene.py",
    scene_class="{_camel_case(key)}V1",
    tags=("#CodingThailand", "#เขียนโปรแกรม", "#โปรแกรมมิ่ง"),
    cues=(
        NarrationCue(
            key="hook",
            text="เขียนบทนำที่ดึงดูดความสนใจ",
            subtitle_beats=(
                "บทนำ",
                "ดึงดูดความสนใจ",
            ),
        ),
        NarrationCue(
            key="concept",
            text="อธิบายแนวคิดหลักของบทนี้ให้เข้าใจง่าย",
            subtitle_beats=(
                "แนวคิดหลัก",
                "เข้าใจง่าย",
            ),
        ),
        NarrationCue(
            key="example",
            text="ยกตัวอย่างการใช้งานจริงให้เห็นภาพชัดเจน",
            subtitle_beats=(
                "ตัวอย่างจริง",
                "เห็นภาพชัด",
            ),
        ),
        NarrationCue(
            key="summary",
            text="สรุปประเด็นสำคัญทั้งหมดของบทนี้",
            subtitle_beats=(
                "สรุปสาระ",
                "จดจำง่าย",
            ),
        ),
        NarrationCue(
            key="cta",
            text="ชวนทุกคนติดตามตอนหน้าแล้วเจอกันใหม่",
            subtitle_beats=(
                "ติดตามได้เลย",
                "เจอกันตอนหน้า",
            ),
        ),
    ),
)
'''


def _scaffold_scene(key: str, class_name: str, scene_name: str) -> str:
    """Build the scene file skeleton for a new episode."""
    sections = (
        ("hook", "เปิดเรื่อง"),
        ("concept", "แนวคิด"),
        ("example", "ตัวอย่าง"),
        ("summary", "สรุป"),
        ("cta", "ติดตาม"),
    )
    methods = []
    for cue_key, label in sections:
        methods.append(f'''    def show_{cue_key}(self) -> None:
        cue = SCRIPT.cue("{cue_key}")
        title = self.make_text("{label}", size=46, color=YELLOW, weight="BOLD")
        title.to_edge(UP, buff=2.2)
        panel = self.make_panel(title="{label}")
        panel.next_to(title, DOWN, buff=0.5)
        group = VGroup(title, panel)
        self.play_cue(
            cue,
            (
                beat(lambda: Write(title), weight=0.8, caption=cue.subtitle_beats[0]),
                beat(lambda: AnimationGroup(FadeIn(panel)), weight=1.0, caption=cue.subtitle_beats[1]),
            ),
            cleanup=group,
        )
''')
    calls = "".join(f"        self.show_{cue_key}()\n" for cue_key, _ in sections)
    return f'''"""Scene สำหรับตอน {key}."""

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

from content.{key} import SCRIPT
from lib.scene_base import NarratedScene
from lib.timeline import beat


class {class_name}(NarratedScene):
    """อธิบาย {key}"""

    def construct(self) -> None:
        self.build_stage()
{calls}
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

{chr(10).join(methods)}
'''


def _registry_add(key: str) -> None:
    """Add a new episode import + entry into content/registry.py."""
    path = ROOT / "content" / "registry.py"
    source = path.read_text(encoding="utf-8")
    import_line = f"from content.{key} import SCRIPT as {key}"

    if import_line in source:
        return
    if f"from content.{key} import" in source:
        return

    # Insert import after the last "from content.X import SCRIPT" line.
    lines = source.splitlines(keepends=True)
    last_import = -1
    for idx, line in enumerate(lines):
        if line.startswith("from content.") and "import SCRIPT" in line:
            last_import = idx
    if last_import < 0:
        # No imports yet; place after module docstring.
        lines.insert(2, f"{import_line}\n")
    else:
        lines.insert(last_import + 1, f"{import_line}\n")
    source = "".join(lines)

    # Add entry to the EPISODES tuple before the closing ")".
    marker = "    )\n"
    tuple_start = source.find("for episode in (")
    if tuple_start >= 0:
        close = source.find(marker, tuple_start)
        if close >= 0:
            source = source[:close] + f"        {key},\n" + source[close:]
    path.write_text(source, encoding="utf-8")


def command_preflight(args: argparse.Namespace) -> int:
    """Run validate -> pytest -> audio -> status in one gate command."""
    print("=" * 56)
    print(f"[PREFLIGHT] {args.episode}")
    failed: list[str] = []

    issues = validate_many(selected_episodes(args.episode), ROOT)
    errors = sum(issue.level == "ERROR" for issue in issues)
    for issue in issues:
        print(f"[{issue.level}] {issue.message}")
    print(f"[1/4] validate: {'PASS' if not errors else f'{errors} error(s)'}")
    if errors:
        failed.append("validate")
    else:
        print("[OK] validation passed")

    test_result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=False)
    print(f"[2/4] pytest: {'PASS' if test_result.returncode == 0 else 'FAIL'}")
    if test_result.returncode != 0:
        failed.append("pytest")

    audio = command_audio(argparse.Namespace(episode=args.episode, force=args.force))
    print(f"[3/4] audio: {'PASS' if audio == 0 else 'FAIL'}")
    if audio != 0:
        failed.append("audio")

    status = command_status(argparse.Namespace(episode=args.episode, strict=True))
    print(f"[4/4] status: {'PASS' if status == 0 else 'FAIL'}")
    if status != 0:
        failed.append("status")

    print("=" * 56)
    if failed:
        print(f"[PREFLIGHT] FAILED on: {', '.join(failed)}")
        return 1
    print(f"[PREFLIGHT] READY TO RENDER ✔  ({args.episode})")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Animetion Studio v6")
    sub = result.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(func=command_list)

    validate = sub.add_parser("validate")
    validate.add_argument("episode", choices=("all", *EPISODES.keys()))
    validate.set_defaults(func=command_validate)

    audio = sub.add_parser("audio")
    audio.add_argument("episode", choices=("all", *EPISODES.keys()))
    audio.add_argument("--force", action="store_true")
    audio.set_defaults(func=command_audio)

    status = sub.add_parser("status", help="show local narration-cache readiness")
    status.add_argument("episode", choices=("all", *EPISODES.keys()), default="all", nargs="?")
    status.add_argument("--strict", action="store_true", help="fail when any narration cache is missing")
    status.set_defaults(func=command_status)

    preview = sub.add_parser("preview")
    preview.add_argument("episode", choices=tuple(EPISODES.keys()))
    preview.set_defaults(func=command_preview)

    render = sub.add_parser("render")
    render.add_argument("episode", choices=tuple(EPISODES.keys()))
    render.add_argument("--preset", choices=("draft", "final"), default="final")
    render.set_defaults(func=command_render)

    clean = sub.add_parser("clean")
    clean.add_argument("target", choices=("media", "narration", "all"))
    clean.set_defaults(func=command_clean)

    scaffold = sub.add_parser("scaffold", help="generate a new episode skeleton")
    scaffold.add_argument("episode")
    scaffold.add_argument("--title", default="", help="display title (default: derived from key)")
    scaffold.set_defaults(func=command_scaffold)

    preflight = sub.add_parser("preflight", help="gate: validate + pytest + audio + status in one command")
    preflight.add_argument("episode", choices=("all", *EPISODES.keys()))
    preflight.add_argument("--force", action="store_true", help="regenerate narration audio even if cached")
    preflight.set_defaults(func=command_preflight)

    copilot = sub.add_parser("copilot", help="generate an episode skeleton from a topic via local Ollama")
    copilot.add_argument("episode")
    copilot.add_argument("topic", nargs="+", help="topic or title of the video, e.g. 'ฟังก์ชันในภาษา C'")
    copilot.add_argument("--title", default="", help="override the display title from the LLM")
    copilot.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    copilot.add_argument("--host", default=DEFAULT_HOST, help=f"Ollama host (default: {DEFAULT_HOST})")
    copilot.add_argument("--instruction", default="", help="extra constraint/instruction to append to the prompt")
    copilot.set_defaults(func=command_copilot)
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
