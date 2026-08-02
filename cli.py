"""Command line interface for Animetion Studio v6."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from content.registry import EPISODES, get_episode
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
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
