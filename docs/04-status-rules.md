# 4. The status rules (v0.2, proposed)

Applied to every installed account, once a week. The board shows only the status and the reason,
with its evidence. The rules are not on it.

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

1. **No signal**: no customer call in the window.
2. **Red**: one explicit churn signal, **or** two strong warning signs that have each lasted 3+ weeks.
3. **Yellow**: one warning sign, a negative trend younger than 3 weeks, or an open complaint or
   unanswered ask.
4. **Green**: at least one customer call, tone normal or positive, no serious open complaint.

No signal comes first on purpose: without the customer's voice, nothing else can be judged, and
internal notes can't stand in for it.

**Implied weights.** There is no score, but red behaves as if there were one: an explicit churn
signal counts **2**, each different warning sign that has lasted 3+ weeks counts **1**, and red
starts at **2**. Open asks and warnings younger than 3 weeks count 0, so they can only reach yellow.

## Inputs and how far each can push an account

| Input | Source | Used for | Can push an account to |
|---|---|---|---|
| Customer call transcripts, last 4 weeks | Every call recorder the team uses. Full transcripts, not summaries | Main evidence: churn signals, warning signs, tone, open asks | **Red** |
| Who speaks on calls | Transcript speakers. Calendar invitees don't count | The "disengaging" warning sign | **Red**, as 1 of 2 warning signs |
| Contract, pilot/POC and decision end dates | The account tracker | "No value" and "value not proven" count only if a date is within 90 days | Gate on other signals |
| Account owners' notes | The account tracker: blockers, last update, delay reasons | Context, plus "stuck" (installed 12+ weeks, not delivering) | **Yellow**, never green alone |
| Internal calls about the account | Call recorder | Context only. Not the customer's voice | Nothing |
| Product usage | Product analytics | Not connected yet | Nothing yet |

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

### Yellow: something is off, not at escalation level

- any single strong signal, or a clear negative trend that has not yet lasted 3 weeks
- an open complaint or repeated ask that nobody has answered
- 3+ weeks of expected customer meetings with no recording and no explanation, while other calls
  in the window were recorded (with no call at all, the first check already made it no signal)
- a customer statement relayed internally (marked as relayed, with its source) that points to
  risk. **Relayed statements can support red but never make it red on their own.**

### Green: healthy

Customer engaged, tone normal or positive, no open serious complaint. **Green needs at least one
customer call in the window.** Internal notes alone are not enough.

### No signal: we cannot tell

No customer call in the window. Internal notes can give context but cannot make the account green.
Never call silence green.

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
date if there is one) and a `detail` (one short line). Yellow shows only those two lines plus folded
sources. Red shows the headline and up to 3 reasons with quotes. No paragraphs on the board.

## The math

Every number in the rules, and where it lives in the code. They are choices, not measured
thresholds: they were set by judgement and checked against one backtest
([05-backtesting.md](05-backtesting.md)). Change them in one place and the validator follows.

| Number | Meaning | Where |
|---|---|---|
| **4 weeks** | The window: the last 4 full weeks up to the run date | `window_weeks` in `config.json` |
| **Order** | No signal → red → yellow → green; the first match wins. Code enforces the first step: no customer call means no signal | `validate_account` in `healthcheck/validate.py` |
| **2 / 1 / 2 points** | Implied weights: churn signal 2, each different lasting warning sign 1, red at 2 | `CHURN_SIGNAL_POINTS`, `LASTING_WARNING_POINTS`, `RED_AT_POINTS` in `healthcheck/rules.py` |
| **3 weeks** | A strong signal must be present in 3 of the 4 weeks before it counts toward red | `MIN_WEEKS_FOR_RED` in `healthcheck/rules.py` |
| **90 days** | "No value" or "value not proven" only escalates when the nearest end date is this close | applied by the agent (the date comparison needs the call's context) |
| **12 weeks** | Installed this long and not really delivering = "stuck" | applied by the agent |
| **15 words** | Headline length. Longer is a warning, not an error | `HEADLINE_WORDS` in `healthcheck/validate.py` |
| **2 accounts** | A reason on this many red/yellow accounts shows under *Recurring reasons* | `recurring_reasons` in `healthcheck/board.py` |
| **12 / 52 weeks** | The trend tab shows 12 weekly columns; the summary column counts the last 52 runs | `render` in `healthcheck/board.py` |

The red rule as code (`red_points` in `healthcheck/validate.py`):

```
direct  = reasons that are not relayed
points  = 2  if any direct reason has driver = churn_signal
        + 1  for each DISTINCT driver among direct reasons where
               driver ∈ {disengagement, tone, value_not_proven, trust_broken, stuck}
               and weeks_present ≥ 3
red is allowed if points ≥ 2
            and at least one direct reason carries a verbatim quote
```

Any status other than no signal needs `customer_call_in_window` to be true. Days to the end date are
`end_date − run_date`, shown only when not negative.

## Changelog

- **v0.2, later the same week.** Wrote down the order of the checks (no signal first) and the
  implied weights, and listed every input with how far it can push an account. No status changed.
  A v0.3 is proposed in [07-proposed-v0.3.md](07-proposed-v0.3.md).

- **v0.2.** Backtest on an account that had already left. v0.1 gave **zero weeks of warning**: no
  customer call had been recorded for months, "value not proven" was tied to a renewal that was
  still far away (the customer actually decided at the end of the trial phase), and "stuck" trusted
  the go-live field. Changes: nearest end date includes pilot/POC end and decision meetings; "no
  value" plus an end date within 90 days is red; "stuck" is judged on real delivery; unrecorded
  meetings and relayed statements make yellow; green needs a customer call.
- **v0.1.** First version.
