"""Run ruff check or ruff format on .py.jinja files by handling Jinja syntax."""
import re
import subprocess
import sys
from pathlib import Path


def extract_jinja(content: str) -> tuple[str, list[str]]:
    """Replace Jinja expressions with stable placeholders; return (modified, originals)."""
    originals: list[str] = []

    def replace(m: re.Match) -> str:
        idx = len(originals)
        originals.append(m.group(0))
        return f"__JINJA{idx:04d}__"

    content = re.sub(r"\{\{.*?\}\}", replace, content)   # {{ expr }}
    content = re.sub(r"\{%.*?%\}", replace, content)      # {% tag %}
    content = re.sub(r"\{#.*?#\}", replace, content)      # {# comment #}
    return content, originals


def restore_jinja(content: str, originals: list[str]) -> str:
    for idx, original in enumerate(originals):
        content = content.replace(f"__JINJA{idx:04d}__", original)
    return content


def is_py_jinja(path: Path) -> bool:
    return path.suffix == ".jinja" and path.stem.endswith(".py")


def run_check(path: Path, ruff_cmd: list[str]) -> int:
    cleaned, _ = extract_jinja(path.read_text(encoding="utf-8"))
    result = subprocess.run(
        [*ruff_cmd, "check", "--stdin-filename", str(path), "-"],
        input=cleaned, capture_output=True, text=True, encoding="utf-8",
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def run_format(path: Path, ruff_cmd: list[str]) -> int:
    original = path.read_text(encoding="utf-8")
    cleaned, originals = extract_jinja(original)
    result = subprocess.run(
        [*ruff_cmd, "format", "--stdin-filename", str(path), "-"],
        input=cleaned, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
        return result.returncode
    formatted = restore_jinja(result.stdout, originals)
    if formatted != original:
        path.write_text(formatted, encoding="utf-8")
        print(f"Reformatted {path}")
    return 0


def resolve_files(args: list[str]) -> list[Path]:
    files: list[Path] = []
    for arg in args:
        matched = [p for p in Path(".").glob(arg) if is_py_jinja(p)]
        if matched:
            files.extend(matched)
        else:
            p = Path(arg)
            if is_py_jinja(p):
                files.append(p)
            elif p.exists():
                print(f"Skipping {arg} (not a .py.jinja file)")
    return files


if __name__ == "__main__":
    # Usage:
    #   python ruff_jinja.py "template/**/*.py.jinja"            # check
    #   python ruff_jinja.py --format "template/**/*.py.jinja"   # format (writes files)
    #   python ruff_jinja.py --uvx "template/**/*.py.jinja"      # use `uvx ruff`
    #   python ruff_jinja.py --format --uvx "template/**/*.py.jinja"

    raw_args = sys.argv[1:]
    mode = "format" if "--format" in raw_args else "check"
    use_uvx = "--uvx" in raw_args
    glob_args = [a for a in raw_args if a not in ("--format", "--uvx")]

    if not glob_args:
        print("Usage: python ruff_jinja.py [--format] [--uvx] <file.py.jinja|glob> [...]")
        sys.exit(1)

    ruff_cmd = ["uvx", "ruff"] if use_uvx else ["ruff"]
    files = resolve_files(glob_args)

    if not files:
        print("No .py.jinja files matched.")
        sys.exit(0)

    fn = run_format if mode == "format" else run_check
    exit_code = max(fn(p, ruff_cmd) for p in files)
    sys.exit(exit_code)
