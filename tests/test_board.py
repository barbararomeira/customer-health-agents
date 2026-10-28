import json
import os
import shutil

from healthcheck import board
from healthcheck.__main__ import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "config.example.json")

HISTORY = {
    "2026-W10": {"Acme": "green", "Gone": "red"},
    "2026-W11": {"Acme": "yellow", "Gone": "red"},
    "2026-W12": {"Acme": "yellow"},
}


def test_history_keys_sort_across_years():
    h = board.update_history({"2026-W52": {}, "2027-W01": {}}, "2026-W10", [])
    assert list(h) == ["2026-W10", "2026-W52", "2027-W01"]


def test_since_week_finds_the_start_of_the_current_run():
    assert board.since_week(HISTORY, "Acme", "yellow") == "2026-W11"
    assert board.since_week(HISTORY, "Acme", "red") is None


def test_an_account_missing_from_this_run_has_left():
    assert board.left_accounts(HISTORY, "2026-W12") == ["Gone"]


def test_recurring_reasons_need_two_flagged_accounts():
    a = [{"status": "yellow", "why": [{"driver": "tone"}, {"driver": "tone"}]},
         {"status": "red", "why": [{"driver": "tone"}, {"driver": "stuck"}]},
         {"status": "green", "why": [{"driver": "stuck"}]}]
    assert board.recurring_reasons(a) == [("Tone", 2, 2)]


def test_example_run_validates_and_builds(tmp_path):
    """The shipped example is the documentation. If it stops building, the docs are wrong."""
    shutil.copytree(os.path.join(ROOT, "example-run"), tmp_path / "ex")
    run = tmp_path / "ex" / "runs" / "2026-W12"
    assert main([str(run), "--date", "2026-03-16", "--config", CFG]) == 0
    page = (run / "board.html").read_text()
    assert "Acme Foods" in page and "Pilot ends 2026-05-01 · 46 days" in page
    assert page.count('<span class="tag">New</span>') == 2   # Acme yellow→red, Corvel green→yellow
    history = json.loads((tmp_path / "ex" / "runs" / "history.json").read_text())
    assert list(history) == ["2026-W10", "2026-W11", "2026-W12"]


def test_invalid_findings_block_the_board(tmp_path):
    run = tmp_path / "runs" / "2026-W12"
    run.mkdir(parents=True)
    (run / "findings_g1.json").write_text(json.dumps({"accounts": [
        {"account": "Acme", "status": "green", "customer_call_in_window": False, "headline": "h", "why": []}]}))
    assert main([str(run), "--config", CFG]) == 1
    assert not (run / "board.html").exists()
    assert not (tmp_path / "runs" / "history.json").exists()
