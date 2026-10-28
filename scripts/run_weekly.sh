#!/bin/zsh
# Weekly customer health run. Renders prompts/weekly.md from config.json, runs Claude Code headless,
# then validates the findings and builds the board. Schedule it for Sunday night or Monday morning,
# so the window ends on a finished week.
#
# The board is a local HTML file. Publishing it (to a wiki, an internal site, a shared drive) is a
# separate step on purpose: a person looks at any new red before anyone else sees it.

export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT" || exit 1
CONFIG="${1:-config.json}"
[ -f "$CONFIG" ] || { echo "No $CONFIG. Copy config.example.json to config.json first."; exit 1; }

RUN_DATE="$(date +%F)"
WEEK="$(date +%G-W%V)"
OUT_DIR="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("output_dir","output"))' "$CONFIG")"
RUN_DIR="$OUT_DIR/runs/$WEEK"
mkdir -p "$RUN_DIR"
LOG="$OUT_DIR/run-$RUN_DATE.log"

# Single-run lock: a hand-started run and a scheduled run must not write the same week's findings.
# mkdir is atomic; the PID tells a live run from a crashed one.
LOCK="$OUT_DIR/.run_weekly.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  OTHER=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$OTHER" ] && kill -0 "$OTHER" 2>/dev/null; then
    echo "$(date '+%F %T') ABORT: run already in progress (pid $OTHER)." | tee -a "$LOG"
    exit 0
  fi
  echo "$(date '+%F %T') NOTE: stale lock from pid ${OTHER:-unknown} reclaimed." | tee -a "$LOG"
fi
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT INT TERM

MODEL="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["models"]["coordinator"])' "$CONFIG")"
PROMPT="$(python3 -m healthcheck.prompt "$RUN_DIR" "$RUN_DATE" "$CONFIG")"

echo "$(date '+%F %T') start $WEEK" >> "$LOG"
claude -p "$PROMPT" --model "$MODEL" >> "$LOG" 2>&1

# The agent runs the validator itself; run it again here so a green exit code means a valid board,
# whatever the agent reported.
if python3 -m healthcheck "$RUN_DIR" --date "$RUN_DATE" --config "$CONFIG" >> "$LOG" 2>&1; then
  echo "$(date '+%F %T') OK board: $RUN_DIR/board.html" | tee -a "$LOG"
else
  echo "$(date '+%F %T') FAILED: findings did not validate, no board. See $LOG" | tee -a "$LOG"
  exit 1
fi
