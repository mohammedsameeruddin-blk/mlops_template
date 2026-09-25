"""Run ruff on .py.jinja files by stripping Jinja syntax before checking."""
import re
import subprocess
import sys
from pathlib import Path


def strip_jinja(content: str) -> str:
    # {{ expr | filter }} → bare identifier (makes `from {{ project }}.x` valid Python)
    content = re.sub(
        r"\{\{-?\s*([\w. |]+?)\s*-?\}\}",
        lambda m: m.group(1).strip().split("|")[0].strip().replace(".", "_").replace(" ", "_"),
        content,
    )
    # {# comment #} → remove
    content = re.sub(r"\{#.*?#\}", "", content)
    return content


def check(filepath: str) -> int:
    path = Path(filepath)
    if not path.suffix == ".jinja" or not path.stem.endswith(".py"):
        print(f"Skipping {filepath} (not a .py.jinja file)")
        return 0
    cleaned = strip_jinja(path.read_text(encoding="utf-8"))
    result = subprocess.run(
        ["ruff", "check", "--stdin-filename", str(path), "-"],
        input=cleaned,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ruff_jinja.py <file.py.jinja|glob> [...]")
        sys.exit(1)
    files = []
    for arg in sys.argv[1:]:
        matched = list(Path(".").glob(arg))
        if matched:
            files.extend(str(p) for p in matched)
        else:
            files.append(arg)  # treat as literal path
    if not files:
        print("No files matched.")
        sys.exit(0)
    exit_code = max(check(f) for f in files)
    sys.exit(exit_code)
