"""python3 -m healthcheck <run_dir> [--date YYYY-MM-DD] [--config config.json]

Reads   <run_dir>/findings_*.json   one file per agent group, {"accounts": [...]}
        <run_dir>/roster.json       every installed account: owner, nearest end date
        <run_dir>/overrides.json    optional: a reviewer's status changes, applied before validation
Writes  <run_dir>/board.html, <run_dir>/status.json, and <run_dir>/../history.json

Validation runs first and blocks the build: a board is never rendered from findings that break
the rules.
"""
import argparse
import glob
import json
import os
import sys
from datetime import date

from . import board
from .validate import validate


def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    p = argparse.ArgumentParser(prog="healthcheck")
    p.add_argument("run_dir", help="e.g. output/runs/2026-W12 (the folder name is the ISO week)")
    p.add_argument("--date", default=date.today().isoformat(), help="run date, for days-to-end")
    p.add_argument("--config", default="config.json")
    args = p.parse_args(argv)

    run_dir = os.path.abspath(args.run_dir)
    week_key = os.path.basename(run_dir)
    cfg = _load(args.config, None) or _load("config.example.json", {})

    accounts = []
    for f in sorted(glob.glob(os.path.join(run_dir, "findings_*.json"))):
        d = _load(f, {})
        accounts += d["accounts"] if isinstance(d, dict) else d
    if not accounts:
        print(f"No findings in {run_dir}", file=sys.stderr)
        return 2
    roster = _load(os.path.join(run_dir, "roster.json"), [])
    overrides = _load(os.path.join(run_dir, "overrides.json"), {})
    for a in accounts:
        a.update(overrides.get(a["account"], {}))

    errors, warnings = validate(accounts, roster, base_dir=run_dir)
    for w in warnings:
        print("warning:", w)
    if errors:
        for x in errors:
            print("ERROR:", x, file=sys.stderr)
        print(f"{len(errors)} error(s): board not built.", file=sys.stderr)
        return 1

    hist_path = os.path.join(os.path.dirname(run_dir), "history.json")
    history = board.update_history(_load(hist_path, {}), week_key, accounts)
    page = board.render(accounts, roster, history, week_key, args.date, cfg)

    with open(os.path.join(run_dir, "board.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(run_dir, "status.json"), "w", encoding="utf-8") as f:
        json.dump({a["account"]: a["status"] for a in accounts}, f, indent=1)
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=1, ensure_ascii=False)

    counts = {s: sum(a["status"] == s for a in accounts) for s in ("red", "yellow", "green", "no_signal")}
    print(counts, "->", os.path.join(run_dir, "board.html"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
