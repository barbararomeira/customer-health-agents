# Decisions log

Why this is shaped the way it is. Each entry records what was chosen, what was genuinely considered,
and what the choice costs, because the cost is the part that tells you whether to copy it.

**Note on names.** Every company, person and quote in this repo is invented.

**Scope note.** These decisions come from both this clean-room template and the internal weekly run
that inspired it. Each entry says whether it is **implemented here** (code enforces it),
**guidance** (the prompt and rules ask for it; nothing checks it), or a **production lesson only**.

---

## 1. Red is a rule, not a probability

**Chose:** red means "would likely churn without escalation", decided by written rules: one explicit
churn signal, or two strong signals that have each lasted three weeks.

**Considered:** a churn probability per account, from a model fitted on past churns. Also a weighted
health score with a red threshold.

**Why:** a probability needs churned accounts to learn from, and the team this was built for had a
handful. A model fitted on five churns is a story with decimals. A weighted score has the same
problem with extra steps: the weights are guesses, and the threshold is chosen afterwards to make
the board look right. Written rules are also guesses, but they are guesses anyone can read, argue
with and change, and the changelog in [the status rules](docs/04-status-rules.md) records each change and why.

**Cost:** no calibration. "Likely" is a judgement. The rules should be backtested on every account
that leaves (see 7 and [backtesting](docs/05-backtesting.md)), and when there are enough churns to fit something, this decision should be
revisited.

**Implementation status:** implemented here. `validate.py` refuses a red the rules do not allow.

---

## 2. The board shows the reason, never a score

**Chose:** status plus reason plus evidence. No number anywhere on the board.

**Considered:** showing the score that produced the status, "for transparency".

**Why:** a score invites the wrong conversation. "Why is it 41 and not 55?" is a meeting about the
model. "The operations director said nothing is usable and the pilot ends in 46 days" is a meeting
about the account. The rules are public in [the status rules](docs/04-status-rules.md) for anyone who wants to check the reasoning;
the board is for acting.

**Implementation status:** implemented here. There is no score to show.

---

## 3. Silence is not health

**Chose:** a fourth status, **no signal**, for accounts with no customer call in the window. Green
requires at least one customer call.

**Considered:** three statuses, with "no complaints" counting as green.

**Why:** in the backtest that shaped v0.2, the account that left had no recorded customer call for
months. Under three statuses it showed green the whole way down. Internal notes said things were
fine, because the notes were written by people who also had not spoken to the customer.

**Cost:** a column of grey cards that some weeks is long. That is the point: it is the list of
accounts nobody is talking to.

**Implementation status:** implemented here. `validate.py` refuses green without
`customer_call_in_window`.

---

## 4. Attendance is who speaks, not who was invited

**Chose:** the readers list the customer-side speakers in each transcript and track them over time.

**Considered:** using the meeting's attendee list from the calendar or the recorder.

**Why:** calendar attendee lists are invitees. A plant manager who is invited to every weekly call
and has not spoken in three of them looks perfectly engaged in the attendee list, and that is
exactly the signal that matters most.

**Implementation status:** guidance. The prompt asks for it; nothing checks it.

---

## 5. A missing recording is unknown, not a no-show

**Chose:** when an expected meeting has no recording, the reader checks the internal notes. If the
notes do not explain it, it is recorded as unknown.

**Considered:** treating a missing recording as a cancelled meeting, which is the simpler rule.

**Why:** recordings go missing for boring reasons: the recorder was not invited, someone used a
different link, the meeting moved to the shop floor. Counting those as no-shows makes the
disengagement signal fire on the account owner's tooling habits, not the customer's behaviour. Three
weeks of unexplained gaps is still yellow, as its own reason, so the gap is not ignored either.

**Implementation status:** guidance, in the prompt and [the status rules](docs/04-status-rules.md).

---

## 6. Tone is compared with the same customer, never across customers

