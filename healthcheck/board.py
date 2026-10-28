"""Render one run's findings as the weekly health board (a single self-contained HTML page).

The board shows only the status and the reason, with its evidence. The scoring rules are not on it:
people act on "red, and here is why", and argue with a score.
"""
import html
import json
import os
from collections import Counter
from datetime import date

from .rules import DRIVERS, STATUS_ORDER

e = html.escape
LABEL = {"red": "Red", "yellow": "Yellow", "green": "Green", "no_signal": "No signal", "churned": "Left"}


def _norm(s):
    return " ".join(s.lower().replace("-", " ").split())


def _roster_row(roster, account):
    for r in roster:
        if _norm(r["account"]) == _norm(account):
            return r
    return {}


def _short(week_key):
    return week_key.split("-")[1]  # "2026-W12" -> "W12"


def update_history(history, week_key, accounts):
    """history = {"YYYY-Www": {account: status}}. Keys sort correctly across years."""
    history = dict(history)
    history[week_key] = {a["account"]: a["status"] for a in accounts}
    return dict(sorted(history.items()))


def since_week(history, account, status):
    """The first week of the current unbroken run of this status, or None."""
    start = None
    for w in reversed(sorted(history)):
        if history[w].get(account) == status:
            start = w
        else:
            break
    return start


def _since_label(history, name, status):
    if status == "churned":
        return "Left"
    start = since_week(history, name, status)
    return _short(start) if start else "—"


def left_accounts(history, week_key):
    """Accounts seen in an earlier week that are not in this run: they left the installed base."""
    seen = {n for w in history if w != week_key for n in history[w]}
    return sorted(seen - set(history.get(week_key, {})))


def recurring_reasons(accounts):
    """Drivers that appear on two or more red/yellow accounts: a pattern, not a one-off."""
    flagged = [a for a in accounts if a["status"] in ("red", "yellow")]
    c = Counter(d for a in flagged for d in {w.get("driver") for w in a.get("why") or []} if d and d != "other")
    return [(DRIVERS[d], k, len(flagged)) for d, k in c.most_common(4) if k >= 2]


def render(accounts, roster, history, week_key, run_date, cfg):
    accounts = sorted(accounts, key=lambda a: (STATUS_ORDER[a["status"]], a["account"].lower()))
    groups = {k: [a for a in accounts if a["status"] == k] for k in STATUS_ORDER}
    counts = {k: len(v) for k, v in groups.items()}
    weeks_sorted = sorted(history)
    prev_week = weeks_sorted[weeks_sorted.index(week_key) - 1] if weeks_sorted.index(week_key) else None
    window = cfg.get("window_weeks", 4)

    def owner(name):
        return _roster_row(roster, name).get("owner") or "—"

    def end_chip(name):
        r = _roster_row(roster, name)
        if not r.get("end_date"):
            return ""
        days = (date.fromisoformat(r["end_date"]) - date.fromisoformat(run_date)).days
        if days < 0:
            return ""
        kind = r.get("end_label") or "Ends"
        return f'<span class="chip">{e(kind)} {e(r["end_date"])} · {days} days</span>'

    def new_tag(a):
        p = history[prev_week].get(a["account"]) if prev_week else None
        return '<span class="tag">New</span>' if p is not None and p != a["status"] else ""

    def links(ev):
        return "".join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener">{e(x.get("label") or "source")}</a>'
                       for x in ev or [] if x.get("url"))

    def sources(a):
        seen, uniq = set(), []
        for x in (x for w in a.get("why") or [] for x in w.get("evidence") or [] if x.get("url")):
            if x["url"] not in seen:
                seen.add(x["url"])
                uniq.append(x)
        if not uniq:
            return ""
        return f'<details><summary>Sources ({len(uniq)})</summary><div class="src">{links(uniq)}</div></details>'

    def red_card(a):
        items = "".join(
            f'<li><span class="drv">{e(DRIVERS.get(w.get("driver"), "Context"))}'
            + (' · relayed' if w.get("relayed") else "") + f'</span><p>{e(w["reason"])}</p>'
            + (f'<blockquote>“{e(w["quote"])}”</blockquote>' if w.get("quote") else "")
            + f'<div class="src">{links(w.get("evidence"))}</div></li>'
            for w in (a.get("why") or [])[:3])
        sup = (f'<p class="sup"><span>Support needed</span>{e(a["support_needed"])}</p>'
               if a.get("support_needed") else "")
        return f'''<article class="red-card">
  <div class="rc-head"><h3>{e(a["account"])}</h3>{new_tag(a)}<span class="muted">Owner {e(owner(a["account"]))}</span>{end_chip(a["account"])}</div>
  <p class="headline">{e(a.get("headline") or "")}</p>
  <ul class="reasons">{items}</ul>{sup}
</article>'''

    def small_card(a, kind):
        head = a.get("headline") or (a.get("why") or [{}])[0].get("reason", "")
        detail = f'<p class="detail">{e(a["detail"])}</p>' if a.get("detail") else ""
        return f'''<article class="card {kind}">
  <div class="c-head"><h4>{e(a["account"])}</h4>{new_tag(a)}<span class="muted">{e(owner(a["account"]))}</span></div>
  <p class="c-line">{e(head)}</p>{detail}{sources(a)}
</article>'''

    red_html = "".join(red_card(a) for a in groups["red"]) or '<p class="muted">No account is red this week.</p>'
    yellow_html = "".join(small_card(a, "y") for a in groups["yellow"]) or '<p class="muted">No yellow accounts.</p>'
    nosig_html = "".join(small_card(a, "n") for a in groups["no_signal"]) or '<p class="muted">Every account had a customer call.</p>'
    green_html = "".join(f'<span class="gchip">{e(a["account"])}</span>' for a in groups["green"]) or '<span class="muted">—</span>'
    pat_html = "".join(f"<li><b>{e(d)}</b><span>{k} of {n}</span></li>" for d, k, n in recurring_reasons(accounts)) \
        or "<li>No reason repeats across accounts.</li>"

    # Trend: last 12 weekly columns; the summary column counts the last 52 runs.
    weeks, year_weeks = weeks_sorted[-12:], weeks_sorted[-52:]

    def year_summary(name):
        c = Counter(history[w].get(name) for w in year_weeks if history[w].get(name))
        parts = [f"{c[k]} {LABEL[k].lower()}" for k in ("red", "yellow", "green", "no_signal") if c[k]]
        return " · ".join(parts) + (" weeks" if parts else "")

    rows = [(a["account"], a["status"]) for a in accounts] + [(n, "churned") for n in left_accounts(history, week_key)]
    trend_rows = "".join(
        f'<tr><th scope="row">{e(name)}</th><td class="muted">{e(owner(name))}</td>'
        + "".join(f'<td><span class="pill {history[w].get(name, "none")}">{e(LABEL.get(history[w].get(name), "—"))}</span></td>' for w in weeks)
        + f'<td class="muted">{e(_since_label(history, name, status))}</td>'
        + f'<td class="muted">{e(year_summary(name))}</td></tr>'
        for name, status in rows)
    trend_head = "".join(f"<th>{e(_short(w))}</th>" for w in weeks)

    rules_version = cfg.get("rules_version", "")
    how = f"""
<div class="how">
  <section class="panel"><h3>What the board answers</h3>
    <p>Which installed accounts would likely churn without an escalation, and why. Every account gets one status each week, and every reason links to the call or note it comes from.</p></section>
  <section class="panel"><h3>The four statuses</h3>
    <dl>
      <dt><span class="pill red">Red</span></dt><dd>Would likely churn without escalation. Kept rare: one explicit churn signal from the customer, or two strong warning signs that have lasted 3 weeks or more.</dd>
      <dt><span class="pill yellow">Yellow</span></dt><dd>Something is off, not at escalation level: one warning sign, a negative trend younger than 3 weeks, or an open ask nobody has answered.</dd>
      <dt><span class="pill green">Green</span></dt><dd>Engaged, tone normal or positive, no serious open complaint. Needs at least one customer call in the window.</dd>
      <dt><span class="pill no_signal">No signal</span></dt><dd>No customer call in the last {window} weeks. Internal notes add context but cannot make an account green, because silence is not health.</dd>
    </dl></section>
  <section class="panel"><h3>What never counts against an account</h3>
    <ul>
      <li>A missing recording with no explanation. It is marked unknown, never a no-show.</li>
      <li>Internal calls. They explain context but are not the customer's voice.</li>
      <li>Deliberate product design the customer agreed to.</li>
    </ul>
    <p class="muted">Reasons are written about the account, never about the account owner.</p></section>
  <section class="panel"><h3>Rules version</h3><p>{e(rules_version)}</p></section>
</div>"""

    css = open(os.path.join(os.path.dirname(__file__), "board.css"), encoding="utf-8").read()
    week = _short(week_key)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Customer Health Board</title>
