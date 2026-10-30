# 7. Proposed for v0.3

**Not applied.** The code and the example still follow v0.2. This is the next set of changes, written
down after the first real weekly run, while the contract end dates it depends on were being corrected.

## 1. Colour means risk, and only risk

In v0.2, "the contract ends soon" is mixed into the colours through the 90-day rules. v0.3 splits
it out, so each colour has one meaning:

| Colour | Meaning |
|---|---|
| **Red** | Would likely churn without escalation: a churn signal, two lasting warning signs, **or a contract past its end date with no renewal or extension signed** |
| **Orange** *(new)* | Something is wrong **and** the contract ends within 90 days |
| **Yellow** | Something is wrong, with no near deadline |
| **Green** | Healthy, whatever the contract date |

## 2. Contract timing becomes a tag

Every account within 90 days of its end date gets a **"Renews in X days"** tag, green ones included,
and appears in a **"Renewals in the next 90 days"** strip at the top of the board, sorted by date. A
healthy account with a renewal next month still needs someone to run the renewal; it just doesn't
need an escalation.

**Which end date, by contract type:**

- **A pilot/POC or a new contract** ends at **go-live date plus committed term**. So it has **no end
  date until it goes live**: an account stuck before go-live is not "safe until the contract ends",
  it is judged on the go-live clock (section 3).
- **A renewal contract** uses the dates of the renewal contract itself.

Take the dates from wherever contracts live for you (a sales pipeline, a CRM, a contracts sheet).

## 3. Onboarding accounts are judged on the go-live clock

Installed accounts that are not fully live are judged on how long go-live is taking, not on call
volume.

- The clock starts at installation. **The target is 4 weeks.**
- **Go-live late** (a new warning sign): more than **5 weeks** from installation without a full
  go-live. More than **12 weeks** counts as a strong warning sign.
- **A partial go-live is not a go-live.** The clock keeps running until every contracted line is live.
- No customer call is fine during the first 5 weeks. After that, a late go-live with no customer
  call is flagged, because silence during a delay is when dissatisfaction builds unseen. *(This is
  the one case where v0.3 would look past "no signal".)*

## 4. Two lookbacks

- The **last 4 weeks** set this week's status (unchanged).
- The **last 12 weeks** give each customer's baseline for tone and attendance, and catch slow
  patterns, such as a sponsor or leadership gradually dropping out of meetings.

## 5. Check the dates before you trust them

The contract dates turned out to be the weakest input, and the rules lean on them hard (the
90-day window, "past its end date = red"). What checking them found, and what to do about it:

- **The CRM may not have them.** The renewal-date field was filled for very few accounts, and two
  similar fields were used inconsistently (one on older deals, the other on newer ones). Find
  where contract dates *actually* live before writing a rule that depends on them.
- **Cross-check every computed date against the calls.** Close date plus term gave several accounts
  "past their end date". For three of them that clashed with what the customer had said on a
  call. The rule in section 2 (POC/new contract = go-live + term) fixed most of the clashes.
- **A tracker formula can be wrong for one contract type.** Here, the renewal date was computed
  correctly for first contracts and wrongly for renewals. Test the formula on one contract of
  each type.
- **Fix the data before turning the rule on.** Send each account owner the list of accounts past
  their end date (renewed, extended, quote out, or really lapsed?) and only then let "past end
  date = red" run. Otherwise the first board marks renewed accounts red.
- **Look for a parallel health score.** The sales pipeline already had its own health score and
  churn-risk fields. Two health measures that disagree undermine both. Decide which one is the
  record.

## 6. What to expect from the first v0.3 board

It will look much worse than v0.2, and that is the rules working, not the accounts collapsing:

- every account past an end date with nothing signed goes red at once;
- the 5-week go-live rule flags most onboarding accounts straight away, because few go live in 4;
- every partial go-live keeps its clock running, including accounts that have been "partially live"
  for a year.

Say this to the team before publishing it.

## What would change in the code

- `STATUSES` gains `orange`; the board gets an orange section and pill.
- The roster's `end_date` drives a tag and a renewals strip instead of a status.
- `roster.json` gains `installed_on` and `fully_live_on`; a `golive_late` driver is added, strong
  after 12 weeks.
- `config.json` gains `baseline_weeks: 12`.

## Open questions

- **When does a renewal term start: at signing, or when the previous term ends?** One renewal was
  signed mid-year for 12 months, while the customer said the contract ends 12 months after the
  original go-live. The answer decides the end date of every renewal.
- **Partial go-live:** proposed that it *starts* the contract term but does *not* stop the
  onboarding clock. Not confirmed.

- Is orange a separate escalation path, or a yellow with a deadline? If the response is the same,
  it should be a tag, not a colour.
- The 4 / 5 / 12-week onboarding numbers are targets the team chose, not measured from past
  go-lives. Check them against the actual installation-to-go-live history before using them.

## Weaknesses of v0.2 that v0.3 doesn't fix yet

Raised while writing down the weights. Not solved here:

- **Yellow is too broad.** In the first real run, half the accounts were yellow. A status that
  covers half the base stops telling anyone where to look.
- **"Stuck" never escalates on its own**, however long it lasts. One strong signal is yellow
  forever. The go-live clock (section 3) is a partial answer for onboarding accounts only.
- **The line between "says there's no value" (a churn signal, 2 points) and "questions the value"
  (a warning sign, 1 point) is fragile.** It's one reader's judgement of one sentence, and it
  decides between red and yellow.
- **Numeric weights would look more precise than the inputs are.** That's why the weights stay
  implied (2 / 1 / red at 2) and never become a score on the board.
