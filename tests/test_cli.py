import importlib
from pathlib import Path

from cli import main

ROOT = Path(__file__).parents[1]


def test_list_command(capsys) -> None:
    assert main(["list"]) == 0


def test_scaffold_creates_valid_episode(tmp_path, monkeypatch) -> None:
    key = "scaffold_test_tmp"
    content_path = ROOT / "content" / f"{key}.py"
    scene_path = ROOT / "scenes" / f"{key}_scene.py"
    registry_path = ROOT / "content" / "registry.py"
    original_registry = registry_path.read_text(encoding="utf-8")

    try:
        assert main(["scaffold", key, "--title", "Scaffold Test"]) == 0
        assert content_path.is_file()
        assert scene_path.is_file()

        importlib.reload(importlib.import_module("content.registry"))
        import cli as cli_module
        importlib.reload(cli_module)
        assert cli_module.main(["validate", key]) == 0
    finally:
        content_path.unlink(missing_ok=True)
        scene_path.unlink(missing_ok=True)
        registry_path.write_text(original_registry, encoding="utf-8")
        importlib.reload(importlib.import_module("content.registry"))
        importlib.reload(importlib.import_module("cli"))


def test_scaffold_rejects_existing_episode(capsys) -> None:
    assert main(["scaffold", "cpp_hello_world"]) == 1


def test_scaffold_slugifies_and_rejects_duplicate(capsys) -> None:
    assert main(["scaffold", "cpp-hello-world"]) == 1


def test_preflight_fails_when_validate_fails(monkeypatch) -> None:
    from types import SimpleNamespace

    import cli as cli_module
    from lib.validation import Issue

    monkeypatch.setattr(cli_module, "validate_many", lambda episodes, root: (Issue("ERROR", "boom"),))
    monkeypatch.setattr(cli_module, "command_audio", lambda args: 0)
    monkeypatch.setattr(cli_module, "command_status", lambda args: 0)
    monkeypatch.setattr(cli_module.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    assert cli_module.main(["preflight", "cpp_hello_world"]) == 1
