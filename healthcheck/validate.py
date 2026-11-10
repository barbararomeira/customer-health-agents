"""Check the agents' findings before anything is built from them.

Deciding a status is a judgement and cannot be unit-tested. Its output can be: every status the
board shows must be one the rules allow, given the reasons the agent itself wrote down. A findings
file that fails here is not rendered.

Errors block the build. Warnings are printed and do not.
"""
import os
import re
from datetime import date

from .rules import (CHURN_SIGNAL_POINTS, DRIVERS, LASTING_WARNING_POINTS, MIN_WEEKS_FOR_RED, ORANGE_WITHIN_DAYS,
                    RED_AT_POINTS, STATUSES, STRONG_DRIVERS)

HEADLINE_WORDS = 15


def _norm(text):
    """Compare quotes on words, not on typography or line wrapping."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(re.sub(r"[^\w' ]+", " ", text.lower()).split())


def _local_source(url, base_dir):
    """Evidence that points at a file in the run folder (e.g. transcripts/x.md#L12), or None."""
    if not url or "://" in url:
        return None
    path = os.path.normpath(os.path.join(base_dir, url.split("#", 1)[0]))
    return path if os.path.isfile(path) else None


def days_to_end(roster_row, run_date):
    """Days from the run date to the account's nearest end date (negative = passed), or None."""
    if not roster_row or not roster_row.get("end_date") or not run_date:
        return None
    return (date.fromisoformat(roster_row["end_date"]) - date.fromisoformat(run_date)).days


def red_points(why):
    """The implied weights behind red: churn signal or confirmed exit 2, each different lasting warning sign 1.

    Relayed statements (a colleague passing on what the customer said) can support red but never
    make it alone, so they score nothing. The exception is a hard fact about leaving (our equipment
    is being removed): it counts in full wherever it was written down.
    """
    direct = [w for w in why if not w.get("relayed")]
    churn = CHURN_SIGNAL_POINTS if (any(w.get("driver") == "churn_signal" for w in direct)
                                    or any(w.get("driver") == "leaving" for w in why)) else 0
    lasting = {w["driver"] for w in direct
               if w.get("driver") in STRONG_DRIVERS and (w.get("weeks_present") or 0) >= MIN_WEEKS_FOR_RED}
    return churn + LASTING_WARNING_POINTS * len(lasting)


def validate_account(a, base_dir=".", roster_row=None, run_date=None):
    errors, warnings = [], []
    name = a.get("account") or "<no name>"
    status = a.get("status")
    why = a.get("why") or []

    def err(msg):
        errors.append(f"{name}: {msg}")

    if status not in STATUSES:
        err(f"unknown status {status!r}")
        return errors, warnings

    for i, w in enumerate(why, 1):
        if w.get("driver") not in DRIVERS:
            err(f"reason {i} has unknown driver {w.get('driver')!r}")
        if not any(x.get("url") for x in w.get("evidence") or []):
            err(f"reason {i} has no evidence link (no evidence, no reason)")
        # A quote comes from one call; the other links on the reason are supporting evidence. So the
        # quote must appear verbatim in at least one cited file. Remote links cannot be checked here.
        quote = w.get("quote")
        local = [s for s in (_local_source(x.get("url"), base_dir) for x in w.get("evidence") or []) if s]
        if quote and local and not any(_norm(quote) in _norm(open(s, encoding="utf-8").read()) for s in local):
            err(f"reason {i} quote is not verbatim in any cited transcript")

    # Silence is not health: without a customer call in the window an account can't be green.
    if not a.get("customer_call_in_window") and status == "green":
        err("green without a customer call in the window: silence is not health, so it is yellow at most")

    if status in ("red", "orange", "yellow") and not why and a.get("customer_call_in_window"):
        err(f"{status} with no reason")

    if status == "orange":
        d = days_to_end(roster_row, run_date)
        if d is None or d > ORANGE_WITHIN_DAYS:
            err(f"orange needs an end date within {ORANGE_WITHIN_DAYS} days (or passed); "
                f"{'none in the roster' if d is None else f'{d} days away'}")

    if status == "red":
        if red_points(why) < RED_AT_POINTS:
            err(f"red without an explicit churn signal or two strong signals lasting {MIN_WEEKS_FOR_RED}+ weeks "
                f"({red_points(why)} of {RED_AT_POINTS} points)")
        if not any(w.get("quote") for w in why if not w.get("relayed") or w.get("driver") == "leaving"):
            err("red without a verbatim customer quote (or the written exit fact)")

    if not a.get("headline"):
        err("no headline")
    elif a.get("headline") and len(a["headline"].split()) > HEADLINE_WORDS:
        warnings.append(f"{name}: headline is {len(a['headline'].split())} words (aim for {HEADLINE_WORDS} or fewer)")

    return errors, warnings


def validate(accounts, roster=None, base_dir=".", run_date=None):
    errors, warnings = [], []
    seen = set()
    for a in accounts:
        if a.get("account") in seen:
            errors.append(f"{a.get('account')}: appears twice in the findings")
        seen.add(a.get("account"))
        row = next((r for r in roster or [] if r["account"] == a.get("account")), None)
        e, w = validate_account(a, base_dir, row, run_date)
        errors += e
        warnings += w
    for r in roster or []:
        if r["account"] not in seen:
            errors.append(f"{r['account']}: in the roster but has no finding (every installed account gets a status)")
    return errors, warnings