**Chose:** a customer's tone is judged against that customer's own earlier calls.

**Why:** some teams are terse and neutral in every call. Problem-solving calls sound negative by
nature. An absolute tone scale flags the same accounts every week for their culture and misses the
customer whose warm calls went curt.

**Implementation status:** guidance.

---

## 7. The nearest end date, not the renewal date

**Chose:** every "within 90 days" rule uses the **nearest** end date: contract end, renewal, pilot
or proof-of-concept end, or a named decision meeting.

**Considered:** the renewal date, which is the field the CRM has.

**Why:** v0.1 used the renewal date. Backtested on an account that had already left, it gave **zero
weeks of warning**. The customer had said in calls that the product was not giving them value, but
the renewal was months away, so "value not proven" never fired. The customer actually decided at the
end of the trial phase, a date that lived in a different system.

**The generalisation:** a rule that depends on a date is only as good as the choice of date, and the
date the customer decides on is often not the one in the contract field.

**Implementation status:** the rule is in [the status rules](docs/04-status-rules.md) and `roster.json` carries one `end_date` per
account with its label. Choosing the nearest date when building the roster is yours.

---

## 8. A relayed statement can support red, never make it alone

**Chose:** "the customer told me after the call that procurement is questioning the licence count"
is marked `relayed` and can make an account yellow. It counts toward red only next to a direct
signal.

**Why:** second-hand statements are often the earliest warning, so ignoring them is wrong. They are
also the least reliable evidence, and a red that rests on one cannot be checked by opening a call.

**Implementation status:** implemented here. Relayed reasons are left out of the red count, and a
red needs at least one quote that is not relayed.

---

## 9. A person sees a new red before anyone else

**Chose:** the run builds the board locally and stops. Publishing is a separate step a person takes
after looking at every new red.

**Considered:** publishing automatically after the run.

**Why:** a wrong red reaches the account owner as an accusation and the customer's champion as a
rumour. The cost of a day's delay is small next to that. Every override a reviewer writes, with its
reason, is also the best input the rules get.

**Implementation status:** implemented here, by omission: `run_weekly.sh` does not publish.

---

## 10. Check the output of the judgement, and block the board when it fails

**Chose:** `validate.py` runs before the board is built, and any error stops the build. The
agents' statuses must be ones the rules allow, given the reasons they wrote down; every reason needs
an evidence link; quotes are checked verbatim against local transcripts; every roster account needs a
finding.

**Considered:** trusting the coordinator's re-check, and printing warnings instead of failing.

**Why:** the judgement (is this really a churn signal?) cannot be unit-tested. The consistency
between the judgement and the rules can. A red written as "two strong signals" where one has lasted
two weeks is not a judgement call; it is a rule broken, and it should never reach a reader.
Warnings get read for a week and then ignored.

**Cost:** a run can end with no board. The script says so loudly, and the agent is told to fix the
findings, never the validator.

**Removal condition:** if the validator blocks boards that a human reviewer agrees were right,
loosen the rule that fired, in [the status rules](docs/04-status-rules.md) first, then in `rules.py`. Do not remove it because it is
inconvenient.

**Implementation status:** implemented here, with tests in `tests/test_validate.py`. The quote check
covers local files only; links to a call recorder are not checked.

---

## 11. Reasons are about the account, never about its owner

**Chose:** every reason describes what the customer said or did.

**Why:** the board is shared with the account owners. "The owner hasn't followed up" turns a risk
board into a performance review, and the people best placed to save the account stop trusting it.
An unanswered ask is still a reason, written as what the customer is waiting for.

**Implementation status:** guidance.

---

## 12. Every installed account, not only live ones

**Chose:** the roster is every account with an installation, including ones that never went live.

**Why:** the accounts most at risk are often the ones stuck between installation and go-live, and a
"live accounts" filter removes exactly those.

**Implementation status:** guidance. The roster is yours to build.
