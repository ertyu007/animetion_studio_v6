"""Import all Manim modules with a generated API stub."""

from pathlib import Path
import subprocess
import sys


def test_project_imports_with_manim_stub() -> None:
    root = Path(__file__).parents[1]
    script = r'''
import ast
import sys
import types
from pathlib import Path

root = Path.cwd()
names = set()

# Scan only source owned by this project. A local .venv may contain thousands
# of third-party .py files with arbitrary source encodings; those files are not
# part of this import smoke test and must never be parsed here.
source_files = [root / "cli.py"]
for source_dir in ("lib", "content", "scenes"):
    source_files.extend(sorted((root / source_dir).rglob("*.py")))

for path in source_files:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "manim":
            names.update(alias.name for alias in node.names)

class Dummy:
    def __init__(self, *args, **kwargs):
        pass

manim = types.ModuleType("manim")
for name in names:
    setattr(manim, name, Dummy)
manim.BOLD = "BOLD"
manim.NORMAL = "NORMAL"
manim.smooth = lambda value: value
sys.modules["manim"] = manim

for module in (
    "lib.components",
    "lib.motion",
    "lib.scene_base",
):
    __import__(module)
'''
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
