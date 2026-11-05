"""The tutorial, replayed: every file and command on tutorial.html, in page order.

Files are <pre data-file="debate/...">: written (or replaced) in a fresh folder.
Commands are <code class="cmd" data-run>: run there, and each must succeed; with
data-expect="text", its output must also contain that text. data-run="skip" marks
a command that costs money or opens a browser: shown on the page, not replayed.
Every run is a rehearsal, so no model is called and no key is needed.

    python tests/test_tutorial.py                 # the tutorial.html beside tests/
    python tests/test_tutorial.py path/to/tutorial.html

It uses whichever `teamrunner` is installed: PyPI's in this repository's CI, the
wheel about to be released in the package's.
"""

from __future__ import annotations

import html.parser
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class Steps(html.parser.HTMLParser):
    """Collects ("file", path, text) and ("run", command, expect) in page order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.steps: list[tuple[str, str, str | None]] = []
        self._open: tuple[str, str, str | None] | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "pre" and "data-file" in a:
            self._open, self._text = ("file", a["data-file"], None), []
        elif tag == "code" and "data-run" in a and a["data-run"] != "skip":
            self._open, self._text = ("run", "", a.get("data-expect")), []

    def handle_data(self, data):
        if self._open:
            self._text.append(data)

    def handle_endtag(self, tag):
        if self._open and tag in ("pre", "code"):
            kind, path, expect = self._open
            text = "".join(self._text)
            self.steps.append((kind, path, text) if kind == "file" else (kind, text.strip(), expect))
            self._open = None


def teamrunner() -> list[str]:
    found = shutil.which("teamrunner")
    return [found] if found else [sys.executable, "-m", "teamrunner"]


def main() -> int:
    # Windows consoles default to a code page with no ✓ or ✗; print UTF-8 everywhere
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    page = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "tutorial.html"
    parser = Steps()
    parser.feed(page.read_text(encoding="utf-8"))
    files = sum(1 for s in parser.steps if s[0] == "file")
    runs = sum(1 for s in parser.steps if s[0] == "run")
    if not files or not runs:
        print(f"{page}: no marked files or commands found")
        return 1

    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp, "home")  # an empty home: no key file, so nothing could call a model
        home.mkdir()
        env.update(HOME=str(home), USERPROFILE=str(home))
        work = Path(tmp, "work")
        work.mkdir()
        version = subprocess.run(teamrunner() + ["--version"], capture_output=True, text=True,
                                 encoding="utf-8", env=env).stdout.strip()
        print(f"{page.name}: {files} files, {runs} commands, with {version}")
        for kind, what, extra in parser.steps:
            if kind == "file":
                target = work / what
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(extra, encoding="utf-8")
                print(f"  wrote {what}")
                continue
            words = shlex.split(what)
            if words[0] != "teamrunner":
                print(f"  ✗ {what}\n    a tutorial command must start with teamrunner")
                return 1
            done = subprocess.run(teamrunner() + words[1:], cwd=work, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=env, stdin=subprocess.DEVNULL)
            said = done.stdout + done.stderr
            if done.returncode != 0 or (extra and extra not in said):
                why = f"exit code {done.returncode}" if done.returncode else f"no “{extra}” in its output"
                print(f"  ✗ {what}  ({why})\n" + "\n".join("    " + line for line in said.splitlines()))
                return 1
            print(f"  ✓ {what}")
    print("The tutorial works as written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
