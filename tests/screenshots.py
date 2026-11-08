"""Retake the tutorial's and homepage's screenshots of `teamrunner ui` (D137 (5)).

Builds a workspace the way the tutorial does, with free rehearsals only (no key, no
model), opens it in `teamrunner ui`, and saves four PNGs in img/:

    ui-home.png          the hello team open in the editor
    ui-conversation.png  a rehearsal's conversation (step 1)
    ui-compare.png       two runs compared, one member changed (step 3)
    ui-flow.png          the flow diagram of chair.md (step 4)

Uses the installed `teamrunner` and Google Chrome through Playwright:

    uv run --with playwright python tests/screenshots.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SITE = Path(__file__).resolve().parents[1]
IMG = SITE / "img"


def teamrunner() -> list[str]:
    found = shutil.which("teamrunner")
    return [found] if found else [sys.executable, "-m", "teamrunner"]


def tr(work: Path, env: dict, *args: str) -> None:
    subprocess.run(teamrunner() + list(args), cwd=work, env=env, check=True,
                   capture_output=True, stdin=subprocess.DEVNULL)


def main() -> int:
    IMG.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp, "home"); home.mkdir()
        work = Path(tmp, "teams"); work.mkdir()
        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home), "NO_COLOR": "1",
               "BROWSER": "true"}  # the server must not open the user's own browser
        tr(work, env, "new", "hello", "--from", "round_robin")
        topic = "Four-day weeks make teams more productive"
        tr(work, env, "run", "hello", "--rehearse", "--message", topic)
        against = work / "hello" / "02_against.md"
        text = against.read_text(encoding="utf-8")
        old = ("You speak once, after your opponent. Rebut their main point, then make\n"
               "your strongest case against the topic, in one paragraph.")
        new = ("You speak once, after your opponent. Attack their weakest claim\n"
               "directly and without hedging: name it, say why it fails, and give\n"
               "the strongest counter-evidence you know. Then make your case against\n"
               "the topic, in one forceful paragraph.")
        assert old in text, "02_against.md no longer has the lines the tutorial changes"
        time.sleep(1.1)  # a run folder is named to the second
        against.write_text(text.replace(old, new), encoding="utf-8")
        tr(work, env, "run", "hello", "--rehearse", "--message", topic)
        (work / "hello" / "chair.md").write_text(
            "# Three rounds of for and against, then the judge decides.\n\n"
            "rounds(*3) -> judge\n\nrounds = for -> against\n", encoding="utf-8")

        server = subprocess.Popen(teamrunner() + ["ui", "."], cwd=work, env=env, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            url = None
            for line in server.stdout:
                m = re.search(r"https?://127\.0\.0\.1:\d+/\S*", line)
                if m:
                    url = m.group(0); break
            if not url:
                print("teamrunner ui printed no address"); return 1
            shoot(url)
        finally:
            server.terminate(); server.wait(timeout=10)
    print("saved", ", ".join(sorted(p.name for p in IMG.glob("ui-*.png"))))
    return 0


def shoot(url: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1240, "height": 780}, device_scale_factor=2,
                                color_scheme="light")
        page.goto(url)
        page.locator("#folder-path").wait_for(state="attached")
        # show the workspace as ~/teams, not the temporary folder it really is
        tidy = """() => { for (const id of ['folder-path', 'command', 'runs-command']) {
            const e = document.getElementById(id);
            e.textContent = e.textContent.replace(/(\\/private)?\\/(var|tmp)\\/\\S*?\\/teams/g, '~/teams'); } }"""
        tree = page.locator("#files")
        tree.get_by_role("button", name=re.compile(r"^▸?\s*hello")).first.click()
        tree.get_by_role("button", name=re.compile("02_against")).click()
        page.locator(".CodeMirror").wait_for()
        page.wait_for_timeout(400)
        page.evaluate(tidy)
        page.screenshot(path=IMG / "ui-home.png")

        tree.get_by_role("button", name=re.compile("chair")).click()
        page.get_by_role("button", name="Flow diagram").click()
        page.locator("#flow-diagram svg").wait_for()
        page.wait_for_timeout(600)
        page.evaluate(tidy)
        page.screenshot(path=IMG / "ui-flow.png")

        page.locator("#runs-view").click()
        rows = page.locator("#runs-rows tr")
        rows.first.wait_for()
        rows.nth(1).locator("button").first.click()  # the older run: the first rehearsal
        page.locator("#run-conversation > *").first.wait_for()
        page.wait_for_timeout(400)
        page.evaluate(tidy)
        page.screenshot(path=IMG / "ui-conversation.png")

        page.locator("#back-runs").click()
        rows.first.wait_for()
        for i in (1, 0):  # older run on the left
            rows.nth(i).locator("input[type=checkbox]").check()
        page.locator("#compare-runs").click()
        page.locator("#run-comparison .source-diff").first.wait_for()
        page.wait_for_timeout(600)
        page.evaluate("""() => { const h = [...document.querySelectorAll('#run-comparison h3')]
            .find(e => e.textContent === 'Member versions'); h.scrollIntoView({block: 'start'});
            window.scrollBy(0, -24); }""")
        page.wait_for_timeout(200)
        page.evaluate(tidy)
        page.screenshot(path=IMG / "ui-compare.png")
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
