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


def _tags(status, why=(), call=True, row=None, **extra):
    a = {"account": "Acme", "status": status, "why": [{"driver": d} for d in why], "customer_call_in_window": call}
    a.update(extra)
    return board.why_tags(a, row, "2026-03-16")


def test_one_tag_per_topic_first_driver_wins():
    t = _tags("yellow", why=["stuck", "unmet_ask"])
    assert t["neg"] == {"Improvements": "not delivering"}


def test_tags_only_use_the_six_topics():
    from healthcheck.rules import TOPICS
    t = _tags("yellow", why=["leaving", "tone", "trust_broken", "golive_late", "usage_collapse"],
              row={"end_date": "2026-04-01", "end_label": "Renewal"})
    assert set(t["neg"]) <= set(TOPICS) and len(t["neg"]) == 6 - 1 + 1   # every topic once (Leaving..Improvements)


def test_red_shows_only_against_and_green_only_in_favour():
    assert _tags("red", why=["churn_signal"], tone="better")["pos"] == {}
    assert _tags("green", why=["unmet_ask"], tone="same")["neg"] == {}
    assert _tags("green", tone="same")["pos"] == {"Tone": "as usual"}


def test_no_call_is_a_tone_tag_and_report_first_accounts_are_never_tagged_for_not_logging_in():
    t = _tags("yellow", call=False, usage={"use": "none", "meant_to_use": False})
    assert t["neg"] == {"Tone": "no customer call in 4 weeks"}
    t = _tags("yellow", usage={"use": "none", "meant_to_use": True})
    assert t["neg"] == {"Product use": "not logging in"}


def test_contract_tag_only_within_90_days_or_passed():
    assert _tags("yellow", row={"end_date": "2026-12-31"})["neg"] == {}
    assert _tags("yellow", row={"end_date": "2026-05-01", "end_label": "Pilot ends"})["neg"] == {"Contract": "pilot ends in 46 days"}
    assert _tags("yellow", row={"end_date": "2026-03-01"})["neg"] == {"Contract": "end passed (2026-03-01)"}


def test_example_run_validates_and_builds(tmp_path):
    """The shipped example is the documentation. If it stops building, the docs are wrong."""
    shutil.copytree(os.path.join(ROOT, "example-run"), tmp_path / "ex")
    run = tmp_path / "ex" / "runs" / "2026-W12"
    assert main([str(run), "--date", "2026-03-16", "--config", CFG]) == 0
    page = (run / "board.html").read_text()
    assert "Acme Foods" in page and "<b>Contract:</b> pilot ends in 46 days" in page
    assert page.count('<span class="tag">New</span>') == 3   # Acme yellow→red, Corvel green→yellow, Vertex yellow→orange
    assert "No signal" not in page and "Recurring reasons" not in page   # v0.6: four colours and why, nothing else
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