<style>{css}</style></head>
<body><div class="wrap">
  <header class="top">
    <div><h1>Customer Health · Week {e(week[1:])}</h1>
      <p class="muted">All installed accounts · customer calls and internal notes, last {window} weeks · run {e(run_date)}</p></div>
    <div class="counts" aria-label="Summary">
      <div class="count r"><b>{counts["red"]}</b><span>Red</span></div>
      <div class="count y"><b>{counts["yellow"]}</b><span>Yellow</span></div>
      <div class="count g"><b>{counts["green"]}</b><span>Green</span></div>
      <div class="count n"><b>{counts["no_signal"]}</b><span>No signal</span></div>
    </div>
  </header>
  <nav class="tabs" aria-label="Views">
    <a href="#board" data-view="board">This week</a><a href="#trend" data-view="trend">Weekly trend</a><a href="#how" data-view="how">How it works</a>
  </nav>
  <div class="view" id="view-trend" hidden>
    <section><h2>Status by week</h2>
      <div class="tbl"><table class="trend"><thead><tr><th>Account</th><th>Owner</th>{trend_head}<th>Current status since</th><th>Last 12 months</th></tr></thead>
      <tbody>{trend_rows}</tbody></table></div></section>
  </div>
  <div class="view" id="view-how" hidden>{how}</div>
  <div class="view" id="view-board">
    <section><h2><i style="background:var(--red)"></i>Red · needs escalation</h2>{red_html}</section>
    <section><h2><i style="background:var(--yellow)"></i>Yellow · watch</h2><div class="grid">{yellow_html}</div></section>
    <div class="bottom">
      <section><h2><i style="background:var(--grey)"></i>No signal · no customer call</h2><div class="grid">{nosig_html}</div></section>
      <section><h2><i style="background:var(--green)"></i>Green</h2><div class="panel gchips">{green_html}</div></section>
      <section><h2>Recurring reasons</h2><div class="panel"><ul class="pat">{pat_html}</ul></div></section>
    </div>
  </div>
</div>
<script>
(function () {{
  var views = ["board", "trend", "how"];
  function show() {{
    var v = (location.hash || "#board").slice(1);
    if (views.indexOf(v) < 0) v = "board";
    views.forEach(function (n) {{ document.getElementById("view-" + n).hidden = n !== v; }});
    document.querySelectorAll(".tabs a").forEach(function (a) {{
      if (a.dataset.view === v) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    }});
  }}
  window.addEventListener("hashchange", show);
  show();
}})();
</script>
</body></html>
'''
