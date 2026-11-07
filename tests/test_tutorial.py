"""The tutorial, replayed: every file and command on tutorial.html, in page order.

Files are <pre data-file="hello/...">: written (or replaced) in a fresh folder.
Edits are <div class="diff" data-edit="hello/...">, shown as a diff: its "-" and
context lines must be in the file as one block, and become its "+" and context
lines, everywhere they appear. A diff touches only the lines it shows, so it
works on an example whichever version of TeamRunner copied it.
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
    """Collects ("file", path, text), ("edit", path, (old, new)) and ("run", command, expect)
    in page order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.steps: list[tuple] = []
        self._open: tuple[str, str, str | None] | None = None
        self._text: list[str] = []
        self._edit: dict | None = None  # inside <div data-edit>: its path, lines, and the line open now

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._edit is not None:
            if tag == "div":
                self._edit["line"] = [(a.get("class") or "x").split()[0], []]
            return
        if tag == "div" and "data-edit" in a:
            self._edit = {"path": a["data-edit"], "lines": [], "line": None}
        elif tag == "pre" and "data-file" in a:
            self._open, self._text = ("file", a["data-file"], None), []
        elif tag == "code" and "data-run" in a and a["data-run"] != "skip":
            self._open, self._text = ("run", "", a.get("data-expect")), []

    def handle_data(self, data):
        if self._edit is not None and self._edit["line"] is not None:
            self._edit["line"][1].append(data)
        elif self._open:
            self._text.append(data)

    def handle_endtag(self, tag):
        if self._edit is not None and tag == "div":
            e = self._edit
            if e["line"] is not None:  # a line of the diff ends
                kind, text = e["line"]
                e["lines"].append((kind, "".join(text)[2:]))  # drop the "- ", "+ " or "  " in front
                e["line"] = None
            else:  # the diff ends
                old = "\n".join(t for k, t in e["lines"] if k != "p")
                new = "\n".join(t for k, t in e["lines"] if k != "m")
                self.steps.append(("edit", e["path"], (old, new)))
                self._edit = None
            return
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
    files = sum(1 for s in parser.steps if s[0] in ("file", "edit"))
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
        print(f"{page.name}: {files} files and edits, {runs} commands, with {version}")
        for kind, what, extra in parser.steps:
            if kind == "file":
                target = work / what
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(extra, encoding="utf-8")
                print(f"  wrote {what}")
                continue
            if kind == "edit":
                target, (old, new) = work / what, extra
                text = target.read_text(encoding="utf-8") if target.exists() else ""
                if old not in text:
                    print(f"  ✗ edit {what}\n    these lines are not in it:\n"
                          + "\n".join("      " + line for line in old.splitlines()))
                    return 1
                target.write_text(text.replace(old, new), encoding="utf-8")
                print(f"  edited {what}" + (f" ({text.count(old)} places)" if text.count(old) > 1 else ""))
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
