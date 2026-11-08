"""Pack real TeamRunner runs for the homepage's "Watch a real run" replay.

Each run folder's own record (run.json and events.jsonl) is copied unchanged to
runs/<version>-<n>/, so a reader can check the replay against it, and the turns the
page needs are gathered into runs/debate.json. Nothing is written by hand: every word,
verdict, model, time and cost comes from the run's events.

    python tests/pack_runs.py plain=path/to/run_folder ... checked=path/to/run_folder ...
"""
import json
import pathlib
import shutil
import sys

site = pathlib.Path(__file__).resolve().parent.parent
out = site / "runs"
out.mkdir(exist_ok=True)

runs, count = [], {}
for arg in sys.argv[1:]:
    version, _, folder = arg.partition("=")
    folder = pathlib.Path(folder)
    count[version] = count.get(version, 0) + 1
    name = f"{version}-{count[version]}"
    dest = out / name
    dest.mkdir(exist_ok=True)
    for f in ("run.json", "events.jsonl"):
        shutil.copyfile(folder / f, dest / f)

    run = json.loads((folder / "run.json").read_text())
    events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines() if line.strip()]
    assert run["status"] == "completed", f"{folder}: {run['status']}"
    turns = []
    for e in events:
        if e.get("event") != "agent_message":
            continue
        rounds = next((b for b in e.get("blocks") or [] if b["block"] == "rounds"), None)
        turns.append({
            "from": e["from"],
            "round": rounds and rounds["number"],
            "attempt": (e.get("attempt") or {}).get("number") or 1,
            "content": e.get("content") or "",
            "output": e.get("output"),
            "model": e.get("model_resolved"),
            "ms": e.get("latency_ms"),
            "cost": e.get("cost_usd"),
        })
    models = sorted(run["prices"]["models"])
    runs.append({
        "name": name,
        "version": version,
        "started": run["started_at"],
        "model": models[0] if len(models) == 1 else ", ".join(models),
        "topic": run["inputs"]["topic"]["value"],
        "turns": turns,
        "ms": run["latency_ms"],
        "cost": run["cost_usd"],
        "tokens": run["tokens"],
        "teamrunner": run["teamrunner_version"],
        "winner": next((t["output"]["winner"] for t in reversed(turns)
                        if t["from"] == "judge" and t["output"]), None),
    })

(out / "debate.json").write_text(json.dumps({"runs": runs}, ensure_ascii=False, indent=1))
for r in runs:
    print(f"{r['name']:10} {r['winner']:8} {len(r['turns']):3} turns  ${r['cost']:.4f}  {r['ms']/1000:.0f}s")
print(f"wrote {out / 'debate.json'}")
