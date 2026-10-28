"""Render prompts/weekly.md with the values from config.json.

python3 -m healthcheck.prompt <run_dir> <run_date> [config.json]  -> prints the prompt
"""
import json
import os
import re
import sys

from .rules import MIN_WEEKS_FOR_RED

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render(template, cfg, run_dir, run_date):
    src = cfg.get("sources", {})
    values = {
        "RUN_DATE": run_date,
        "RUN_DIR": run_dir,
        "WINDOW_WEEKS": cfg.get("window_weeks", 4),
        "ROSTER_FILE": src.get("roster_file", "roster.json"),
        "TRANSCRIPTS_DIR": src.get("transcripts_dir", "transcripts"),
        "NOTES_DIR": src.get("notes_dir", "notes"),
        "INTERNAL_SPEAKERS": ", ".join(cfg.get("internal_speakers", [])) or "(none listed)",
        "NEVER_A_RISK": " ".join(cfg.get("never_a_risk", [])) or "(none listed)",
        "ACCOUNTS_PER_AGENT": cfg.get("accounts_per_agent", 5),
        "READER_MODEL": cfg.get("models", {}).get("account_readers", ""),
        "MIN_WEEKS": MIN_WEEKS_FOR_RED,
    }
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), template)
    return out


if __name__ == "__main__":
    run_dir, run_date = sys.argv[1], sys.argv[2]
    cfg_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "config.json")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    with open(os.path.join(ROOT, "prompts", "weekly.md"), encoding="utf-8") as f:
        print(render(f.read(), cfg, run_dir, run_date))
