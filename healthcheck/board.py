"""Render one run's findings as the weekly health board (a single self-contained HTML page).

The board shows only the colour and why, with its evidence. Every card carries at most one tag per
topic (Leaving, Contract, Tone, Product use, Go-live, Improvements). The scoring rules are not on it:
people act on "red, and here is why", and argue with a score.
"""
import html
import json
import os
from collections import Counter
from datetime import date

from .rules import DRIVER_TAG, DRIVERS, ORANGE_WITHIN_DAYS, STATUS_ORDER, TOPICS

e = html.escape
LABEL = {"red": "Red", "orange": "Orange", "yellow": "Yellow", "green": "Green", "no_signal": "Yellow", "churned": "Left"}


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


def why_tags(a, roster_row, run_date, window=4):
    """The reasons for the colour as topic tags: {"neg": {topic: text}, "pos": {topic: text}}.

    At most one tag per topic. Red cards show only what counts against; green cards only what counts
    in favour. Optional finding fields: "tone" (worse / same / better), "usage" ({"use": daily |
    regular | low | none, "collapse", "halved", "meant_to_use"}), "golive" ({"late": "week 7" |
    "partial since 15 Jul", "on_time": bool}).
    """
    neg, pos = {}, {}
    for w in a.get("why") or []:
        t = DRIVER_TAG.get(w.get("driver"))
        if t:
            neg.setdefault(*t)
    g = a.get("golive") or {}
    if g.get("late"):
        neg["Go-live"] = g["late"] if "Go-live" not in neg or neg["Go-live"] == "late" else neg["Go-live"]
    elif g.get("on_time"):
        pos["Go-live"] = "on time"
    if roster_row and roster_row.get("end_date") and run_date:
        days = (date.fromisoformat(roster_row["end_date"]) - date.fromisoformat(run_date)).days
        label = (roster_row.get("end_label") or "Ends").lower()
        if days < 0:
            neg.setdefault("Contract", f"end passed ({roster_row['end_date']})")
        elif days <= ORANGE_WITHIN_DAYS:
            neg.setdefault("Contract", f"{label} in {days} days")
    tone = a.get("tone")
    if tone == "worse":
        neg.setdefault("Tone", "worse than usual")
    elif not a.get("customer_call_in_window"):
        neg.setdefault("Tone", f"no customer call in {window} weeks")
    elif tone == "better":
        pos["Tone"] = "warmer than usual"
    elif tone == "same":
        pos["Tone"] = "as usual"
    u = a.get("usage") or {}
    if u.get("collapse"):
        neg.setdefault("Product use", "stopped")
    elif u.get("use") == "daily":
        pos["Product use"] = "daily"
    elif u.get("use") == "regular":
        pos["Product use"] = "regular"
    elif u.get("meant_to_use") and u.get("use") in ("low", "none"):
        neg["Product use"] = "not logging in" if u["use"] == "none" else "rarely logs in"
    if u.get("halved") and not u.get("collapse"):
        neg.setdefault("Product use", "halved")
    pos = {k: v for k, v in pos.items() if k not in neg}
    if a["status"] == "red":
        pos = {}
    if a["status"] == "green":
        neg = {}
    return {"neg": neg, "pos": pos}


def _tags_html(tags):
    out = [f'<span class="why neg"><b>{e(k)}:</b> {e(tags["neg"][k])}</span>' for k in TOPICS if k in tags["neg"]]
    out += [f'<span class="why pos"><b>{e(k)}:</b> {e(tags["pos"][k])}</span>' for k in TOPICS if k in tags["pos"]]
    return f'<div class="whys">{"".join(out)}</div>' if out else ""


def render(accounts, roster, history, week_key, run_date, cfg):
    accounts = sorted(accounts, key=lambda a: (STATUS_ORDER[a["status"]], a["account"].lower()))
    groups = {k: [a for a in accounts if a["status"] == k] for k in STATUS_ORDER}
    counts = {k: len(v) for k, v in groups.items()}
    weeks_sorted = sorted(history)
    prev_week = weeks_sorted[weeks_sorted.index(week_key) - 1] if weeks_sorted.index(week_key) else None
    window = cfg.get("window_weeks", 4)

    def owner(name):
        return _roster_row(roster, name).get("owner") or "—"

    def tags(a):
        return _tags_html(why_tags(a, _roster_row(roster, a["account"]), run_date, window))

    def new_tag(a):
        p = history[prev_week].get(a["account"]) if prev_week else None
        p = "yellow" if p == "no_signal" else p          # the old fifth status is drawn as yellow
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
  <div class="rc-head"><h3>{e(a["account"])}</h3>{new_tag(a)}<span class="muted">Owner {e(owner(a["account"]))}</span></div>
  {tags(a)}
  <p class="headline">{e(a.get("headline") or "")}</p>
  <ul class="reasons">{items}</ul>{sup}
