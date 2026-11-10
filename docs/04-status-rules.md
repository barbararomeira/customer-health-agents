# 4. The status rules (v0.6)

Applied to every installed account, once a week. The board shows only the colour and why (six
topic tags, plus the reason and its evidence). The rules are not on it.

*v0.2 was the first version run weekly. v0.3 to v0.6 came from that use: an orange colour, product
use, team-chat hard facts, and a simpler board. The [changelog](#changelog) says what changed and why.*

Code checks what it can: [`healthcheck/validate.py`](../healthcheck/validate.py) refuses a status
the rules do not allow, given the reasons the agent wrote down. The judgement itself (is this tone
really worse? is this a churn signal?) stays with the agent and with the person who reviews a new red.
The numbers are under [The math](#the-math) at the end.

## Scope

Every account that has been **installed**: an installation date, a go-live date, or an
implementation record with an actual installation date. Not only accounts marked live, because the
accounts most at risk are often the ones that never got there. Accounts that have left are kept out
of the board and used for backtests.

## Window

The last 4 full weeks up to the run date (`window_weeks` in the config). "This week" is the most
recent 7 days.

## How the status is decided

The checks run in this order. **The first one that matches sets the status.**

1. **Red**: one explicit churn signal or a confirmed exit, **or** two strong warning signs that have
   each lasted 3+ weeks.
2. **Orange**: anything that would make it yellow, **and** the nearest end date is within 90 days
   (or already passed).
3. **Yellow**: one warning sign, a negative trend younger than 3 weeks, an open complaint or
   unanswered ask, a late go-live, or **no customer call in the window**.
4. **Green**: at least one customer call, tone normal or positive, no serious open complaint.

Silence is never green: without the customer's voice, nothing else can be judged, and internal notes
can't stand in for it. (Up to v0.4 this was a fifth status, "no signal". It became a yellow reason
because the board's owner wanted four colours and why, nothing else.)

**Implied weights.** There is no score, but red behaves as if there were one: an explicit churn
signal or a confirmed exit counts **2**, each different warning sign that has lasted 3+ weeks counts
**1**, and red starts at **2**. Open asks and warnings younger than 3 weeks count 0, so they can only reach yellow.

## Inputs and how far each can push an account

| Input | What the source must give you | Used for | Can push an account to |
|---|---|---|---|
| Customer call transcripts, last 4 weeks | Full transcripts (not summaries) with dates and speaker names | Main evidence: churn signals, warning signs, tone, open asks | **Red** |
| Who speaks on calls | Speaker labels in the transcript. Calendar invitees don't count | The "disengaging" warning sign | **Red**, as 1 of 2 warning signs |
| Contract, pilot/POC and decision end dates | One nearest end date per account, and what kind of date it is | "No value" and "value not proven" count only if a date is within 90 days | Gate on other signals |
| Account owners' notes | Dated notes per account: blockers, last update, delay reasons | Context, plus "stuck" (installed 12+ weeks, not delivering) | **Yellow**, never green alone |
| Team chat channels per customer (v0.5) | Messages from the last 4 weeks; never direct messages | Context like account notes; hard facts (equipment removed, contract cancelled) mark a confirmed exit | **Red**, only for a confirmed exit |
| Internal calls about the account | Same as customer calls, marked as internal | Context only. Not the customer's voice | Nothing |
| Product usage | Per account: user-days (people who open and click) per week, and whether the account is meant to use the product | Regular use = engagement; a collapse = one warning sign ([v0.4](08-product-usage.md)) | **Red**, as 1 of 2 warning signs (collapse only) |

### Choosing your sources

The rules don't care where the data comes from. Use whatever your team already has; the run only
reads three things, all from files:

| The run reads | Fill it from, for example |
|---|---|
| `transcripts/`: one file per call | Any call recorder or meeting-notes tool that exports full transcripts with speaker names, or transcripts pasted in by hand |
| `notes/`: one file per account | A CRM, a project tracker, a shared doc, or a spreadsheet export of the account owners' updates |
| `roster.json`: every installed account | A CRM, a contracts sheet or a sales pipeline: owner, nearest end date, and its label (contract end, renewal, pilot end, decision meeting) |

Where the files live is set in `config.json` → `sources`. If you have more than one place for the
same input (two call recorders, say), merge them into the same folder. Whatever you choose, the
minimum bar is the middle column of the table above: a source that only gives summaries, or no
speaker names, can't support the tone and attendance rules.

## Statuses

### Red: would likely churn without escalation

Red must be rare. When in doubt, choose yellow. Red needs **either**:

1. **One explicit churn signal** from the customer in the window:
   - they say they will not renew, are reconsidering, pausing, or cutting scope or budget for you
   - they mention evaluating a competitor, or building it in-house as a replacement
   - the champion or sponsor left or was moved, and nobody on their side has taken over
   - a formal escalation to their management about you, or a request to stop or remove the product
   - they say the product gives them no value ("nothing usable", "duplicates what we have"),
     **and** the nearest end date is within 90 days

   **or**

2. **At least two strong signals, each present for 3 or more weeks of the window:**
   - **Disengagement**: their decision makers stopped speaking in calls, or recurring meetings were
     cancelled or no-showed (confirmed by notes), or they stopped replying
   - **Tone** well below that customer's own baseline: sustained frustration, distrust, curt or
     deferring answers
   - **Value not proven**: they question what they get, or their KPIs show no progress, and the
     nearest end date is within 90 days
   - **Trust broken**: they repeatedly dispute your numbers or call the data unusable, with no fix
     in sight
   - **Stuck**: installed 12+ weeks and not actually delivering (judge by real delivery, not by a
     go-live date field), with a blocker on your side or no plan

**The nearest end date** is whichever comes first: contract end, renewal, pilot or proof-of-concept
end, or a named decision meeting. Not only the renewal date.

A **confirmed exit** is a hard fact that a site is ending, such as our equipment being removed. It
counts in full even when a colleague wrote it down in a team channel, and the card says whether the
company continues at other sites.

### Orange: something is wrong, and the end date is close

Whatever would make the account yellow, when the nearest end date is within 90 days or has passed
without a signed renewal. Same reasons as yellow; the deadline is what changes who acts and how fast.

### Yellow: something is off, not at escalation level

- any single strong signal, or a clear negative trend that has not yet lasted 3 weeks
- an open complaint or repeated ask that nobody has answered
- 3+ weeks of expected customer meetings with no recording and no explanation, while other calls
  in the window were recorded
- no customer call at all in the window (shown as "Tone: no customer call in 4 weeks")
- a go-live more than 5 weeks after installation, or a partial go-live
- a customer statement relayed internally (marked as relayed, with its source) that points to
  risk. **Relayed statements can support red but never make it red on their own.**

### Green: healthy

Customer engaged, tone normal or positive, no open serious complaint. **Green needs at least one
customer call in the window.** Internal notes alone are not enough.

## How to read signals

- **Tone is relative to that customer's own earlier calls**, never absolute. Problem-solving calls
  sound negative and that is normal. A team whose normal register is neutral and terse is not
  being negative.
- Tone markers: the customer's share of talking drops, shorter answers, fewer questions, deferring
  language ("we'll see", "after the budget review", "not a priority now"), frustration words, a
  sudden shift to formal tone, sarcasm.
- **Attendance is who speaks in the transcript.** Calendar invites list who was asked, not who came.
  Track the customer-side speakers over time, especially managers and decision makers.
- **A missing recording is unknown, not a no-show.** If an expected recurring meeting has no
  recording, look in the internal notes for cancelled, moved or no-show. If the notes do not say,
  record it as unknown.

## Hard rules

- Every reason cites evidence: a call link (with timestamp where possible) or a note link. No
  evidence, no reason. *(Checked by the validator.)*
- Quotes are verbatim from the transcript. Never invent or paraphrase into a quote. *(Checked by the
  validator when the transcript is a local file.)*
- Deliberate product design that the customer agreed to is never a risk. List it in
  `config.json` → `never_a_risk` so the agents know.
- Customer-side delays (holidays, legal, their infrastructure) are context, not your failure, but
  they still count for "stuck" if they stall the account.
- Internal calls can explain context but are **not customer signals**. Use them only to resolve
  facts ("renewal discussion is ongoing").
- Write reasons about the **account**, never about the person who owns it.
- Do not over-claim. If a signal is weak or ambiguous, say so or leave it out.

## Board wording

Each account gets a `headline` (one line, 15 words or fewer, the reason in plain words, with the
date if there is one) and a `detail` (one short line). Orange, yellow and green cards show the tags,
those two lines and folded sources. Red shows the tags, the headline and up to 3 reasons with
quotes. No paragraphs on the board.

**Why, as six topics.** Every card says why with at most one tag per topic, written "Topic: value".
Red tags count against the account, green tags in its favour. Red cards show only what counts
against; green cards only what counts in favour. Tags explain the colour; they never change it.

| Topic | Against | In favour |
|---|---|---|
| **Leaving** | said they may stop · site is ending | n/a |
| **Contract** | ends in X days (within 90) · end passed | n/a |
| **Tone** | worse than usual · decision makers gone quiet · no customer call in 4 weeks | as usual · warmer than usual |
| **Product use** | stopped · not logging in (only for accounts meant to use it) · halved | daily · regular |
| **Go-live** | late (more than 5 weeks) · partial | on time |
| **Improvements** | not delivering · no value seen yet · our numbers disputed · open request unanswered | n/a |

A tag that says nothing ("customer call in the last 4 weeks", with no read on how the call went) is
left out. A green card with no tags means nothing counts against it. Wording and mapping live in
`DRIVER_TAG` and `TOPICS` (`healthcheck/rules.py`) and `why_tags` (`healthcheck/board.py`).

## The math

Every number in the rules, and where it lives in the code. They are choices, not measured
thresholds: they were set by judgement and checked against one backtest
([05-backtesting.md](05-backtesting.md)). Change them in one place and the validator follows.

| Number | Meaning | Where |
|---|---|---|
| **4 weeks** | The window: the last 4 full weeks up to the run date | `window_weeks` in `config.json` |
| **Order** | Red → orange → yellow → green; the first match wins. Code enforces that no customer call is never green, and that orange has an end date within 90 days | `validate_account` in `healthcheck/validate.py` |
| **2 / 1 / 2 points** | Implied weights: churn signal or confirmed exit 2, each different lasting warning sign 1, red at 2 | `CHURN_SIGNAL_POINTS`, `LASTING_WARNING_POINTS`, `RED_AT_POINTS` in `healthcheck/rules.py` |
| **3 weeks** | A strong signal must be present in 3 of the 4 weeks before it counts toward red | `MIN_WEEKS_FOR_RED` in `healthcheck/rules.py` |
| **90 days** | Orange, the Contract tag, and when "no value" escalates | `ORANGE_WITHIN_DAYS` in `healthcheck/rules.py` |
| **5 weeks** | Installed this long without a full go-live = "Go-live: late" (yellow) | applied by the agent |
| **12 weeks** | Installed this long and not really delivering = "stuck" | applied by the agent |
| **15 words** | Headline length. Longer is a warning, not an error | `HEADLINE_WORDS` in `healthcheck/validate.py` |
| **12 / 52 weeks** | The trend tab shows 12 weekly columns; the summary column counts the last 52 runs | `render` in `healthcheck/board.py` |

The red rule as code (`red_points` in `healthcheck/validate.py`):

```
direct  = reasons that are not relayed
points  = 2  if any direct reason has driver = churn_signal, or any reason has driver = leaving
        + 1  for each DISTINCT driver among direct reasons where
               driver ∈ {disengagement, tone, value_not_proven, trust_broken, stuck, usage_collapse}
               and weeks_present ≥ 3
red is allowed if points ≥ 2
            and at least one direct reason carries a verbatim quote
```

Green needs `customer_call_in_window` to be true. Days to the end date are `end_date − run_date`;
orange needs them ≤ 90 (negative = passed).

## Changelog

- **v0.6, in use.** The why tags use six fixed topics, at most one tag per topic, written
  "Topic: value": Leaving, Contract, Tone, Product use, Go-live and Improvements. Display only, no
  status change. A late go-live is not split by whose fault it was, because the cause can't be
  captured reliably; the card's headline gives the context instead.
- **v0.5, in use.** Simpler board: four colours only (no "no signal" colour; no customer call in 4
  weeks is a yellow reason), no renewals strip, and every card shows **why** in plain-word tags
  (against / in favour). Team chat channels per customer become a source: messages count like account
  owners' notes, but **hard facts** (equipment removed, contract cancelled, work stopped) count in
  full, and a confirmed exit is red with a note on whether the company continues at other sites.
  Found because a site's exit decision arrived by email and only showed up in a team channel.
- **v0.4, in use.** Product usage enters the status: regular use counts as engagement, and only
  a collapse (regular use, then almost nothing for 3+ weeks) counts against an account meant to
  use the product. Report-first accounts are never penalised for not logging in. See
  [08-product-usage.md](08-product-usage.md).
- **v0.3, in use.** Orange (something wrong **and** the end date within 90 days), contract timing
  as a tag instead of a status, a go-live clock for onboarding accounts, and tone compared with a
  12-week baseline. One part was **not** adopted: "contract past its end date with nothing signed =
  red". Past end dates turned out to be stale data more often than real exits, so it is a tag
  ("Contract: end passed") until someone confirms it. The proposal is in
  [07-proposed-v0.3.md](07-proposed-v0.3.md).
- **v0.2, later the same week.** Wrote down the order of the checks (no signal first) and the
  implied weights, and listed every input with how far it can push an account. No status changed.

- **v0.2.** Backtest on an account that had already left. v0.1 gave **zero weeks of warning**: no
  customer call had been recorded for months, "value not proven" was tied to a renewal that was
  still far away (the customer actually decided at the end of the trial phase), and "stuck" trusted
  the go-live field. Changes: nearest end date includes pilot/POC end and decision meetings; "no
  value" plus an end date within 90 days is red; "stuck" is judged on real delivery; unrecorded
  meetings and relayed statements make yellow; green needs a customer call.
- **v0.1.** First version.