</article>'''

    def small_card(a, kind):
        head = a.get("headline") or (a.get("why") or [{}])[0].get("reason", "")
        detail = f'<p class="detail">{e(a["detail"])}</p>' if a.get("detail") else ""
        return f'''<article class="card {kind}">
  <div class="c-head"><h4>{e(a["account"])}</h4>{new_tag(a)}<span class="muted">{e(owner(a["account"]))}</span></div>
  {tags(a)}<p class="c-line">{e(head)}</p>{detail}{sources(a)}
</article>'''

    red_html = "".join(red_card(a) for a in groups["red"]) or '<p class="muted">No account is red this week.</p>'
    orange_html = "".join(small_card(a, "o") for a in groups["orange"]) or '<p class="muted">No orange accounts.</p>'
    yellow_html = "".join(small_card(a, "y") for a in groups["yellow"]) or '<p class="muted">No yellow accounts.</p>'
    green_html = "".join(small_card(a, "g") for a in groups["green"]) or '<p class="muted">No green accounts.</p>'

    # Trend: last 12 weekly columns; the summary column counts the last 52 runs.
    weeks, year_weeks = weeks_sorted[-12:], weeks_sorted[-52:]

    def year_summary(name):
        c = Counter({"no_signal": "yellow"}.get(s, s) for s in (history[w].get(name) for w in year_weeks) if s)
        parts = [f"{c[k]} {LABEL[k].lower()}" for k in ("red", "orange", "yellow", "green") if c[k]]
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
    <p>Which installed accounts would likely churn without an escalation, and why. Every account gets one colour each week, and every reason links to the call, note or message it comes from.</p></section>
  <section class="panel"><h3>The four colours</h3>
    <dl>
      <dt><span class="pill red">Red</span></dt><dd>Would likely churn without escalation. Kept rare: one explicit churn signal, a confirmed exit (our equipment is being removed), or two warning signs that have each lasted 3 weeks or more.</dd>
      <dt><span class="pill orange">Orange</span></dt><dd>Something is wrong <b>and</b> the contract, pilot or renewal ends within {ORANGE_WITHIN_DAYS} days (or already passed).</dd>
      <dt><span class="pill yellow">Yellow</span></dt><dd>Something is off, with no near deadline: one warning sign, a trend younger than 3 weeks, an open ask, a late go-live, or no customer call in {window} weeks.</dd>
      <dt><span class="pill green">Green</span></dt><dd>Engaged, tone normal or positive, no serious open complaint. Needs at least one customer call in the window: silence is not health.</dd>
    </dl></section>
  <section class="panel"><h3>Why: six topics, one tag each</h3>
    <p>Every card says why with at most one tag per topic. Red tags count against the account, green tags in its favour. Tags explain the colour; they never change it.</p>
    <ul>
      <li><b>Leaving</b>: said they may stop, or the site is ending.</li>
      <li><b>Contract</b>: ends in X days, or the end date passed.</li>
      <li><b>Tone</b>: compared with the same customer's earlier calls. Worse, decision makers gone quiet, or no customer call; as usual or warmer.</li>
      <li><b>Product use</b>: daily or regular use counts in favour. Only a collapse counts against, and only for accounts meant to work in the product.</li>
      <li><b>Go-live</b>: late (more than 5 weeks from installation) or partial; on time.</li>
      <li><b>Improvements</b>: not delivering, no value seen yet, our numbers disputed, or an open request unanswered.</li>
    </ul></section>
  <section class="panel"><h3>How the colour is decided</h3>
    <p class="muted">Checked in this order. The first rule that matches sets the colour.</p>
    <ol>
      <li><span class="pill red">Red</span> One churn signal or confirmed exit, <b>or</b> two warning signs that have each lasted 3 weeks or more.</li>
      <li><span class="pill orange">Orange</span> Anything that would make it yellow, and an end date within {ORANGE_WITHIN_DAYS} days.</li>
      <li><span class="pill yellow">Yellow</span> One warning sign, a trend younger than 3 weeks, an open ask, a late go-live, or no customer call.</li>
      <li><span class="pill green">Green</span> At least one customer call, tone normal or positive, and no serious open complaint.</li>
    </ol>
    <p class="muted">Implied weights: a churn signal or confirmed exit counts 2, a warning sign that has lasted 3+ weeks counts 1, and red starts at 2.</p></section>
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
      <p class="muted">All installed accounts · customer calls, internal notes and product use, last {window} weeks · run {e(run_date)}</p></div>
    <div class="counts" aria-label="Summary">
      <div class="count r"><b>{counts["red"]}</b><span>Red</span></div>
      <div class="count o"><b>{counts["orange"]}</b><span>Orange</span></div>
      <div class="count y"><b>{counts["yellow"]}</b><span>Yellow</span></div>
      <div class="count g"><b>{counts["green"]}</b><span>Green</span></div>
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
    <section><h2><i style="background:var(--orange)"></i>Orange · wrong, and the end date is close</h2><div class="grid">{orange_html}</div></section>
    <section><h2><i style="background:var(--yellow)"></i>Yellow · watch</h2><div class="grid">{yellow_html}</div></section>
    <section><h2><i style="background:var(--green)"></i>Green · healthy</h2><div class="grid">{green_html}</div></section>
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
